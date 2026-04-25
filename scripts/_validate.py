#!/usr/bin/env python3
"""
Validate the agents-system-setup repository.

Checks (per the CONTRIBUTING.md contract):
  1. JSON parses cleanly + minimum required fields per manifest
  2. Version consistency across the four version-bearing manifests
  3. YAML frontmatter parses for every SKILL.md and *.agent.md
  4. Frontmatter `name` matches filename basename
  5. UTF-8-without-BOM encoding for every text file under git
  6. Internal markdown link resolution (./relative paths only)
  7. Codex TOML subagents parse and include required fields
  8. Replication ledger/logs do not live inside agents/ directories
 9. Governance baseline references and templates are present
10. Context optimization policy and generated-template markers are present
 11. Local-vs-git-tracked artifact policy is present

Exits non-zero on any failure. Designed to be invoked from CI on
Linux / macOS / Windows runners with only Python 3.10+ available
(no pip install required: jsonschema is OPTIONAL — when absent we
fall back to ad-hoc field checks).

Usage:
  python3 scripts/_validate.py
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Force UTF-8 on stdout/stderr so Windows cp1252 doesn't reject non-ASCII output.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# ---------- 1 & 2: manifest validation + version sync ----------

VERSIONED_MANIFESTS = [
    REPO / "plugin.json",
    REPO / ".claude-plugin" / "plugin.json",
    REPO / ".codex-plugin" / "plugin.json",
]
MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"

REQUIRED = {
    "plugin.json": ["name", "version", "description"],
    ".claude-plugin/plugin.json": ["name", "version", "description"],
    ".codex-plugin/plugin.json": ["name", "version", "description"],
    ".agents/plugins/marketplace.json": ["name", "plugins"],
}


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        err(f"missing manifest: {path.relative_to(REPO).as_posix()}")
    except json.JSONDecodeError as e:
        err(f"invalid JSON in {path.relative_to(REPO).as_posix()}: {e}")
    return None


def check_manifests() -> None:
    versions: dict[str, str] = {}
    for path in VERSIONED_MANIFESTS:
        rel = path.relative_to(REPO).as_posix()
        data = load_json(path)
        if data is None:
            continue
        for key in REQUIRED[rel]:
            if key not in data:
                err(f"{rel}: missing required field `{key}`")
        if "version" in data:
            v = data["version"]
            if not re.fullmatch(r"\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?", str(v)):
                err(f"{rel}: version `{v}` is not semver")
            versions[rel] = str(v)
        if "name" in data and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(data["name"])):
            err(f"{rel}: name `{data['name']}` must be lowercase kebab-case")

    # marketplace
    rel = MARKETPLACE.relative_to(REPO).as_posix()
    mdata = load_json(MARKETPLACE)
    if mdata is not None:
        for key in REQUIRED[rel]:
            if key not in mdata:
                err(f"{rel}: missing required field `{key}`")
        plugins = mdata.get("plugins", [])
        if not isinstance(plugins, list) or not plugins:
            err(f"{rel}: plugins[] must be a non-empty array")
        for i, p in enumerate(plugins):
            src = p.get("source", {})
            sp = src.get("path")
            if sp is None:
                err(f"{rel}: plugins[{i}].source.path missing")
            else:
                # Codex CLI rule: must start with `./`, must not be bare `./`,
                # must not contain `..`, and must resolve to a dir containing
                # .codex-plugin/plugin.json or .claude-plugin/plugin.json.
                # Source: openai/codex codex-rs/core-plugins/src/marketplace.rs
                # (resolve_local_plugin_source_path) and utils/plugins/src/
                # plugin_namespace.rs (DISCOVERABLE_PLUGIN_MANIFEST_PATHS).
                if not sp.startswith("./"):
                    err(f"{rel}: plugins[{i}].source.path `{sp}` must start with `./`")
                elif sp.rstrip("/") in ("", "."):
                    err(f"{rel}: plugins[{i}].source.path `{sp}` must not be bare `./` (Codex rejects it)")
                elif ".." in sp.split("/"):
                    err(f"{rel}: plugins[{i}].source.path `{sp}` must not contain `..`")
                else:
                    plugin_root = (REPO / sp[2:]).resolve()
                    if not plugin_root.is_dir():
                        err(f"{rel}: plugins[{i}].source.path `{sp}` does not exist on disk")
                    elif not (
                        (plugin_root / ".codex-plugin" / "plugin.json").is_file()
                        or (plugin_root / ".claude-plugin" / "plugin.json").is_file()
                    ):
                        err(f"{rel}: plugins[{i}].source.path `{sp}` is missing .codex-plugin/plugin.json or .claude-plugin/plugin.json — Codex/Claude marketplace will skip it")

    # version sync
    unique = set(versions.values())
    if len(unique) > 1:
        details = ", ".join(f"{k}={v}" for k, v in versions.items())
        err(f"version mismatch across manifests: {details}")


# ---------- 3 & 4: agent/skill frontmatter ----------

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, Any] | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    body = m.group(1)
    try:
        import yaml  # type: ignore

        return yaml.safe_load(body) or {}
    except ImportError:
        # Minimal fallback: extract `key: value` pairs at top level only.
        out: dict[str, Any] = {}
        for line in body.splitlines():
            if ":" in line and not line.startswith(" "):
                k, _, v = line.partition(":")
                out[k.strip()] = v.strip().strip("'\"")
        return out
    except Exception as e:
        err(f"frontmatter parse error: {e}")
        return None


def check_frontmatter_files() -> None:
    targets: list[tuple[Path, str]] = []
    for p in REPO.rglob("SKILL.md"):
        if ".git" in p.parts:
            continue
        targets.append((p, "skill"))
    for p in REPO.rglob("*.agent.md"):
        if ".git" in p.parts:
            continue
        targets.append((p, "agent"))

    for path, kind in targets:
        rel = path.relative_to(REPO)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            err(f"{rel}: not valid UTF-8")
            continue

        fm = parse_frontmatter(text)
        if fm is None:
            err(f"{rel}: missing or unparseable YAML frontmatter")
            continue

        name = fm.get("name")
        desc = fm.get("description")
        if not desc:
            err(f"{rel}: frontmatter missing `description`")

        # Filename-vs-name check
        if kind == "skill":
            expected = path.parent.name
        else:  # agent: <name>.agent.md
            expected = path.name.removesuffix(".agent.md")
        if name and name != expected:
            err(f"{rel}: frontmatter name `{name}` does not match basename `{expected}`")
        if not name:
            err(f"{rel}: frontmatter missing `name`")


# ---------- 5: encoding ----------

def check_encoding() -> None:
    text_exts = {".md", ".json", ".yaml", ".yml", ".sh", ".ps1", ".template", ".snippet.md"}
    for path in REPO.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        if path.suffix not in text_exts and path.name not in {".gitignore", ".gitattributes", ".editorconfig", ".markdownlint.yaml"}:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if data.startswith(b"\xef\xbb\xbf"):
            err(f"{path.relative_to(REPO)}: UTF-8 BOM not allowed")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            err(f"{path.relative_to(REPO)}: not valid UTF-8")


# ---------- 6: internal markdown links ----------

LINK_RE = re.compile(r"\[[^\]]+\]\((\.[^)#?]+)(?:#[^)]*)?\)")


def check_internal_links() -> None:
    for path in REPO.rglob("*.md"):
        if ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for m in LINK_RE.finditer(text):
            target = (path.parent / m.group(1)).resolve()
            if not target.exists():
                err(f"{path.relative_to(REPO)}: broken link → {m.group(1)}")


# ---------- 7: Codex TOML subagents (.codex/agents/*.toml) ----------

def check_codex_toml_agents() -> None:
    try:
        import tomllib  # py 3.11+
    except ImportError:
        warn("tomllib unavailable (Python <3.11) — skipping .codex/agents/*.toml validation")
        return
    # Validate any .codex/agents/ tree under the repo (project-scope) but skip
    # samples inside skill assets/templates.
    for agents_dir in REPO.rglob(".codex/agents"):
        if not agents_dir.is_dir() or ".git" in agents_dir.parts:
            continue
        for toml_path in agents_dir.glob("*.toml"):
            rel = toml_path.relative_to(REPO)
            try:
                data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
            except Exception as e:
                err(f"{rel}: invalid TOML: {e}")
                continue
            for key in ("name", "description", "developer_instructions"):
                if not data.get(key):
                    err(f"{rel}: missing required Codex subagent field `{key}`")
            name = data.get("name")
            if isinstance(name, str) and name != toml_path.stem:
                warn(f"{rel}: TOML `name` ({name}) differs from filename stem ({toml_path.stem}) — name is the source of truth, but matching filenames is the recommended convention")
            effort = data.get("model_reasoning_effort")
            if effort and effort not in ("low", "medium", "high"):
                err(f"{rel}: model_reasoning_effort must be low|medium|high (got `{effort}`)")
            sandbox = data.get("sandbox_mode")
            if sandbox and sandbox not in ("read-only", "workspace-write"):
                warn(f"{rel}: sandbox_mode `{sandbox}` is not one of the documented values (read-only|workspace-write)")


# ---------- 8: replication ledger location ----------

LEDGER_FORBIDDEN_DIRS = (
    ".claude/agents",
    ".codex/agents",
    ".opencode/agents",
    ".github/agents",
    ".config/opencode/agents",
)


def check_replication_ledger() -> None:
    """The replication ledger and any operational log MUST NOT live inside an
    agents/ directory or use a `.md` extension — runtime loaders walk those
    trees by extension and will treat the file as a malformed agent.
    """
    patterns = ("*replication*", "*replicat*.log", "*replicat*.md", "*replicat*.jsonl")
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        name_lower = path.name.lower()
        if "replicat" not in name_lower:
            continue
        rel = path.relative_to(REPO).as_posix()
        for forbidden in LEDGER_FORBIDDEN_DIRS:
            if forbidden in rel:
                err(f"{rel}: replication ledger/log must not live inside `{forbidden}` — runtime will misread it as an agent. Move to `.agents-system-setup/replication.jsonl`.")
        if path.suffix == ".md" and "/agents/" in f"/{rel}":
            err(f"{rel}: replication artifact with `.md` extension inside an agents/ tree will be parsed as a malformed agent.")


# ---------- 9: governance baseline ----------

SKILL_ROOT = REPO / "plugins" / "agents-system-setup" / "skills" / "agents-system-setup"


def require_contains(path: Path, needles: tuple[str, ...]) -> None:
    rel = path.relative_to(REPO).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        err(f"{rel}: required governance file is missing")
        return
    except UnicodeDecodeError:
        err(f"{rel}: not valid UTF-8")
        return
    for needle in needles:
        if needle not in text:
            err(f"{rel}: missing required governance marker `{needle}`")


def check_governance_baseline() -> None:
    """The skill must keep security, audit, architecture, and design-pattern
    governance as first-class generated outputs, not optional wrap-up notes.
    """
    required_files = [
        SKILL_ROOT / "references" / "security-audit-architecture.md",
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        SKILL_ROOT / "assets" / "orchestrator.agent.md.template",
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
    ]
    for path in required_files:
        if not path.is_file():
            err(f"{path.relative_to(REPO).as_posix()}: required governance file is missing")

    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Phase 1.8 — Security, Audit, Architecture Intake",
            "Security & Audit Matrix",
            "Threat Model",
            "Architecture & Design Pattern",
            "Quality Gates",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "security-audit-architecture.md",
        (
            "OWASP GenAI",
            "NIST SSDF",
            "MCP Security Best Practices",
            "SLSA",
            "C4 Model",
            "Quality Gates",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Security & Audit Matrix",
            "## Threat Model",
            "## Architecture & Design Pattern Decisions",
            "## ADR Index",
            "## Quality Gates",
            "{{SECURITY_AUDIT_MATRIX_ROWS}}",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.agent.md.template",
        (
            "Security & Audit Matrix",
            "Threat Model",
            "Architecture & Design Pattern Decisions",
            "security/audit evidence",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        (
            "## Security & Audit Boundaries",
            "## Architecture & Design Expectations",
            "{{AUDIT_EVIDENCE}}",
            "{{PATTERNS_TO_PRESERVE}}",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "Security & Audit Boundaries",
            "Architecture & Design Expectations",
            "{{AUDIT_EVIDENCE}}",
            "{{PATTERNS_TO_PRESERVE}}",
        ),
    )


# ---------- 10: context optimization ----------

def check_context_optimization() -> None:
    """The skill must stay compact-by-default and preserve progressive loading
    markers in generated templates.
    """
    context_ref = SKILL_ROOT / "references" / "context-optimization.md"
    if not context_ref.is_file():
        err(f"{context_ref.relative_to(REPO).as_posix()}: required context optimization reference is missing")

    require_contains(
        SKILL_ROOT / "references" / "context-optimization.md",
        (
            "Balanced",
            "Compact",
            "Full",
            "Context budgets",
            "Concise delegation packets",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Phase 1.9 — Output Profile & Context Budget",
            "Context Loading Policy",
            "Context profile",
            "Context split",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Read First",
            "## Context Loading Policy",
            "{{CONTEXT_PROFILE}}",
            "{{DETAIL_REFERENCES}}",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.agent.md.template",
        (
            "## Context Load Order",
            "## Delegation Packet",
            "concise delegation packet",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        (
            "## Context Load Order",
            "Keep the response concise",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "Context Load Order",
            "Outcome first",
        ),
    )

    skill_path = SKILL_ROOT / "SKILL.md"
    try:
        line_count = len(skill_path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return
    if line_count > 500:
        err(f"{skill_path.relative_to(REPO).as_posix()}: SKILL.md exceeds hard 500-line limit ({line_count})")
    elif line_count > 300:
        warn(f"{skill_path.relative_to(REPO).as_posix()}: SKILL.md is {line_count} lines; target is about 250. Consider moving more detail to references.")


# ---------- 11: local-vs-git-tracked artifact policy ----------

def check_local_tracking_policy() -> None:
    require_contains(
        SKILL_ROOT / "references" / "local-tracking.md",
        (
            "project-tracked",
            "project-local",
            "personal-global",
            ".git/info/exclude",
            "git check-ignore",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Phase 1.6 — Artifact Scope & Tracking",
            "artifact_tracking",
            ".git/info/exclude",
            "git check-ignore",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "interview.md",
        (
            "Project files, git-tracked",
            "Project files, local-only / untracked",
            "Personal/global outside this repo",
            "artifact_tracking",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "{{ARTIFACT_TRACKING}}",
            "{{ARTIFACT_TRACKING_NOTES}}",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Artifact tracking",
            "Local exclude",
        ),
    )


# ---------- main ----------

def main() -> int:
    print(f"Validating {REPO} …")
    check_manifests()
    check_frontmatter_files()
    check_encoding()
    check_internal_links()
    check_codex_toml_agents()
    check_replication_ledger()
    check_governance_baseline()
    check_context_optimization()
    check_local_tracking_policy()

    if WARNINGS:
        print("\nWARNINGS:")
        for w in WARNINGS:
            print(f"  [WARN] {w}")
    if ERRORS:
        print("\nERRORS:")
        for e in ERRORS:
            print(f"  [FAIL] {e}")
        print(f"\n{len(ERRORS)} error(s).")
        return 1
    print(f"\n[OK] All checks passed ({len(WARNINGS)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
