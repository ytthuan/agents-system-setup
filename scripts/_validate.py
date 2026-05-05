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
  8. Gemini Markdown subagents parse for local, remote, and extension scopes
  9. OpenCode Markdown agents use the Markdown/frontmatter schema
 10. Claude plugin-shipped agents avoid project-only fields
 11. Replication ledger/logs do not live inside agents/ directories
 12. Governance baseline references and templates are present
 13. Context optimization policy and generated-template markers are present
 14. Local-vs-git-tracked artifact policy is present
 15. Plan handoff policy is present and platform-specific
 16. Codex shared artifacts are documented as CLI + App compatible without
      overclaiming Codex App plugin installation
  17. Runtime update audit tracks supported-runtime drift for five runtimes
  18. Runtime invocation guidance distinguishes skills, commands, plugins,
      and provider-specific `/`, `$`, and `@` syntax

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
SUPPORTED_RUNTIMES = ("copilot-cli", "claude-code", "opencode", "codex-cli", "gemini-cli")
YAML_FALLBACK_WARNED = False
YAML_FALLBACK_IN_USE = False


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# ---------- 1 & 2: manifest validation + version sync ----------

VERSIONED_MANIFESTS = [
    REPO / "plugin.json",
    REPO / ".claude-plugin" / "plugin.json",
    REPO / ".codex-plugin" / "plugin.json",
    REPO / "plugins" / "agents-system-setup" / ".claude-plugin" / "plugin.json",
    REPO / "plugins" / "agents-system-setup" / ".codex-plugin" / "plugin.json",
]
MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"

REQUIRED = {
    "plugin.json": ["name", "version", "description"],
    ".claude-plugin/plugin.json": ["name", "version", "description"],
    ".codex-plugin/plugin.json": ["name", "version", "description"],
    "plugins/agents-system-setup/.claude-plugin/plugin.json": ["name", "version", "description"],
    "plugins/agents-system-setup/.codex-plugin/plugin.json": ["name", "version", "description"],
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
        if rel == "plugin.json":
            compat = data.get("compatibility")
            if not isinstance(compat, dict):
                err(f"{rel}: compatibility must be a mapping")
            else:
                for runtime in SUPPORTED_RUNTIMES:
                    value = compat.get(runtime)
                    if not isinstance(value, str) or not value:
                        err(f"{rel}: compatibility must include `{runtime}` as a version string")

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
            if not isinstance(p, dict):
                err(f"{rel}: plugins[{i}] must be an object")
                continue
            src = p.get("source")
            source_kind = None
            sp = None
            if isinstance(src, str):
                source_kind = "local" if src.startswith("./") else "remote"
                sp = src if source_kind == "local" else None
            elif isinstance(src, dict):
                source_kind = src.get("source")
                sp = src.get("path")
            else:
                err(f"{rel}: plugins[{i}].source must be a string or object")
                continue

            if sp is not None or source_kind == "local":
                if not isinstance(sp, str) or not sp:
                    err(f"{rel}: plugins[{i}].source.path missing")
                    continue
                # Codex CLI local rule: path must start with `./`, must not be
                # bare `./`, must not contain `..`, and must resolve to a dir
                # containing .codex-plugin/plugin.json or .claude-plugin/plugin.json.
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

    cdata = load_json(CLAUDE_MARKETPLACE)
    if cdata is not None:
        rel = CLAUDE_MARKETPLACE.relative_to(REPO).as_posix()
        metadata_version = cdata.get("metadata", {}).get("version")
        if metadata_version:
            versions[f"{rel}:metadata.version"] = str(metadata_version)
        plugins = cdata.get("plugins", [])
        if not isinstance(plugins, list) or not plugins:
            err(f"{rel}: plugins[] must be a non-empty array")
        else:
            for i, plugin in enumerate(plugins):
                if not isinstance(plugin, dict):
                    err(f"{rel}: plugins[{i}] must be an object")
                    continue
                plugin_version = plugin.get("version")
                if plugin_version:
                    versions[f"{rel}:plugins[{i}].version"] = str(plugin_version)

    # version sync
    unique = set(versions.values())
    if len(unique) > 1:
        details = ", ".join(f"{k}={v}" for k, v in versions.items())
        err(f"version mismatch across manifests: {details}")


def check_schema_files() -> None:
    for path in sorted((REPO / "schemas").glob("*.json")):
        rel = path.relative_to(REPO).as_posix()
        data = load_json(path)
        if data is None:
            continue
        for key in ("$schema", "$id", "title", "type"):
            if key not in data:
                err(f"{rel}: schema missing required field `{key}`")


# ---------- 3 & 4: agent/skill frontmatter ----------

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
CODEX_NICKNAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 _-]{0,31}$")
READ_ONLY_IDENTITY_RE = re.compile(
    r"(^|[-_])(reviewer|review|auditor|audit|security|architect|architecture|governance)($|[-_])",
    re.IGNORECASE,
)


def is_codex_read_only_identity(*values: Any) -> bool:
    """Return True for unambiguous read-only identity surfaces.

    Scope this to identity surfaces (name and filename stem), not descriptions,
    so descriptive text does not create read-only false positives. Empty Owned
    paths are also read-only at generation time, but this validator cannot infer
    Owned paths from TOML alone.
    """
    for value in values:
        if not isinstance(value, str):
            continue
        normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
        if READ_ONLY_IDENTITY_RE.search(normalized):
            return True
    return False


def parse_scalar(value: str) -> Any:
    raw = value.strip()
    if not raw:
        return ""
    if raw in {"|", ">"}:
        return raw
    if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
        return raw[1:-1]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none", "~"}:
        return None
    try:
        return int(raw)
    except ValueError:
        try:
            return float(raw)
        except ValueError:
            return raw


def parse_simple_yaml(body: str) -> Any:
    """Tiny fallback for the YAML shapes used by runtime frontmatter.

    It is not a full YAML parser. It covers the repository's simple mappings,
    nested permission blocks, scalar lists, and remote-agent lists well enough to
    avoid false positives when PyYAML is unavailable.
    """
    rows: list[tuple[int, str]] = []
    for line in body.splitlines():
        raw = line.rstrip("\r")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        rows.append((indent, raw.strip()))
    if not rows:
        return {}

    def parse_key(raw_key: str) -> str:
        key = raw_key.strip()
        if (key.startswith("'") and key.endswith("'")) or (key.startswith('"') and key.endswith('"')):
            return key[1:-1]
        return key

    def split_key_value(stripped: str) -> tuple[str, str]:
        key, _, value = stripped.partition(":")
        return parse_key(key), value.strip()

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index < len(rows) and rows[index][1].startswith("- "):
            return parse_list(index, indent)
        return parse_mapping(index, indent)

    def parse_list(index: int, indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while index < len(rows):
            line_indent, stripped = rows[index]
            if line_indent < indent or not stripped.startswith("- "):
                break
            if line_indent > indent:
                index += 1
                continue
            tail = stripped[2:].strip()
            if not tail:
                next_index = index + 1
                if next_index < len(rows) and rows[next_index][0] > line_indent:
                    child, index = parse_block(next_index, rows[next_index][0])
                    result.append(child)
                else:
                    result.append(None)
                    index += 1
                continue
            if ":" in tail and not tail.startswith(('"', "'")):
                key, value = split_key_value(tail)
                item: dict[str, Any] = {}
                if value:
                    item[key] = parse_scalar(value)
                    index += 1
                else:
                    next_index = index + 1
                    if next_index < len(rows) and rows[next_index][0] > line_indent:
                        child, index = parse_block(next_index, rows[next_index][0])
                        item[key] = child
                    else:
                        item[key] = None
                        index += 1
                if index < len(rows) and rows[index][0] > line_indent:
                    extra, index = parse_mapping(index, rows[index][0])
                    if isinstance(extra, dict):
                        item.update(extra)
                result.append(item)
            else:
                result.append(parse_scalar(tail))
                index += 1
        return result, index

    def parse_mapping(index: int, indent: int) -> tuple[dict[str, Any], int]:
        out: dict[str, Any] = {}
        while index < len(rows):
            line_indent, stripped = rows[index]
            if line_indent < indent or stripped.startswith("- "):
                break
            if line_indent > indent:
                index += 1
                continue
            if ":" not in stripped:
                index += 1
                continue
            key, value = split_key_value(stripped)
            if value in {"|", ">"}:
                block_lines: list[str] = []
                index += 1
                while index < len(rows) and rows[index][0] > line_indent:
                    block_lines.append(rows[index][1])
                    index += 1
                out[key] = "\n".join(block_lines) if value == "|" else " ".join(block_lines)
                continue
            if value:
                out[key] = parse_scalar(value)
                index += 1
                continue

            next_index = index + 1
            if next_index < len(rows) and rows[next_index][0] > line_indent:
                child, index = parse_block(next_index, rows[next_index][0])
                out[key] = child
            elif next_index < len(rows) and rows[next_index][1].startswith("- "):
                child, index = parse_list(next_index, rows[next_index][0])
                out[key] = child
            else:
                out[key] = None
                index += 1
        return out, index

    parsed, _ = parse_block(0, rows[0][0])
    return parsed


def parse_yaml_document(body: str) -> Any:
    global YAML_FALLBACK_IN_USE, YAML_FALLBACK_WARNED
    try:
        import yaml  # type: ignore

        return yaml.safe_load(body) or {}
    except ImportError:
        YAML_FALLBACK_IN_USE = True
        if not YAML_FALLBACK_WARNED:
            warn("PyYAML not installed; using limited fallback parser — results may be unreliable")
            YAML_FALLBACK_WARNED = True
        return parse_simple_yaml(body)


def split_frontmatter(text: str) -> tuple[str, str] | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return m.group(1), text[m.end():]


def parse_frontmatter(text: str) -> dict[str, Any] | None:
    split = split_frontmatter(text)
    if split is None:
        return None
    body, _ = split
    try:
        document = parse_yaml_document(body)
    except Exception as e:
        err(f"frontmatter parse error: {e}")
        return None
    if not isinstance(document, dict):
        err("frontmatter must be a YAML mapping")
        return None
    return document


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
    for p in (REPO / ".github" / "agents").glob("*.md"):
        if p.name.endswith(".agent.md"):
            continue
        warn(
            f"{p.relative_to(REPO).as_posix()}: `.github/agents/*.md` detected; "
            "the emitter writes `.agent.md`, so verify this is an intentional "
            "Copilot import/upstream-drift signal"
        )
        targets.append((p, "copilot-agent-import"))

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
        elif kind == "agent":  # agent: <name>.agent.md
            expected = path.name.removesuffix(".agent.md")
        else:  # Copilot import/drift signal: <name>.md
            expected = path.name.removesuffix(".md")
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
    candidates = set(REPO.rglob("*.md")) | set(REPO.rglob("*.template")) | set(REPO.rglob("*.snippet.md"))
    for path in sorted(candidates):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for m in LINK_RE.finditer(text):
            if "{{" in m.group(1) or "}}" in m.group(1):
                continue
            target = (path.parent / m.group(1)).resolve()
            if not target.exists():
                err(f"{path.relative_to(REPO)}: broken link → {m.group(1)}")


# ---------- 7: Codex TOML subagents (.codex/agents/*.toml) ----------

def check_codex_toml_agents() -> None:
    try:
        import tomllib  # py 3.11+
    except ImportError:
        warn("tomllib unavailable (Python <3.11) — skipping Codex TOML validation")
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
            if isinstance(name, str) and not SLUG_RE.fullmatch(name):
                err(f"{rel}: Codex `name` must be a lowercase slug using letters, digits, hyphen, or underscore")
            if isinstance(name, str) and name != toml_path.stem:
                warn(f"{rel}: TOML `name` ({name}) differs from filename stem ({toml_path.stem}) — name is the source of truth, but matching filenames is the recommended convention")
            desc = data.get("description")
            if isinstance(desc, str) and not desc.startswith("Use when"):
                err(f"{rel}: Codex `description` must start with `Use when` for runtime discovery")
            elif desc is not None and not isinstance(desc, str):
                err(f"{rel}: Codex `description` must be a string")
            nicknames = data.get("nickname_candidates")
            if nicknames is not None:
                if not isinstance(nicknames, list):
                    err(f"{rel}: nickname_candidates must be an array of display-name strings")
                else:
                    seen_nicknames: set[str] = set()
                    for nickname in nicknames:
                        if not isinstance(nickname, str) or not nickname.strip():
                            err(f"{rel}: nickname_candidates entries must be non-empty strings")
                            continue
                        folded = nickname.casefold()
                        if folded in seen_nicknames:
                            err(f"{rel}: nickname_candidates contains duplicate `{nickname}`")
                        seen_nicknames.add(folded)
                        if not CODEX_NICKNAME_RE.fullmatch(nickname):
                            err(f"{rel}: nickname `{nickname}` must be 1-32 chars, start with a letter, and use letters/digits/space/hyphen/underscore only")
            effort = data.get("model_reasoning_effort")
            if effort and effort not in ("low", "medium", "high"):
                err(f"{rel}: model_reasoning_effort must be low|medium|high (got `{effort}`)")
            sandbox = data.get("sandbox_mode")
            if sandbox and sandbox not in ("read-only", "workspace-write"):
                warn(f"{rel}: sandbox_mode `{sandbox}` is not one of the documented values (read-only|workspace-write)")
            if is_codex_read_only_identity(data.get("name"), toml_path.stem) and sandbox != "read-only":
                err(f"{rel}: read-only reviewer/auditor/security/architect/governance Codex agents must set sandbox_mode = \"read-only\"")
            for key in ("job_max_runtime_seconds",):
                value = data.get(key)
                if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value <= 0):
                    err(f"{rel}: {key} must be a positive integer")
            spawn_csv = data.get("spawn_agents_on_csv")
            if spawn_csv is not None and not isinstance(spawn_csv, bool):
                err(f"{rel}: spawn_agents_on_csv must be boolean when present")

    for config_path in REPO.rglob(".codex/config.toml"):
        if ".git" in config_path.parts:
            continue
        rel = config_path.relative_to(REPO)
        try:
            data = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except Exception as e:
            err(f"{rel}: invalid TOML: {e}")
            continue
        agents = data.get("agents")
        if not isinstance(agents, dict):
            err(f"{rel}: missing or invalid [agents] table")
            continue
        for key in ("max_threads", "max_depth"):
            value = agents.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                err(f"{rel}: [agents].{key} must be a positive integer")


# ---------- 8: Gemini Markdown subagents (.gemini/agents/*.md, extension agents/*.md) ----------

def is_positive_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and value > 0


def is_positive_int(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and value > 0


def is_numeric(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float))


def is_gemini_local_agent_path(path: Path) -> bool:
    parts = path.parts
    return path.suffix == ".md" and not path.name.startswith("_") and any(
        parts[i] == ".gemini" and i + 2 < len(parts) and parts[i + 1] == "agents" and i + 2 == len(parts) - 1
        for i in range(len(parts))
    )


def is_gemini_extension_agent_path(path: Path) -> bool:
    if path.suffix != ".md" or path.name.startswith("_") or path.parent.name != "agents":
        return False
    return (path.parent.parent / "gemini-extension.json").is_file()


def validate_gemini_agent_record(rel: Path, record: Any, markdown_body: str, *, list_item: int | None = None) -> None:
    prefix = f"{rel}" if list_item is None else f"{rel}: item {list_item}"
    if not isinstance(record, dict):
        err(f"{prefix}: Gemini agent frontmatter must be a YAML mapping")
        return
    if "mcpServers" in record:
        err(f"{prefix}: Gemini frontmatter must use `mcp_servers`, not `mcpServers`")
    if "mcp-servers" in record:
        err(f"{prefix}: Gemini frontmatter must use `mcp_servers`, not `mcp-servers`")

    name = record.get("name")
    if not isinstance(name, str) or not name:
        err(f"{prefix}: missing required Gemini `name`")
    elif not SLUG_RE.fullmatch(name):
        err(f"{prefix}: Gemini `name` must be a lowercase slug using letters, digits, hyphen, or underscore")

    kind_value = record.get("kind", "local")
    kind = "local" if kind_value is None else kind_value
    if not isinstance(kind, str) or kind not in ("local", "remote"):
        err(f"{prefix}: Gemini `kind` must be `local` or `remote`")
        return

    for key in ("max_turns", "timeout_mins"):
        value = record.get(key)
        if value is not None and not is_positive_int(value):
            err(f"{prefix}: Gemini `{key}` must be a positive integer")
    if "temperature" in record and not is_numeric(record.get("temperature")):
        err(f"{prefix}: Gemini `temperature` must be numeric")

    if kind == "local":
        for key in ("agent_card_url", "agent_card_json", "auth"):
            if key in record:
                err(f"{prefix}: local Gemini agent must not set remote field `{key}`")
        mcp_servers = record.get("mcp_servers")
        if mcp_servers is not None and not isinstance(mcp_servers, dict):
            err(f"{prefix}: Gemini `mcp_servers` must be a mapping")
        desc = record.get("description")
        if not isinstance(desc, str) or not desc:
            err(f"{prefix}: local Gemini agent missing required `description`")
        if not markdown_body.strip():
            err(f"{prefix}: local Gemini agent body must contain the system prompt")
    else:
        for key in ("tools", "mcp_servers", "model", "temperature", "max_turns", "timeout_mins"):
            if key in record:
                err(f"{prefix}: remote Gemini agent must not set local execution field `{key}`")
        has_url = "agent_card_url" in record
        has_json = "agent_card_json" in record
        if has_url == has_json:
            err(f"{prefix}: remote Gemini agent requires exactly one of `agent_card_url` or `agent_card_json`")
        elif has_url:
            url = record.get("agent_card_url")
            if not isinstance(url, str) or not re.fullmatch(r"https?://\S+", url):
                err(f"{prefix}: remote Gemini `agent_card_url` must be an http(s) URL")
        elif not isinstance(record.get("agent_card_json"), dict):
            err(f"{prefix}: remote Gemini `agent_card_json` must be a mapping")


def check_gemini_markdown_agents() -> None:
    for path in REPO.rglob("*.md"):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        if not is_gemini_local_agent_path(path) and not is_gemini_extension_agent_path(path):
            continue
        rel = path.relative_to(REPO)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            err(f"{rel}: not valid UTF-8")
            continue
        split = split_frontmatter(text)
        if split is None:
            err(f"{rel}: missing Gemini YAML frontmatter")
            continue
        frontmatter_body, markdown_body = split
        try:
            document = parse_yaml_document(frontmatter_body)
        except Exception as e:
            err(f"{rel}: invalid Gemini YAML frontmatter: {e}")
            continue
        if isinstance(document, list):
            if not document:
                err(f"{rel}: Gemini remote-agent YAML list must not be empty")
                continue
            for index, item in enumerate(document):
                if not isinstance(item, dict) or item.get("kind") != "remote":
                    err(f"{rel}: remote YAML lists are allowed only when every item has `kind: remote`")
                    break
                validate_gemini_agent_record(rel, item, "", list_item=index)
            continue
        validate_gemini_agent_record(rel, document, markdown_body)


# ---------- 9: OpenCode Markdown agents (.opencode/agents/*.md) ----------

def is_opencode_agent_path(path: Path) -> bool:
    parts = path.parts
    return path.suffix == ".md" and (
        any(parts[i] == ".opencode" and i + 1 < len(parts) and parts[i + 1] == "agents" for i in range(len(parts)))
        or any(
            parts[i] == ".config"
            and i + 2 < len(parts)
            and parts[i + 1] == "opencode"
            and parts[i + 2] == "agents"
            for i in range(len(parts))
        )
    )


def check_opencode_markdown_agents() -> None:
    valid_modes = {"primary", "subagent", "all"}
    valid_permission_keys = {
        "read",
        "edit",
        "glob",
        "grep",
        "list",
        "bash",
        "task",
        "external_directory",
        "todowrite",
        "webfetch",
        "websearch",
        "codesearch",
        "lsp",
        "skill",
        "question",
        "doom_loop",
    }
    valid_actions = {"allow", "ask", "deny"}

    for path in REPO.rglob("*.md"):
        if ".git" in path.parts or "node_modules" in path.parts or not is_opencode_agent_path(path):
            continue
        rel = path.relative_to(REPO)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            err(f"{rel}: not valid UTF-8")
            continue
        split = split_frontmatter(text)
        frontmatter_body = split[0] if split else ""
        fm = parse_frontmatter(text)
        if fm is None:
            err(f"{rel}: missing or unparseable OpenCode YAML frontmatter")
            continue
        if "name" in fm:
            err(f"{rel}: OpenCode Markdown agents must not set `name`; filename stem is the agent name")
        if not fm.get("description"):
            err(f"{rel}: OpenCode frontmatter missing required `description`")
        mode = fm.get("mode")
        if mode is not None and mode not in valid_modes:
            err(f"{rel}: OpenCode `mode` must be one of primary|subagent|all")
        if mode == "primary":
            permission = fm.get("permission")
            task_permission = permission.get("task") if isinstance(permission, dict) else None
            fallback_permission_task_text = (
                YAML_FALLBACK_IN_USE
                and re.search(r"(?m)^\s*permission\s*:", frontmatter_body)
                and re.search(r"(?m)^\s*task\s*:", frontmatter_body)
            )
            if not isinstance(permission, dict):
                if fallback_permission_task_text:
                    warn(f"{rel}: PyYAML fallback could not verify nested OpenCode `permission.task`; install PyYAML for strict validation")
                else:
                    err(f"{rel}: OpenCode primary agents must gate subagent invocation with `permission.task`")
            elif not isinstance(task_permission, dict):
                if fallback_permission_task_text:
                    warn(f"{rel}: PyYAML fallback could not verify nested OpenCode `permission.task`; install PyYAML for strict validation")
                else:
                    err(f"{rel}: OpenCode primary agents must set `permission.task` as a mapping with `\"*\": deny` or `\"*\": ask`")
            elif task_permission.get("*") not in {"deny", "ask"}:
                err(f"{rel}: OpenCode primary `permission.task` must include `\"*\": deny` or `\"*\": ask`; permissive wildcard allow is not allowed")
        for key in ("mcp-servers", "mcpServers"):
            if key in fm:
                err(f"{rel}: OpenCode agents must not set `{key}`; configure MCP in opencode.json `mcp`")
        permission = fm.get("permission")
        if permission is not None:
            if not isinstance(permission, dict):
                err(f"{rel}: OpenCode `permission` must be a mapping")
            else:
                for perm_key, perm_value in permission.items():
                    if perm_key not in valid_permission_keys:
                        err(f"{rel}: OpenCode permission key `{perm_key}` is not documented")
                        continue
                    if isinstance(perm_value, str):
                        if perm_value not in valid_actions:
                            err(f"{rel}: OpenCode permission `{perm_key}` must be allow|ask|deny")
                    elif isinstance(perm_value, dict):
                        rules = list(perm_value.items())
                        if "*" in perm_value and rules and rules[0][0] != "*":
                            err(f"{rel}: OpenCode permission `{perm_key}` wildcard `*` must appear first because rules are last-match-wins")
                        for pattern, action in rules:
                            if not isinstance(pattern, str) or action not in valid_actions:
                                err(f"{rel}: OpenCode permission `{perm_key}` rules must map string patterns to allow|ask|deny")
                    else:
                        err(f"{rel}: OpenCode permission `{perm_key}` must be allow|ask|deny or a pattern mapping")
        if "tools" in fm and "permission" not in fm:
            warn(f"{rel}: OpenCode `tools` is deprecated; prefer `permission` for tool gating")


# ---------- 10: Claude plugin-shipped agent field restrictions ----------

CLAUDE_PLUGIN_AGENT_FORBIDDEN_FIELDS = ("hooks", "mcpServers", "permissionMode")


def is_claude_plugin_agent_path(path: Path) -> bool:
    if path.suffix != ".md" or path.name.startswith("_"):
        return False
    for root in path.parents:
        agents_dir = root / "agents"
        if (root / ".claude-plugin" / "plugin.json").is_file() and path.is_relative_to(agents_dir):
            return True
    return False


def check_claude_plugin_agent_fields() -> None:
    for path in REPO.rglob("*.md"):
        if ".git" in path.parts or "node_modules" in path.parts or not is_claude_plugin_agent_path(path):
            continue
        rel = path.relative_to(REPO)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            err(f"{rel}: not valid UTF-8")
            continue
        fm = parse_frontmatter(text)
        if fm is None:
            err(f"{rel}: missing or unparseable Claude plugin agent frontmatter")
            continue
        for key in CLAUDE_PLUGIN_AGENT_FORBIDDEN_FIELDS:
            if key in fm:
                err(f"{rel}: Claude plugin-shipped agents must not use project/user-only field `{key}`")


# ---------- 11: replication ledger location ----------

LEDGER_FORBIDDEN_DIRS = (
    ".claude/agents",
    ".codex/agents",
    ".opencode/agents",
    ".github/agents",
    ".gemini/agents",
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
        if is_gemini_extension_agent_path(path):
            err(f"{rel}: replication ledger/log must not live inside a Gemini extension `agents/` directory. Move to `.agents-system-setup/replication.jsonl`.")
        if path.suffix == ".md" and "/agents/" in f"/{rel}":
            err(f"{rel}: replication artifact with `.md` extension inside an agents/ tree will be parsed as a malformed agent.")


# ---------- 12: governance baseline ----------

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


def require_not_contains(path: Path, needles: tuple[str, ...]) -> None:
    rel = path.relative_to(REPO).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return
    for needle in needles:
        if needle in text:
            err(f"{rel}: forbidden stale runtime marker `{needle}`")


def require_matches(path: Path, patterns: tuple[str, ...]) -> None:
    rel = path.relative_to(REPO).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        err(f"{rel}: required governance file is missing")
        return
    except UnicodeDecodeError:
        err(f"{rel}: not valid UTF-8")
        return
    for pattern in patterns:
        if not re.search(pattern, text, re.MULTILINE):
            err(f"{rel}: missing required governance pattern `{pattern}`")


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


SECRET_SHAPE_RE = re.compile(
    r"("
    r"gh[psour]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"AIza[A-Za-z0-9_-]{35}|glpat-[A-Za-z0-9_-]{20,}|"
    r"(?:sk|rk)_live_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|"
    r"xox[abprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}|"
    r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|"
    r"AccountKey=[A-Za-z0-9+/=]{20,}|SharedAccessSignature=[^\s'\"<>]{20,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r")"
)
ENV_PLACEHOLDER_RE = re.compile(
    r"\$\{[A-Za-z_][A-Za-z0-9_]*\}|\{env:[A-Za-z_][A-Za-z0-9_]*\}"
)
OPTIONAL_PLACEHOLDER_RE = re.compile(r"\{\{OPTIONAL_[A-Z0-9_]+\}\}")
MCP_FRONTMATTER_KEYS = {"mcp-servers", "mcp_servers", "mcpServers"}
CODEX_MCP_TABLE_RE = re.compile(
    r"(?m)^\s*(?:\[\s*mcp_servers(?:\.[^\]\s#]+)?\s*\]|\[\[\s*mcp_servers(?:\.[^\]\s#]+)?\s*\]\])\s*(?:#.*)?$"
)


def _env_placeholder_spans(line: str) -> list[tuple[int, int]]:
    return [match.span() for match in ENV_PLACEHOLDER_RE.finditer(line)]


def _span_inside_any(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    return any(span_start <= start and end <= span_end for span_start, span_end in spans)


def _is_runtime_agent_path(path: Path) -> bool:
    rel = path.relative_to(REPO).as_posix()
    agent_dirs = (
        ".github/agents/",
        ".claude/agents/",
        ".opencode/agents/",
        ".codex/agents/",
        ".gemini/agents/",
    )
    return any(part in rel for part in agent_dirs)


def _has_structural_mcp_config(path: Path, text: str) -> bool:
    """Detect actual MCP config surfaces, not prose mentioning key names."""
    if path.suffix == ".toml":
        return bool(CODEX_MCP_TABLE_RE.search(text))
    if path.suffix != ".md":
        return False
    split = split_frontmatter(text)
    if split is None:
        return False
    try:
        document = parse_yaml_document(split[0])
    except Exception:
        return False
    if not isinstance(document, dict):
        return False
    for key in MCP_FRONTMATTER_KEYS:
        value = document.get(key)
        if value not in (None, "", [], {}):
            return True
    return False


def _is_mcp_or_memory_surface(path: Path) -> bool:
    rel = path.relative_to(REPO).as_posix()
    if ".git" in path.parts or "node_modules" in path.parts or not path.is_file():
        return False
    lower_name = path.name.lower()
    if rel in {"AGENTS.md", "GEMINI.md"}:
        return True
    if path.name in {".mcp.json", "opencode.json"}:
        return True
    if path.suffix == ".json" and (
        lower_name.startswith("mcp") or lower_name.startswith(".mcp") or lower_name.endswith("mcp.json")
    ):
        return True
    if path.name == "config.toml" and ".codex" in path.parts:
        return True
    if path.name in {"settings.json", "settings.local.json"} and ".claude" in path.parts:
        return True
    if path.name == "settings.json" and ".gemini" in path.parts:
        return True
    if _is_runtime_agent_path(path) and path.suffix in {".md", ".toml"}:
        return True
    if path.suffix in {".template", ".md"} and str(SKILL_ROOT / "assets") in str(path):
        return "mcp" in path.read_text(encoding="utf-8", errors="ignore").lower()
    return ("learning" in lower_name or "learnings" in lower_name) and path.suffix in {".md", ".jsonl"}


def check_mcp_approval_gate() -> None:
    """Keep MCP writes explicit, approval-gated, and auditable."""
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "MCP config approval gate",
            "Phase 3.5 — MCP Config Approval Gate (mandatory",
            "No MCP write may occur before this gate returns approval",
            "Replication re-triggers this gate per new target",
            "agents-system-setup:mcp-approved",
            "x-agents-system-setup",
            "<config>.agents-system-setup.approval.json",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "replication.md",
        (
            "MCP APPROVAL GATE",
            "Replication must re-trigger the MCP approval gate",
            "approvals",
            "artifact_tracking",
            "overwrites",
            "x-agents-system-setup",
            "<config>.agents-system-setup.approval.json",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "platforms.md",
        (
            "agents-system-setup:mcp-approved",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.agent.md.template",
        (
            ".mcp.json",
            "Route security-sensitive work",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.claude.md.template",
        (
            ".mcp.json",
            "Route security-sensitive work",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.opencode.md.template",
        (
            "opencode.json",
            "Route security-sensitive work",
            "{{OPTIONAL_PERMISSION_TASK_BLOCK}}",
        ),
    )
    for rel in (
        "subagent.agent.md.template",
        "subagent.claude.md.template",
        "subagent.opencode.md.template",
        "subagent.gemini.md.template",
    ):
        require_contains(
            SKILL_ROOT / "assets" / rel,
            (
                "{{OPTIONAL_MCP_APPROVAL_MARKER}}",
            ),
        )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "{{OPTIONAL_MCP_APPROVAL_COMMENT}}",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "Optional placeholder substitution table",
            "{{OPTIONAL_MCP_APPROVAL_MARKER}}",
            "{{OPTIONAL_MCP_APPROVAL_COMMENT}}",
            "{{OPTIONAL_PERMISSION_TASK_BLOCK}}",
            "Never emit `permission.task` with `\"*\": allow`",
        ),
    )

    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "node_modules" in path.parts:
            continue
        if not _is_runtime_agent_path(path) or path.suffix not in {".md", ".toml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        has_mcp = _has_structural_mcp_config(path, text)
        if has_mcp and "agents-system-setup:mcp-approved" not in text:
            err(f"{path.relative_to(REPO).as_posix()}: MCP block present without approval marker — re-run Phase 3.5")


def _central_mcp_server_names(path: Path) -> set[str]:
    if path.name not in {".mcp.json", "opencode.json"}:
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return set()
    if not isinstance(data, dict):
        return set()
    if path.name == ".mcp.json":
        block = data.get("mcpServers") or data.get("mcp")
    else:
        block = data.get("mcp")
    if not isinstance(block, dict):
        return set()
    return {str(name) for name, value in block.items() if not str(name).startswith("x-") and value is not None}


def _metadata_covers_mcp_servers(metadata: Any, server_names: set[str]) -> bool:
    if not isinstance(metadata, dict):
        return False
    approval = metadata.get("mcp_approval")
    if not isinstance(approval, dict):
        approval = metadata
    servers = approval.get("servers") or approval.get("server_names") or approval.get("approved_servers")
    if isinstance(servers, dict):
        covered = {str(name) for name in servers}
    elif isinstance(servers, list):
        covered = {str(name) for name in servers}
    elif servers == "all":
        covered = set(server_names)
    else:
        covered = set()
    if not server_names.issubset(covered):
        return False
    has_decision = bool(approval.get("decision") or approval.get("approval_state"))
    has_actor = bool(approval.get("approved_by") or approval.get("approval_ref") or approval.get("owner"))
    has_evidence = bool(approval.get("evidence") or approval.get("verification_evidence"))
    return has_decision and has_actor and has_evidence


def _central_mcp_approval_sidecars(path: Path) -> tuple[Path, ...]:
    rel_token = path.relative_to(REPO).as_posix().replace("/", "__")
    return (
        path.with_name(f"{path.name}.agents-system-setup.approval.json"),
        REPO / ".agents-system-setup" / "mcp-approvals" / f"{rel_token}.json",
    )


def _central_mcp_config_has_approval_evidence(path: Path, server_names: set[str]) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return False
    if isinstance(data, dict) and _metadata_covers_mcp_servers(data.get("x-agents-system-setup"), server_names):
        return True
    for sidecar in _central_mcp_approval_sidecars(path):
        try:
            sidecar_data = json.loads(sidecar.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        if _metadata_covers_mcp_servers(sidecar_data.get("x-agents-system-setup", sidecar_data), server_names):
            return True
    return False


def check_central_mcp_approval_evidence() -> None:
    """Central MCP configs with server names need durable approval metadata."""
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "node_modules" in path.parts:
            continue
        if path.name not in {".mcp.json", "opencode.json"}:
            continue
        server_names = _central_mcp_server_names(path)
        if not server_names:
            continue
        if not _central_mcp_config_has_approval_evidence(path, server_names):
            rel = path.relative_to(REPO).as_posix()
            names = ", ".join(sorted(server_names))
            err(f"{rel}: central MCP config has servers ({names}) without `x-agents-system-setup` approval metadata or approval sidecar")


def check_optional_placeholder_leaks() -> None:
    """Generated runtime agent directories must not contain template placeholders."""
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "node_modules" in path.parts:
            continue
        if not _is_runtime_agent_path(path) or path.suffix not in {".md", ".toml"}:
            continue
        rel = path.relative_to(REPO).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        match = OPTIONAL_PLACEHOLDER_RE.search(text)
        if match:
            err(f"{rel}: unresolved optional placeholder `{match.group(0)}` in generated runtime agent directory")


def check_optional_placeholder_table() -> None:
    """agent-format.md must document every optional placeholder used by assets."""
    placeholders: set[str] = set()
    for path in (SKILL_ROOT / "assets").rglob("*"):
        if not path.is_file():
            continue
        try:
            placeholders.update(OPTIONAL_PLACEHOLDER_RE.findall(path.read_text(encoding="utf-8")))
        except (UnicodeDecodeError, OSError):
            continue
    try:
        table_text = (SKILL_ROOT / "references" / "agent-format.md").read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        err("references/agent-format.md: missing optional placeholder substitution table")
        return
    for placeholder in sorted(placeholders):
        if placeholder not in table_text:
            err(f"references/agent-format.md: optional placeholder table missing `{placeholder}`")


def check_mcp_secret_shape() -> None:
    """MCP config and learning memory must use env placeholders, not inline tokens."""
    for path in REPO.rglob("*"):
        if not _is_mcp_or_memory_surface(path):
            continue
        rel = path.relative_to(REPO).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            placeholder_spans = _env_placeholder_spans(line)
            for match in SECRET_SHAPE_RE.finditer(line):
                if _span_inside_any(match.start(), match.end(), placeholder_spans):
                    continue
                err(f"{rel}:{line_no}: secret-shaped value in MCP or learning surface; use an environment variable placeholder")


# ---------- 13: context optimization ----------

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
            "Task-Type Routing Map",
            "Context freshness rule",
            "Compact mode trimming",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
            "Delegation packet (canonical schema)",
            "Context freshness:",
            "Required minimum",
            "Expansion blocks",
            "Goal & Definition of Done",
            "File Inventory",
            "Verification Protocol",
            "Reporting Protocol",
            "Recommended Packet Form",
            "Acceptance Checklist",
            "Reporting Template",
            "Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>",
            "Clarification Protocol",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "Codex TOML summary + pointer rule",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Context budget",
            "Task assignment quality",
            "Clarifications requested",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Phase 1.9 — Output Profile & Context Budget",
            "Context Loading Policy",
            "Context profile",
            "Context split",
            "Task-Type Routing Map",
            "Context freshness",
            "compact-mode trimming",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Read First",
            "## Context Loading Policy",
            "{{CONTEXT_PROFILE}}",
            "{{DETAIL_REFERENCES}}",
            "Task-Type Routing Map",
            "Context Freshness",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "GEMINI.md.template",
        (
            "agents-system-setup:platform: gemini-cli",
            "AGENTS.md",
            ".gemini/agents/*.md",
            "mcp_servers",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.agent.md.template",
        (
            "## Context Load Order",
            "## Delegation Packet",
            "AGENTS.md",
            "Plan Handoff Contract",
            "Context freshness: recent",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.claude.md.template",
        (
            "## Delegation Packet",
            "AGENTS.md",
            "Plan Handoff Contract",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.opencode.md.template",
        (
            "## Delegation Packet",
            "AGENTS.md",
            "Plan Handoff Contract",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        (
            "## Context Load Order",
            "Keep the response concise",
            "## Acceptance Checklist",
            "## Reporting Template",
            "clarification_request",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.claude.md.template",
        (
            "## Acceptance Checklist",
            "## Reporting Template",
            "clarification_request",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.opencode.md.template",
        (
            "## Acceptance Checklist",
            "## Reporting Template",
            "clarification_request",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.gemini.md.template",
        (
            "## Acceptance Checklist",
            "## Reporting Template",
            "clarification_request",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "Context Load Order",
            "Outcome first",
            "summary + pointer rule",
            "Task Assignment Acceptance Checklist",
            "clarification_request",
        ),
    )

    _check_codex_developer_instructions_budget(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template"
    )
    _check_agents_template_read_first_budget(
        SKILL_ROOT / "assets" / "AGENTS.md.template"
    )
    _check_managed_block_drift()

    skill_path = SKILL_ROOT / "SKILL.md"
    try:
        line_count = len(skill_path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return
    if line_count > 500:
        err(f"{skill_path.relative_to(REPO).as_posix()}: SKILL.md exceeds hard 500-line limit ({line_count})")
    elif line_count > 300:
        warn(f"{skill_path.relative_to(REPO).as_posix()}: SKILL.md is {line_count} lines; target is about 250. Consider moving more detail to references.")


def _check_codex_developer_instructions_budget(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return
    rel = path.relative_to(REPO).as_posix()
    match = re.search(r'developer_instructions\s*=\s*"""(.*?)"""', text, re.DOTALL)
    if not match:
        return
    body_lines = len(match.group(1).strip("\n").splitlines())
    if body_lines > 80:
        warn(f"{rel}: Codex developer_instructions block is {body_lines} lines; target is <= 60 (apply summary + pointer rule).")


def _check_agents_template_read_first_budget(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return
    rel = path.relative_to(REPO).as_posix()
    match = re.search(r"## Read First\s*\n(.*?)\n## ", text, re.DOTALL)
    if not match:
        return
    body_lines = len([line for line in match.group(1).splitlines() if line.strip()])
    if body_lines > 12:
        warn(f"{rel}: AGENTS.md template Read First has {body_lines} non-empty lines; aim for <= 8.")


def _check_managed_block_drift() -> None:
    import subprocess

    marker_start = "<!-- agents-system-setup:managed:start -->"
    marker_end = "<!-- agents-system-setup:managed:end -->"
    for path in REPO.rglob("*.md"):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if marker_start not in text or marker_end not in text:
            continue
        rel = path.relative_to(REPO).as_posix()
        new_block = _extract_managed_block(text, marker_start, marker_end)
        if new_block is None:
            continue
        try:
            old = subprocess.run(
                ["git", "show", f"HEAD:{rel}"],
                capture_output=True,
                text=True,
                cwd=REPO,
                check=False,
            )
        except FileNotFoundError:
            return
        if old.returncode != 0:
            continue
        old_block = _extract_managed_block(old.stdout, marker_start, marker_end)
        if not old_block or len(old_block) < 10:
            continue
        if len(new_block) > int(len(old_block) * 2.5):
            warn(
                f"{rel}: managed block grew from {len(old_block)} to {len(new_block)} lines (>2.5x). Consider moving overflow detail to a reference per context-optimization."
            )


def _extract_managed_block(text: str, start: str, end: str) -> list[str] | None:
    try:
        block = text.split(start, 1)[1].split(end, 1)[0]
    except IndexError:
        return None
    return [line for line in block.splitlines() if line.strip()]


# ---------- 14: local-vs-git-tracked artifact policy ----------

def check_local_tracking_policy() -> None:
    require_contains(
        SKILL_ROOT / "references" / "local-tracking.md",
        (
            "project-tracked",
            "project-local",
            "personal-global",
            ".git/info/exclude",
            "git check-ignore",
            "GEMINI.md",
            ".gemini/agents/",
            "not a security boundary",
            "always reference environment variables",
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


# ---------- 15: plan handoff policy ----------

def check_plan_handoff_policy() -> None:
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
            "Plan Handoff Contract",
            "HandoffIR",
            "agent: Plan",
            "Copilot CLI",
            "Claude Code",
            "OpenCode",
            "OpenAI Codex (CLI + App)",
            "Gemini CLI",
            "developer_instructions",
            ".gemini/agents/",
            "These twelve fields are mandatory",
            "Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Plan handoff is normalized before emission",
            "Plan Handoff Contract",
            "HandoffIR",
            "references/handoff.md",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Plan Handoff Contract",
            "{{HANDOFF_SOURCES}}",
            "Canonical required fields (12)",
            "Task",
            "Source plan",
            "Owned paths",
            "Read-only paths",
            "Relevant gates",
            "Constraints",
            "Dependencies / wave",
            "Required approvals",
            "Runtime format target",
            "Expected output",
            "Context freshness",
            "Lossiness",
            "Expansion fields",
            "Owning agent",
            "Evidence",
            "{{PLATFORM_FORMAT_NOTES}}",
            "{{HANDOFF_EVIDENCE}}",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.agent.md.template",
        (
            "Plan Handoff Contract",
            "AGENTS.md",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.claude.md.template",
        (
            "agents-system-setup:platform: claude-code",
            "Plan Handoff Contract",
            "AGENTS.md",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.opencode.md.template",
        (
            "agents-system-setup:platform: opencode",
            "mode: primary",
            "{{OPTIONAL_PERMISSION_TASK_BLOCK}}",
            "AGENTS.md",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        (
            "## Handoff Input",
            "{{HANDOFF_SOURCE}}",
            "{{RUNTIME_FORMAT_TARGET}}",
            "Handoff status",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.claude.md.template",
        (
            "agents-system-setup:platform: claude-code",
            "## Handoff Input",
            "Claude Code frontmatter schema",
            "comma-separated string",
            "Do not use a YAML list",
            "Handoff status",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.opencode.md.template",
        (
            "agents-system-setup:platform: opencode",
            "mode: subagent",
            "OpenCode frontmatter schema",
            "No `name:` key",
            "opencode.json",
            "Handoff status",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "Plan Handoff:",
            "{{HANDOFF_SOURCE}}",
            "{{RUNTIME_FORMAT_TARGET}}",
            "Handoff status",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Plan handoff",
            "Runtime format targets",
        ),
    )


# ---------- 16: Codex CLI + App compatibility ----------

def check_codex_cli_app_compatibility() -> None:
    """Codex setup/replication emits shared repo artifacts that work across
    CLI + App surfaces where Codex loads those artifacts. Keep CLI plugin and
    slash-command UX explicitly CLI-only.
    """
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "OpenAI Codex (CLI + App)",
            "CLI-only instructions",
            ".codex/agents/<kebab-name>.toml",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "platforms.md",
        (
            "OpenAI Codex CLI + App",
            "Shared artifacts",
            "CLI-only UX",
            "App-visible UX",
            "Do not claim Codex App plugin installation",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "OpenAI Codex CLI + App",
            "CLI-only",
            "Codex App behavior",
            "nickname_candidates",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "replication.md",
        (
            "Codex CLI + App compatibility rule",
            "surface lossiness",
            ".codex/agents/<name>.toml",
            "must not become required Codex App behavior",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "OpenAI Codex",
            "CLI + App project memory",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "Compatible with Codex CLI and Codex App",
            "Do not require CLI-only commands",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "codex-cli",
            "CLI + App compatible artifacts",
            "plugin install and slash-command examples explicitly CLI-only",
        ),
    )
    require_contains(
        REPO / "README.md",
        (
            "OpenAI Codex (CLI + App)",
            "OpenAI Codex CLI install",
            "Plugin marketplace install and slash-command examples above are CLI-only",
        ),
    )


# ---------- 17: runtime update drift policy ----------

def check_runtime_update_policy() -> None:
    """Latest runtime changes must be source-backed and fully wired across the
    five supported runtimes: Copilot CLI, Claude Code, OpenCode, Codex, Gemini.
    """
    runtime_updates = SKILL_ROOT / "references" / "runtime-updates.md"
    models_ref = SKILL_ROOT / "references" / "models.md"
    require_contains(
        models_ref,
        (
            "Per-Runtime Model Constraints",
            "Copilot CLI",
            "Claude Code",
            "OpenCode",
            "OpenAI Codex (CLI + App)",
            "Gemini CLI",
            "Rate limits",
            "Sources",
            "Decision aid",
            "inherit",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "interview.md",
        (
            "Per-Agent Model Override",
            "(./models.md)",
            "platform default",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Model overrides",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "replication.md",
        (
            "Replication preserves explicit `model:` overrides only",
        ),
    )
    require_contains(
        runtime_updates,
        (
            "Runtime Update Audit",
            "Copilot CLI",
            ".github/agents/<name>.md",
            ".github/agents/<name>.agent.md",
            "Claude Code",
            "plugin-shipped agents",
            "OpenCode",
            "Permission keys",
            "OpenAI Codex (CLI + App)",
            "job_max_runtime_seconds",
            "spawn_agents_on_csv",
            "Gemini CLI",
            "Supported",
            ".gemini/agents/*.md",
            "extension `agents/*.md`",
            "mcp_servers",
            "agent_card_url",
            "agent_card_json",
        ),
    )
    require_matches(runtime_updates, (r"Last verified: \d{4}-\d{2}-\d{2}",))
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Runtime drift is source-backed and gated",
            "runtime-updates.md",
            "Gemini CLI",
            ".gemini/agents/*.md",
            "subagent.gemini.md.template",
            "mcp_servers",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "platforms.md",
        (
            "Gemini CLI",
            "Emit `.github/agents/<name>.agent.md`",
            ".github/agents/<name>.md",
            "plugin-shipped agents",
            "Permission keys",
            "job_max_runtime_seconds",
            "spawn_agents_on_csv",
            ".gemini/agents/<name>.md",
            "extension `agents/*.md`",
            "mcp_servers",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "Emitter rule: keep writing `.github/agents/<name>.agent.md`",
            "Schema split",
            "Plugin-shipped agents",
            "Permission keys",
            "job_max_runtime_seconds",
            "spawn_agents_on_csv",
            "Gemini CLI",
            ".gemini/agents/*.md",
            "kind: local",
            "kind: remote",
            "mcp_servers",
            "agent_card_url",
            "agent_card_json",
            "subagents must not recursively call subagents",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "replication.md",
        (
            "source_scope",
            "agent_invocation",
            "limits:",
            "plugin_component_refs",
            "surface_lossiness",
            "Gemini CLI",
            "gemini-cli",
            "Tool-name canonicalization",
            "agent spawning is implicit",
            "mcp_servers",
            "agent_card_url",
            "agent_card_json",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "marketplaces.md",
        (
            "Gemini CLI",
            ".gemini/agents/*.md",
            "skills`, `mcpServers`, `apps`",
        ),
    )
    require_matches(SKILL_ROOT / "references" / "marketplaces.md", (r"Last verified: \d{4}-\d{2}-\d{2}",))
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Runtime drift notes",
            "Gemini",
            "artifact",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.opencode.md.template",
        (
            "Use `permission:` for tool gating",
            "doom_loop",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "job_max_runtime_seconds",
            "spawn_agents_on_csv",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.gemini.md.template",
        (
            "agents-system-setup:platform: gemini-cli",
            "kind: local",
            "mcp_servers",
            "not `mcpServers`",
            "agent_card_url",
            "agent_card_json",
            "subagents cannot call subagent tools",
        ),
    )
    require_contains(
        REPO / "README.md",
        (
            "Runtime update audit",
            "Gemini CLI now has official subagent docs",
            "supported artifact-first",
            ".gemini/agents/*.md",
        ),
    )
    require_contains(
        REPO / "CHANGELOG.md",
        (
            "five supported runtimes",
            "Gemini CLI",
            "artifact support",
        ),
    )

    for path in (
        runtime_updates,
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "references" / "platforms.md",
        SKILL_ROOT / "references" / "agent-format.md",
        SKILL_ROOT / "references" / "replication.md",
        SKILL_ROOT / "references" / "marketplaces.md",
        SKILL_ROOT / "references" / "output-contract.md",
    ):
        require_not_contains(
            path,
            (
                "Gemini CLI is tracked as a candidate",
                "Gemini CLI is a candidate / monitor only runtime",
                "Gemini CLI candidate",
                "Gemini candidate only",
                "Gemini CLI subagents (candidate only)",
            ),
        )

    validator_text = Path(__file__).read_text(encoding="utf-8")
    for marker in (
        "check_gemini_markdown_agents",
        "check_opencode_markdown_agents",
        "check_claude_plugin_agent_fields",
        "mcp_servers",
        "agent_card_url",
        "GEMINI.md",
        "models.md",
        "Model overrides",
        "Acceptance Checklist",
        "Task assignment quality",
        "check_copilot_tool_profile",
        "Copilot CLI Standard Tool Profiles",
        "check_learning_memory_policy",
        "Memory & Learning System",
        "check_runtime_invocation_policy",
        "$skill-name",
        "SUPPORTED_RUNTIMES",
        "check_mcp_approval_gate",
        "check_mcp_secret_shape",
        "check_optional_placeholder_leaks",
        "agents-system-setup:mcp-approved",
    ):
        if marker not in validator_text:
            err(f"scripts/_validate.py: missing runtime validator marker `{marker}`")

    for manifest in VERSIONED_MANIFESTS:
        data = load_json(manifest)
        if not data:
            continue
        compat = data.get("compatibility", {})
        if isinstance(compat, dict) and "gemini-cli" in compat and not isinstance(compat["gemini-cli"], str):
            err(f"{manifest.relative_to(REPO).as_posix()}: compatibility.gemini-cli must be a version string when present")


def check_runtime_invocation_policy() -> None:
    """Guard provider-specific skill/command/plugin invocation syntax.

    The supported runtimes intentionally differ: Codex uses `$skill-name`,
    slash commands are runtime command surfaces, and `@` selects agents/plugins
    only where the provider documents that composer behavior.
    """
    references = SKILL_ROOT / "references"
    platforms = references / "platforms.md"
    skill_format = references / "skill-format.md"
    marketplaces = references / "marketplaces.md"
    plugin_discovery = references / "plugin-discovery.md"
    runtime_updates = references / "runtime-updates.md"

    require_contains(
        runtime_updates,
        (
            "Invocation and packaging audit",
            "2026-05-05",
            "$skill-name",
            "PLUGIN@MARKETPLACE",
            "permission.skill",
            ".opencode/commands/<name>.md",
            ".gemini/skills/<name>/SKILL.md",
            "native `settings.json` hooks",
            "Do not generalize `/`,",
        ),
    )
    require_contains(
        platforms,
        (
            ".opencode/commands/<name>.md",
            "$ARGUMENTS",
            "permission.skill",
            ".gemini/skills/<name>/SKILL.md",
            "~/.gemini/skills/<name>/SKILL.md",
            "native `settings.json` hooks",
            "not legacy",
            "no `$skill` or `/<skill>` invocation",
        ),
    )
    require_contains(
        skill_format,
        (
            ".gemini/skills/<name>/SKILL.md",
            ".agents/skills/<name>/SKILL.md",
            "~/.gemini/skills/<name>/SKILL.md",
            "`skill` tool",
            "permission.skill",
            "`/skills` to list/manage",
            "$skill-name",
            "Codex-specific",
        ),
    )
    require_contains(
        marketplaces,
        (
            "PLUGIN@MARKETPLACE",
            "/skills         # browse and select installed skills",
            "type @ to choose an installed plugin",
            "$skill-name",
            "permission.skill",
            ".opencode/commands/<name>.md",
            ".gemini/skills/<name>/SKILL.md",
            "settings hooks or extension hooks",
            "`commands/` (slash commands); `skills/` preferred",
        ),
    )
    require_contains(
        plugin_discovery,
        (
            ".opencode/plugins/",
            "opencode.json › plugins",
        ),
    )
    require_contains(
        REPO / "README.md",
        (
            "$agents-system-setup",
            "/skills         # list available skills",
            "generated repo artifacts remain compatible with both CLI and App",
        ),
    )

    scan_paths = [REPO / "README.md", *sorted(references.glob("*.md"))]
    for path in scan_paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (FileNotFoundError, UnicodeDecodeError):
            continue
        rel = path.relative_to(REPO).as_posix()
        for line_no, line in enumerate(lines, 1):
            if "@agents-system-setup" in line:
                err(
                    f"{rel}:{line_no}: stale Codex invocation example "
                    "`@agents-system-setup`; use `$agents-system-setup` "
                    "or `/skills` for bundled skills"
                )
            if "@<plugin-name>" in line:
                err(
                    f"{rel}:{line_no}: stale Codex plugin invocation example "
                    "`@<plugin-name>`; describe typing `@` to choose a plugin "
                    "and `$skill-name` or `/skills` for skills"
                )
            if "opencode plugin install" in line:
                negative_context = re.search(
                    r"\b(no|not|without|nonexistent|does not exist|there is no)\b",
                    line,
                    re.IGNORECASE,
                )
                if not negative_context:
                    err(
                        f"{rel}:{line_no}: stale OpenCode install command "
                        "`opencode plugin install`; use JS/TS plugin paths or "
                        "opencode.json plugin config guidance"
                    )
            if re.search(r"commands/.*legacy", line, re.IGNORECASE):
                not_legacy = re.search(r"\bnot\s+legacy\b|\bnot\b.*\blegacy\b", line, re.IGNORECASE)
                if not not_legacy:
                    warn(
                        f"{rel}:{line_no}: Claude/OpenCode command guidance "
                        "mentions `commands/` as legacy; plugin slash commands "
                        "remain supported"
                    )


def check_copilot_tool_profile() -> None:
    """Hard-enforce the Copilot CLI Standard Tool Profile across docs + templates.

    Source: https://docs.github.com/en/copilot/reference/custom-agents-configuration
    The 7 documented public aliases (execute, read, edit, search, agent, web, todo) plus
    `vscode` (the VS Code chat-host tool set, harmlessly ignored on non-VS-Code surfaces
    per the documented "All unrecognized tool names are ignored" rule) form the
    `standard` profile. Reviewers/auditors get the narrower `read-only` profile.
    """
    require_contains(
        SKILL_ROOT / "references" / "platforms.md",
        (
            "Copilot CLI Standard Tool Profiles",
            "[vscode, execute, read, agent, edit, search, todo]",
            "`standard`",
            "`read-only`",
            "`runner`",
            "`research`",
            "`inherit`",
            "Role → Profile mapping",
            "VS Code chat-host tool set",
            "All unrecognized tool names are ignored",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "vscode",
            "Copilot CLI Standard Tool Profiles",
            "Apply the [Copilot CLI Standard Tool Profiles]",
            "Read-only reviewer",
            "tools: [read, search]",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.agent.md.template",
        (
            "tools: [vscode, execute, read, agent, edit, search, todo]",
            "agents-system-setup:tools-profile: standard",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        (
            "Copilot CLI Standard Tool Profiles",
            "[vscode, execute, read, agent, edit, search, todo]",
            "[read, search]",
            "[execute, read, search, todo]",
            "[read, search, web, todo]",
            "agents-system-setup:tools-profile: {{TOOLS_PROFILE}}",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "interview.md",
        (
            "9c. Copilot CLI Tool Profile",
            "copilot_tools_profile",
            "Standard profile",
            "[vscode, execute, read, agent, edit, search, todo]",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Copilot CLI Standard Tool Profiles",
            "[vscode, execute, read, agent, edit, search, todo]",
            "agents-system-setup:tools-profile",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "replication.md",
        (
            "Copilot CLI tool fill rule",
            "[vscode, execute, read, agent, edit, search, todo]",
            "vscode_host",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "runtime-updates.md",
        (
            "vscode",
            "Standard Tool Profile",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Copilot CLI tools profile",
        ),
    )

    # Warn-only: orchestrator.agent.md.template's tools list must contain `agent`
    # (orchestrator needs to delegate). Subagent template's role-aware comment must
    # NOT grant `agent` to read-only or runner profiles (least privilege).
    orch_text = (SKILL_ROOT / "assets" / "orchestrator.agent.md.template").read_text(encoding="utf-8")
    if "tools: [vscode, execute, read, agent, edit, search, todo]" not in orch_text:
        err("orchestrator.agent.md.template: missing standard tools line "
            "`tools: [vscode, execute, read, agent, edit, search, todo]`")
    if ", agent," not in orch_text and "agent," not in orch_text and ", agent]" not in orch_text:
        err("orchestrator.agent.md.template: orchestrator needs `agent` in its tools to delegate")

    for rel in (
        "references/agent-format.md",
        "assets/subagent.agent.md.template",
        "references/platforms.md",
        "references/replication.md",
    ):
        path = SKILL_ROOT / rel
        require_not_contains(
            path,
            (
                "[read, search, execute]",
                "[read, execute, search]",
                "read-only → tools: [read, search, execute]",
            ),
        )


def check_learning_memory_policy() -> None:
    """Keep the generated memory and reinforcement-learning loop intact."""
    require_contains(
        SKILL_ROOT / "references" / "learning-memory.md",
        (
            "Memory and Learning System",
            "Learning Check contract",
            "overwrite requires orchestrator approval",
            "no secrets or raw credentials",
            "Sensitive new learnings require orchestrator and security-owner approval",
            "Learning Check is still emitted and always returns `none`",
            "Operational ledger",
            "Optional hook/script support",
            "Learning Index",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "learnings.md.template",
        (
            "Curated agent memory",
            "not an operational log",
            "agents-system-setup:learning-memory:start",
            "No secrets or raw credentials",
            "Updates or overwrites require orchestrator approval",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "Memory & Learning System",
            "{{LEARNING_MEMORY_PROFILE}}",
            "{{LEARNING_MEMORY_OWNER}}",
            "{{LEARNING_MEMORY_PATH}}",
            "Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>",
            "overwrite requires orchestrator approval",
            "no secrets or raw credentials",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "GEMINI.md.template",
        (
            "Memory & Learning",
            "Learning Check before done",
            "Do not store secrets or raw credentials",
        ),
    )
    for rel in (
        "orchestrator.agent.md.template",
        "orchestrator.claude.md.template",
        "orchestrator.opencode.md.template",
    ):
        require_contains(
            SKILL_ROOT / "assets" / rel,
            (
                "Reflect & Learn",
                "Learning Check",
                "overwrite",
                "Sensitive new learnings require orchestrator and security-owner approval",
                "Never store secrets or raw credentials",
            ),
        )
    for rel in (
        "subagent.agent.md.template",
        "subagent.claude.md.template",
        "subagent.opencode.md.template",
        "subagent.gemini.md.template",
    ):
        require_contains(
            SKILL_ROOT / "assets" / rel,
            (
                "## Learning Check",
                "Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>",
                "orchestrator approval",
                "Never store secrets or raw credentials",
            ),
        )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "Learning Check:",
            "Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>",
            "orchestrator approval",
            "Never store secrets or raw credentials",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Learning memory is approval-safe",
            "Phase 1.10 — Memory & Learning Profile",
            "Memory & Learning plan",
            "Memory & Learning System",
            "overwrite requires orchestrator approval",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "interview.md",
        (
            "11i. Memory & Learning profile",
            "learning_memory_profile",
            "learning_gate_strength",
            "overwrite requires orchestrator approval",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "context-optimization.md",
        (
            "Memory & learning files",
            "Learning Index",
            "learning-check",
            "Memory & Learning System",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "local-tracking.md",
        (
            ".agents-system-setup/memory/",
            ".agents-system-setup/learnings.jsonl",
            "docs/agents/learnings.md",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Learning memory",
            "Learning check",
            "Learning updates",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "replication.md",
        (
            "Memory & Learning preservation",
            "learning-memory.md",
            "overwrite requires orchestrator approval",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "runtime-updates.md",
        (
            "Generated memory is artifact policy",
            "Memory & Learning System",
        ),
    )
    require_contains(
        REPO / "README.md",
        (
            "Memory & Learning System",
            "Learning Check",
        ),
    )
    require_contains(
        REPO / "CHANGELOG.md",
        (
            "Memory & Learning System",
            "Learning Check",
            "overwrite requires orchestrator approval",
        ),
    )

    for agent_dir in (
        REPO / ".github" / "agents",
        REPO / ".claude" / "agents",
        REPO / ".opencode" / "agents",
        REPO / ".codex" / "agents",
        REPO / ".gemini" / "agents",
    ):
        if not agent_dir.exists():
            continue
        for md in agent_dir.rglob("*.md"):
            name = md.name.lower()
            if "learning" in name or "log" in name or "ledger" in name:
                warn(f"{md.relative_to(REPO).as_posix()}: memory/log Markdown inside runtime agents directory may be parsed as an agent")


# ---------- main ----------

def main() -> int:
    print(f"Validating {REPO} …")
    check_manifests()
    check_schema_files()
    check_frontmatter_files()
    check_encoding()
    check_internal_links()
    check_codex_toml_agents()
    check_gemini_markdown_agents()
    check_opencode_markdown_agents()
    check_claude_plugin_agent_fields()
    check_replication_ledger()
    check_governance_baseline()
    check_mcp_approval_gate()
    check_central_mcp_approval_evidence()
    check_optional_placeholder_leaks()
    check_optional_placeholder_table()
    check_mcp_secret_shape()
    check_context_optimization()
    check_local_tracking_policy()
    check_plan_handoff_policy()
    check_codex_cli_app_compatibility()
    check_runtime_update_policy()
    check_runtime_invocation_policy()
    check_copilot_tool_profile()
    check_learning_memory_policy()

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
