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
  19. Human-input/question tooling is provider-specific and non-terminating
  20. Self-update preflight is safe, fast-forward-only, and config-silent
  21. Generated content-quality / anti-slop review is universal, compact,
       read-only by default, and provider-schema safe
  22. Main-to-subagent prompt handoff guidance is structured, compact,
       provider-neutral, and schema-safe

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
            else:
                named_allows = [
                    name
                    for name, action in task_permission.items()
                    if name != "*" and action == "allow"
                ]
                skip_marker = "agents-system-setup:permission-task-roster: skipped" in frontmatter_body
                if not named_allows and not skip_marker:
                    warn(f"{rel}: OpenCode primary `permission.task` has no named subagent allows; add roster allows or the skipped-roster marker")
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


# ---------- 11b: operational state directory artifact-free ----------

OPERATIONAL_STATE_DIR = ".agents-system-setup"
OPERATIONAL_STATE_FORBIDDEN_SUBTREES = (
    "agents",
    "skills",
    "hooks",
    "commands",
    "prompts",
    "plugins",
)


def check_operational_state_artifacts() -> None:
    """`.agents-system-setup/` is operational state only. Runtime artifact
    subtrees (`agents/`, `skills/`, `hooks/`, `commands/`, `prompts/`,
    `plugins/`) inside it are silently inert and indicate a misroute that
    must go through misplaced-artifacts-migration.
    """
    state_root = REPO / OPERATIONAL_STATE_DIR
    if not state_root.is_dir():
        return
    for entry in state_root.iterdir():
        if not entry.is_dir():
            continue
        if entry.name in OPERATIONAL_STATE_FORBIDDEN_SUBTREES:
            rel = entry.relative_to(REPO).as_posix()
            err(
                f"{rel}: runtime artifact subtree inside `.agents-system-setup/` "
                f"is silently inert. Move contents to the platform-standard path "
                f"and record the migration in `.agents-system-setup/migration.jsonl` "
                f"(see references/misplaced-artifacts-migration.md)."
            )


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


def _read_text_for_policy(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        err(f"{path.relative_to(REPO).as_posix()}: required governance file is missing")
    except UnicodeDecodeError:
        err(f"{path.relative_to(REPO).as_posix()}: not valid UTF-8")
    return None


def _skill_policy_paths() -> list[Path]:
    paths = [SKILL_ROOT / "SKILL.md"]
    paths.extend(sorted((SKILL_ROOT / "references").glob("*.md")))
    paths.extend(
        p
        for p in sorted((SKILL_ROOT / "assets").rglob("*"))
        if p.is_file()
    )
    return paths


def _aggregate_policy_text(paths: list[Path]) -> str:
    chunks: list[str] = []
    for path in paths:
        text = _read_text_for_policy(path)
        if text is None:
            continue
        rel = path.relative_to(REPO).as_posix()
        chunks.append(f"\n--- {rel} ---\n{text}")
    return "\n".join(chunks)


def _require_aggregate_marker(label: str, text: str, marker: str, *, case_sensitive: bool = True) -> None:
    haystack = text if case_sensitive else text.casefold()
    needle = marker if case_sensitive else marker.casefold()
    if needle not in haystack:
        err(f"{label}: missing required governance marker `{marker}`")


def _require_aggregate_pattern(label: str, text: str, pattern: str) -> None:
    if not re.search(pattern, text, re.MULTILINE | re.DOTALL):
        err(f"{label}: missing required governance pattern `{pattern}`")


def _iter_policy_lines(paths: list[Path]):
    for path in paths:
        text = _read_text_for_policy(path)
        if text is None:
            continue
        rel = path.relative_to(REPO).as_posix()
        in_fence = False
        for line_no, line in enumerate(text.splitlines(), start=1):
            if re.match(r"^\s*```", line):
                in_fence = not in_fence
            yield path, rel, line_no, line, in_fence


def _frontmatter_tools(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip().strip("'\"") for part in re.split(r"[, \t]+", value) if part.strip()]
    if isinstance(value, list):
        return [str(part).strip().strip("'\"") for part in value]
    return []


def _has_negative_context(line: str) -> bool:
    return bool(
        re.search(
            r"\b(no|not|never|without|avoid|forbid|forbidden|unsupported|"
            r"anti-pattern|pitfall|does not exist|there is no|do not|don't|must not)\b",
            line,
            re.IGNORECASE,
        )
    )


def _strip_toml_triple_strings(text: str) -> str:
    return re.sub(r'(?s)""".*?"""|\'\'\'.*?\'\'\'', '""', text)


def check_human_input_protocol() -> None:
    """Guard provider-specific question tools and subagent question_request flow."""
    policy_paths = _skill_policy_paths()
    policy_text = _aggregate_policy_text(policy_paths)
    label = "human-input protocol"

    for marker in (
        "Human Input / Question Tool Matrix",
        "question_request",
        "AskUserQuestion",
        "request_user_input",
        "--no-ask-user",
        "ask_user",
        "provider-native",
    ):
        _require_aggregate_marker(label, policy_text, marker)
    _require_aggregate_marker(label, policy_text, "non-terminating", case_sensitive=False)
    _require_aggregate_pattern(
        label,
        policy_text,
        r"permission:\s*(?:\{\s*question\s*:\s*allow\s*\}|\n\s+question:\s*allow\b)",
    )
    for path in (
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "references" / "handoff.md",
    ):
        rel = path.relative_to(REPO).as_posix()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "clarification_request" in line and "legacy" not in line.casefold() and "superseded" not in line.casefold():
                err(f"{rel}:{line_no}: use `question_request` for current human-input flow; `clarification_request` is legacy-only")

    # Copilot generated tool profiles/templates must never include ask_user.
    copilot_paths = [
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "references" / "platforms.md",
        SKILL_ROOT / "references" / "agent-format.md",
        SKILL_ROOT / "references" / "replication.md",
        SKILL_ROOT / "references" / "interview.md",
        SKILL_ROOT / "references" / "runtime-updates.md",
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
    ]
    for path, rel, line_no, line, _ in _iter_policy_lines(copilot_paths):
        gemini_context = "gemini" in line.casefold() or path.name in {"GEMINI.md.template", "subagent.gemini.md.template"}
        if not gemini_context and re.search(r"\btools\s*:\s*\[[^\]\n]*\bask_user\b", line, re.IGNORECASE):
            err(f"{rel}:{line_no}: Copilot generated `tools:` profiles must not include `ask_user`")
        if path.suffix == ".md" and ".github" in path.parts and "agents" in path.parts:
            split = split_frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
            if split is not None:
                try:
                    fm = parse_yaml_document(split[0])
                except Exception:
                    fm = {}
                if isinstance(fm, dict) and any(tool == "ask_user" for tool in _frontmatter_tools(fm.get("tools"))):
                    err(f"{rel}: Copilot custom-agent frontmatter `tools:` must not include `ask_user`")

    # Claude question tooling must be AskUserQuestion, never other runtimes' names.
    claude_paths = [
        SKILL_ROOT / "references" / "human-input.md",
        SKILL_ROOT / "references" / "platforms.md",
        SKILL_ROOT / "references" / "agent-format.md",
        SKILL_ROOT / "references" / "runtime-updates.md",
        SKILL_ROOT / "assets" / "subagent.claude.md.template",
    ]
    _require_aggregate_marker("Claude human-input tooling", _aggregate_policy_text(claude_paths), "AskUserQuestion")
    _require_aggregate_marker("Claude background human-input fallback", _aggregate_policy_text(claude_paths), "background: true")
    for path, rel, line_no, line, _ in _iter_policy_lines(claude_paths):
        claude_context = "claude" in rel.casefold() or re.search(r"\bClaude\b", line)
        if not claude_context:
            continue
        if _has_negative_context(line):
            continue
        if re.search(r"\btools\s*:\s*[^\n]*\b(ask_user|request_user_input)\b", line, re.IGNORECASE):
            err(f"{rel}:{line_no}: Claude `tools:` entries must use `AskUserQuestion`, not another runtime's question tool")
        if re.search(r"\btools\s*:\s*[^\n]*\bquestion\b", line, re.IGNORECASE) and "AskUserQuestion" not in line:
            err(f"{rel}:{line_no}: Claude question tooling must be `AskUserQuestion`, not `question`")
        split = split_frontmatter(path.read_text(encoding="utf-8", errors="ignore")) if path.suffix == ".md" else None
        if split is not None:
            try:
                fm = parse_yaml_document(split[0])
            except Exception:
                fm = {}
            if isinstance(fm, dict):
                lowered_tools = {tool.casefold() for tool in _frontmatter_tools(fm.get("tools"))}
                if lowered_tools & {"ask_user", "question", "request_user_input"}:
                    err(f"{rel}: Claude frontmatter `tools:` must use `AskUserQuestion` for question tooling")
                if fm.get("background") is True and "askuserquestion" in lowered_tools:
                    err(f"{rel}: Claude background agents must return `question_request`, not rely on `AskUserQuestion`")

    # OpenCode must emit nested permission syntax, not a dotted config key.
    opencode_paths = [
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "references" / "human-input.md",
        SKILL_ROOT / "references" / "platforms.md",
        SKILL_ROOT / "references" / "agent-format.md",
        SKILL_ROOT / "references" / "runtime-updates.md",
        SKILL_ROOT / "assets" / "subagent.opencode.md.template",
    ]
    for path, rel, line_no, line, in_fence in _iter_policy_lines(opencode_paths):
        if "permission.question" not in line:
            continue
        if in_fence or not ("literal" in line.casefold() or "shorthand" in line.casefold() or _has_negative_context(line)):
            err(f"{rel}:{line_no}: OpenCode must not emit literal `permission.question`; use nested `permission: {{ question: allow }}`")
        if path.suffix == ".md":
            split = split_frontmatter(path.read_text(encoding="utf-8", errors="ignore"))
            if split is not None:
                try:
                    fm = parse_yaml_document(split[0])
                except Exception:
                    fm = {}
                if isinstance(fm, dict) and "permission.question" in fm:
                    err(f"{rel}: OpenCode frontmatter must not use literal `permission.question`")

    # Codex TOML supports request_user_input only in Plan mode prose, not agent fields.
    codex_toml_paths = [SKILL_ROOT / "assets" / "subagent.codex.toml.template"]
    codex_toml_paths.extend(
        p for p in REPO.rglob("*.toml") if ".codex" in p.parts and ".git" not in p.parts
    )
    for path in codex_toml_paths:
        text = _read_text_for_policy(path)
        if text is None:
            continue
        rel = path.relative_to(REPO).as_posix()
        structural = _strip_toml_triple_strings(text)
        for line_no, line in enumerate(structural.splitlines(), start=1):
            if line.lstrip().startswith("#"):
                continue
            if re.match(r"\s*(ask_user|question|request_user_input)\s*=", line):
                err(f"{rel}:{line_no}: Codex TOML must not define top-level human-input field `{line.strip().split('=', 1)[0].strip()}`")
            if re.match(r"\s*\[\[?\s*(ask_user|question|request_user_input)(?:[.\]\s])", line):
                err(f"{rel}:{line_no}: Codex TOML must not define human-input tables; keep question tooling in developer_instructions prose")

    # Gemini uses ask_user for human input and activate_skill / /skills for skills.
    gemini_paths = [
        SKILL_ROOT / "references" / "agent-format.md",
        SKILL_ROOT / "references" / "platforms.md",
        SKILL_ROOT / "references" / "runtime-updates.md",
        SKILL_ROOT / "references" / "skill-format.md",
        SKILL_ROOT / "references" / "marketplaces.md",
        SKILL_ROOT / "assets" / "GEMINI.md.template",
        SKILL_ROOT / "assets" / "subagent.gemini.md.template",
    ]
    gemini_text = _aggregate_policy_text(gemini_paths)
    _require_aggregate_marker("Gemini human-input tooling", gemini_text, "ask_user")
    _require_aggregate_marker("Gemini skill activation", gemini_text, "activate_skill")
    _require_aggregate_marker("Gemini skill management", gemini_text, "/skills")
    for path, rel, line_no, line, _ in _iter_policy_lines(gemini_paths):
        gemini_context = (
            path.name in {"GEMINI.md.template", "subagent.gemini.md.template"}
            or "gemini" in line.casefold()
            or ".gemini" in line.casefold()
            or "GEMINI.md" in line
        )
        if not gemini_context:
            continue
        if re.search(r"\$(?:skill|<skill>)|/<skill>", line) and not _has_negative_context(line):
            err(f"{rel}:{line_no}: Gemini artifacts must not document `$skill` or `/<skill>` invocation; use `activate_skill` and `/skills` guidance")
        if "ask_user" in line and not re.search(r"human[- ]input|question|interactive|allow", line, re.IGNORECASE):
            err(f"{rel}:{line_no}: Gemini `ask_user` mentions must be limited to human-input/question guidance")


def check_self_update_preflight_policy() -> None:
    """Keep self-update safe: clean fast-forward only, no silent config edits."""
    policy_paths = [
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "references" / "self-update-preflight.md",
        SKILL_ROOT / "references" / "runtime-updates.md",
        SKILL_ROOT / "references" / "marketplaces.md",
        SKILL_ROOT / "references" / "wrapup.md",
        SKILL_ROOT / "assets" / "AGENTS.md.template",
    ]
    policy_text = _aggregate_policy_text(policy_paths)
    label = "self-update preflight policy"
    for marker in (
        "Phase -1 — Self-Update Preflight",
        "AGENTS_SYSTEM_SETUP_HOME",
        "git status --porcelain=v1",
        "git fetch --prune",
        "git merge --ff-only",
        "dirty",
        "missing",
        "divergent",
        "install mode",
        "ask_user",
        "copilot plugin update agents-system-setup",
        "/plugin marketplace update",
        "/reload-plugins",
        "opencode plugin <module>",
        "codex plugin marketplace upgrade",
        "gemini extensions update --all",
    ):
        _require_aggregate_marker(label, policy_text, marker)
    _require_aggregate_pattern(
        label,
        policy_text,
        r"(?:must not|Never|Do not)\s+update MCP/plugin config silently|no MCP/plugin/runtime config changed outside the normal approval gates",
    )

    destructive_patterns = (
        r"\bgit\s+reset\s+--hard\b",
        r"\bgit\s+clean\b",
        r"\bgit\s+stash\b",
        r"\bgit\s+pull\s+--rebase\b",
        r"\bgit\s+pull\b[^\n]*(?:--force|-f)\b",
        r"\bgit\s+fetch\b[^\n]*(?:--force|-f)\b",
    )
    for _, rel, line_no, line, _ in _iter_policy_lines(policy_paths):
        if "opencode plugin install" in line and not _has_negative_context(line):
            err(f"{rel}:{line_no}: self-update docs must not use unqualified `opencode plugin install`; use `opencode plugin <module>` or package/Git update guidance")
        for pattern in destructive_patterns:
            if re.search(pattern, line):
                err(f"{rel}:{line_no}: destructive self-update snippet is forbidden (`{line.strip()}`)")


def check_governance_baseline() -> None:
    """The skill must keep security, audit, architecture, and design-pattern
    governance as first-class generated outputs, not optional wrap-up notes.
    """
    required_files = [
        SKILL_ROOT / "references" / "security-audit-architecture.md",
        SKILL_ROOT / "assets" / "AGENTS.md.template",
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
            "## Orchestration Operating Model",
            "Security & Audit Matrix",
            "Threat Model",
            "Architecture & Design Pattern Decisions",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
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
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            ".mcp.json",
            "opencode.json",
            "Route security-sensitive work",
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

def check_requirements_triage_policy() -> None:
    """Keep the generated requirements-triage role useful and read-mostly."""
    require_contains(
        SKILL_ROOT / "references" / "topology.md",
        (
            "requirements-triage",
            "Requirements Triage Sizing Rule",
            "default-on recommended",
            "read-only",
            "question_request",
            "orchestrator owns user-facing questions",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Requirements triage is default-on recommended",
            "Phase 1.11 — Requirements Triage",
            "requirements_triage_status",
            "separate",
            "merged",
            "skipped",
            "question_request",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Requirements Triage",
            "{{REQUIREMENTS_TRIAGE_STATUS}}",
            "{{REQUIREMENTS_TRIAGE_OWNER}}",
            "{{REQUIREMENTS_TRIAGE_EVIDENCE}}",
            "requirements-triage",
            "question_request",
            "read-only by default",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
            "Requirements triage handoff",
            "triage_source",
            "triage_status",
            "Intent summary",
            "Task type",
            "Recommended routing",
            "Triage:",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Requirements triage",
            "triage_question_requests",
            "intake brief",
            "Triage status",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "context-optimization.md",
        (
            "Requirements triage output",
            "requirements-triage",
            "short-form intake brief",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "Requirements Triage",
            "@requirements-triage",
            "triage: skipped",
            "read-mostly and advisory",
            "I own final decisions and approval gates",
        ),
    )

    topology = (SKILL_ROOT / "references" / "topology.md").read_text(encoding="utf-8")
    triage_lines = [line for line in topology.splitlines() if "requirements-triage" in line]
    if not triage_lines or not any("read-only" in line for line in triage_lines):
        err("references/topology.md: requirements-triage must be read-only by default")
    forbidden = re.compile(
        r"requirements-triage[^\n]*(?:mcp\s*(?:write|config)|runtime config|release metadata|full file edit|edit-capable)",
        re.IGNORECASE,
    )
    for path in (
        SKILL_ROOT / "references" / "topology.md",
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        SKILL_ROOT / "SKILL.md",
    ):
        rel = path.relative_to(REPO).as_posix()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if forbidden.search(line) and not (_has_negative_context(line) or "cannot" in line.casefold()):
                err(f"{rel}:{line_no}: requirements-triage must not receive broad write/config/release ownership")


def check_output_quality_policy() -> None:
    """Keep generated anti-slop review universal, compact, and read-only."""
    require_contains(
        SKILL_ROOT / "references" / "content-quality.md",
        (
            "Content Quality / Anti-Slop Guardrails",
            "agent-quality-curator",
            "anti-slop-reviewer",
            "Signal taxonomy",
            "generic-description",
            "empty-rationale",
            "padding-repetition",
            "slop-completeness",
            "invented-attribution",
            "context-bloat",
            "vague-ownership",
            "unsupported-assertion",
            "silent-gate-gap",
            "prompt-hygiene-risk",
            "Content quality: <ok|warn|fail|n/a>",
            "Quality ledger policy",
            "Do not create `.agents-system-setup/quality-baseline.jsonl` by default",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "topology.md",
        (
            "agent-quality-curator",
            "Content Quality Sizing Rule",
            "universal recommended",
            "read-only",
            "Content quality: ok|warn|fail|n/a",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Content quality is universal",
            "Phase 1.12 — Content Quality Review",
            "content_quality_curator",
            "agent-quality-curator",
            "Content quality: ok|warn|fail|n/a",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Content Quality / Anti-Slop Review",
            "{{CONTENT_QUALITY_STATUS}}",
            "{{CONTENT_QUALITY_CURATOR}}",
            "{{CONTENT_QUALITY_OWNER}}",
            "{{CONTENT_QUALITY_SIGNALS}}",
            "{{CONTENT_QUALITY_REFERENCE}}",
            "agent-quality-curator",
            "Content quality: ok|warn|fail|n/a",
            "Before final output when generated agent-system prose changes",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "Content Quality Review",
            "@agent-quality-curator",
            "Content quality: ok|warn|fail|n/a",
            "read-only and advisory",
            "I own final decisions and approval gates",
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
                "Content quality: ok | warn | fail | n/a; signals=<list|none>",
            ),
        )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "Content quality: ok | warn | fail | n/a; signals=<list|none>",
            "Do not add unsupported TOML question fields or `memory` fields",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "GEMINI.md.template",
        (
            "Content Quality / Anti-Slop Review",
            "Content quality before final output",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
            "content_quality_status",
            "content_quality_curator",
            "content_quality_signals",
            "content-quality-review",
            "Content quality: ok | warn | fail | n/a; signals=<list|none>",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "context-optimization.md",
        (
            "Content quality review",
            "content-quality-review",
            "compact `Content quality` status",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Content quality: <ok|warn|fail|n/a>",
            "Content-quality findings",
            "Full content-quality signal list",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "{{CONTENT_QUALITY_STATUS}}",
            "{{CONTENT_QUALITY_CURATOR}}",
            "{{CONTENT_QUALITY_OWNER}}",
            "{{CONTENT_QUALITY_SIGNALS}}",
            "{{CONTENT_QUALITY_REFERENCE}}",
            "do not emit unsupported fields",
        ),
    )

    forbidden = re.compile(
        r"agent-quality-curator[^\n]*(?:mcp\s*(?:write|config)|runtime config|release metadata|full file edit|edit-capable|broad write|final approval)",
        re.IGNORECASE,
    )
    for path in (
        SKILL_ROOT / "references" / "topology.md",
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        SKILL_ROOT / "SKILL.md",
    ):
        rel = path.relative_to(REPO).as_posix()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if forbidden.search(line) and not _has_negative_context(line):
                err(f"{rel}:{line_no}: agent-quality-curator must not receive broad write/config/release/final-approval ownership")

    codex_template = (SKILL_ROOT / "assets" / "subagent.codex.toml.template").read_text(encoding="utf-8")
    structural_toml = _strip_toml_triple_strings(codex_template)
    if re.search(r"(?m)^\s*(?:content_quality|ask_user|question|request_user_input|memory)\s*=", structural_toml):
        err("assets/subagent.codex.toml.template: content-quality/question/memory must stay in developer_instructions, not TOML fields")


def check_security_team_policy() -> None:
    """Dedicated security-team generation must be explicit, source-backed, and
    read-mostly by default.
    """
    security_team_ref = SKILL_ROOT / "references" / "security-team.md"
    if not security_team_ref.is_file():
        err("plugins/agents-system-setup/skills/agents-system-setup/references/security-team.md: required security-team reference is missing")
        return

    require_contains(
        security_team_ref,
        (
            "Security Team Generation",
            "Source-backed model",
            "OWASP SAMM",
            "NIST SSDF",
            "OWASP Vulnerability Disclosure Cheat Sheet",
            "CISA Coordinated Vulnerability Disclosure",
            "FIRST CVSS",
            "Security team sizing",
            "Authorization and safety boundaries",
            "Evidence and output contract",
            "Do not copy",
            "proprietary",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Dedicated security teams are explicit",
            "Phase 1.8a — Security Team Scope",
            "security_team_depth",
            "security_team_scope",
            "authorization_scope",
            "Security team operating model",
            "remediation writes",
            "external scanning",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "interview.md",
        (
            "Security team / Bug hunting",
            "Security team depth",
            "security_team_depth",
            "Dedicated bug-hunting/security analysis team",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "topology.md",
        (
            "Security team / Bug hunting",
            "Security Team Sizing Rule",
            "vulnerability-researcher",
            "validation-reproducer",
            "attack-path-analyst",
            "remediation-verifier",
            "read-mostly by default",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "context-optimization.md",
        (
            "bug-hunting",
            "vulnerability-validation",
            "attack-path-analysis",
            "remediation-verification",
            "disclosure-triage",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
            "Security Analysis (security-team tasks only)",
            "authorization:",
            "counterevidence",
            "proof_gaps",
            "Security analysis: n/a | scope=",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "prompt-guidelines.md",
        (
            "Security-team handoff notes",
            "authorization scope",
            "counterevidence",
            "proof gaps",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "plugin-discovery.md",
        (
            "Security plugins require license/provenance",
            "codex-security",
            "Never mirror proprietary plugin prompts",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Security team:",
            "Security-team evidence",
            "Security-team findings",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "{{SECURITY_TEAM_DEPTH}}",
            "{{SECURITY_TEAM_OPERATING_MODEL}}",
            "Security-team placeholders",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "{{SECURITY_TEAM_DEPTH}}",
            "## Security Team Operating Model",
            "{{SECURITY_TEAM_OPERATING_MODEL}}",
            "`bug-hunting`",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "GEMINI.md.template",
        (
            "Security Team Operating Model",
            "Gemini subagents",
            "Security analysis",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "Security Team Scope",
            "Security Team Operating Model",
            "authorization scope",
            "read-mostly",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
            "proof gaps",
        ),
    )
    for rel in (
        "subagent.agent.md.template",
        "subagent.claude.md.template",
        "subagent.opencode.md.template",
        "subagent.gemini.md.template",
        "subagent.codex.toml.template",
    ):
        require_contains(
            SKILL_ROOT / "assets" / rel,
            (
                "Security analysis: n/a | scope=",
                "authorization=",
                "validation=",
                "proof_gaps=",
            ),
        )

    forbidden = re.compile(
        r"(?:vulnerability-researcher|validation-reproducer|attack-path-analyst|bug-bounty-triage|compliance-auditor)[^\n]*(?:full file edit|edit-capable|broad write|\*\s*:\s*allow)",
        re.IGNORECASE,
    )
    for path in (
        SKILL_ROOT / "references" / "topology.md",
        SKILL_ROOT / "references" / "security-team.md",
        SKILL_ROOT / "assets" / "AGENTS.md.template",
    ):
        rel = path.relative_to(REPO).as_posix()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if forbidden.search(line) and not _has_negative_context(line):
                err(f"{rel}:{line_no}: security-team research roles must not default to broad write permissions")


def check_cwd_reconnaissance_policy() -> None:
    """Phase 1 must run a safe-readonly cwd reconnaissance with privacy
    guardrails, render a Reconnaissance Card, and ask the user to confirm
    or correct it before continuing the interview.
    """
    recon_ref = SKILL_ROOT / "references" / "cwd-reconnaissance.md"
    if not recon_ref.is_file():
        err(f"{recon_ref.relative_to(REPO).as_posix()}: required cwd-reconnaissance reference is missing")
        return

    require_contains(
        recon_ref,
        (
            "CWD Project Reconnaissance",
            "safe-readonly",
            "Privacy guardrails",
            "No data file reads",
            "Magic-byte detection",
            "Secret redaction",
            "Reconnaissance Card schema",
            "project_kind_signals",
            "data_signals",
            "privacy_redactions",
            "User confirmation prompt",
            "Skip recon",
            # v1.2.0 purpose-first recon
            "Purpose-aware scoring",
            "Scoring rubric",
            "headline_purpose",
            "purpose_relevance",
            "Exploring fallback",
            "exploring",
            # v1.2.0 safety-critical semantics (not just scaffolding)
            "Never filter",
            "`high` \u2192 `med` \u2192 `low` \u2192 `n-a`",
            "normalize",
            "Improve-mode caveat",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Project recon",
            "cwd-reconnaissance",
            "Reconnaissance Card",
            "Privacy guardrails",
            # v1.2.0 purpose-first wiring in SKILL.md
            "Capture Purpose",
            "headline_purpose",
            "purpose-aware",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "interview.md",
        (
            "Recon pre-fill",
            "cwd reconnaissance card",
            # v1.2.0 purpose-first interview wiring
            "headline_purpose",
            "Capture headline purpose",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Recon:",
            "redactions=",
            # v1.2.0 purpose line in contract
            "Purpose:",
        ),
    )
    # Track regression-prevention for the specific secret-pattern names so
    # future edits cannot silently drop one.
    require_contains(
        recon_ref,
        (
            "AKIA[0-9A-Z]",
            "AWS_SECRET_ACCESS_KEY",
            "github_pat_",
            "sk-(?:ant-)?",
            "_authToken",
            "Authorization header",
            "\"private_key\"",
            "JWT triplet",
        ),
    )


def check_purpose_before_footprint_in_phase_0() -> None:
    """Assert that within Phase 0 of SKILL.md the headline purpose
    sub-step appears before the footprint detection sub-step. The
    section header itself ("Capture Purpose, Detect Footprint, Choose
    Mode") lists both words for readability, so the header line is
    excluded from the scan; only the body sub-steps are checked. This
    guards hard rule #32 (purpose-first wizard, v1.2.0) against
    accidental reordering during future edits.
    """
    skill_path = SKILL_ROOT / "SKILL.md"
    if not skill_path.is_file():
        err(f"{skill_path.relative_to(REPO).as_posix()}: SKILL.md is missing")
        return
    text = skill_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    phase0_start = None
    phase0_end = len(lines)
    for idx, line in enumerate(lines):
        if line.startswith("### Phase 0"):
            phase0_start = idx
        elif phase0_start is not None and line.startswith("### Phase "):
            phase0_end = idx
            break
    if phase0_start is None:
        err(f"{skill_path.relative_to(REPO).as_posix()}: missing '### Phase 0' section")
        return
    # Exclude the header line itself; only scan the body.
    body_lines = lines[phase0_start + 1 : phase0_end]
    body_lower = "\n".join(body_lines).lower()
    purpose_at = body_lower.find("purpose")
    footprint_at = body_lower.find("footprint")
    if purpose_at == -1:
        err(
            f"{skill_path.relative_to(REPO).as_posix()}: Phase 0 body must mention 'purpose' "
            "(hard rule #32 — purpose-first wizard)"
        )
        return
    if footprint_at == -1:
        warn(
            f"{skill_path.relative_to(REPO).as_posix()}: Phase 0 body does not mention "
            "'footprint'; verify the mode/detection step still exists"
        )
        return
    if purpose_at >= footprint_at:
        err(
            f"{skill_path.relative_to(REPO).as_posix()}: Phase 0 body mentions 'footprint' "
            "before 'purpose' (hard rule #32 requires purpose-first capture). "
            "Move the headline_purpose ask above the footprint detection step."
        )
        return
    # Additionally assert the exact sub-step ordering markers so the
    # purpose-first sub-step cannot regress without tripping validation.
    body_text = "\n".join(body_lines)
    sub0_at = body_text.find("Sub-step 0 — Capture headline purpose")
    sub1_at = body_text.find("Sub-step 1 — Detect footprint")
    if sub0_at == -1 or sub1_at == -1:
        err(
            f"{skill_path.relative_to(REPO).as_posix()}: Phase 0 must keep the canonical "
            "sub-step markers 'Sub-step 0 — Capture headline purpose' and "
            "'Sub-step 1 — Detect footprint' (v1.2.0 hard rule #32)"
        )
        return
    if sub0_at >= sub1_at:
        err(
            f"{skill_path.relative_to(REPO).as_posix()}: Phase 0 sub-step ordering is wrong; "
            "'Sub-step 0 — Capture headline purpose' must precede "
            "'Sub-step 1 — Detect footprint' (v1.2.0 hard rule #32)"
        )


def check_misplaced_artifacts_migration_policy() -> None:
    """Phase 1 detects and Phase 1.5 surfaces misplaced runtime artifacts
    found under `.agents-system-setup/`. The migration covers all six
    runtime artifact types with a per-artifact ask_user choice and an
    operational ledger at `.agents-system-setup/migration.jsonl`.
    """
    migration_ref = SKILL_ROOT / "references" / "misplaced-artifacts-migration.md"
    if not migration_ref.is_file():
        err(f"{migration_ref.relative_to(REPO).as_posix()}: required misplaced-artifacts-migration reference is missing")
        return

    require_contains(
        migration_ref,
        (
            "Misplaced Artifacts Migration",
            "Detection signals",
            ".agents-system-setup/agents/",
            ".agents-system-setup/skills/",
            ".agents-system-setup/hooks/",
            ".agents-system-setup/commands/",
            ".agents-system-setup/prompts/",
            ".agents-system-setup/plugins/",
            "Per-type, per-platform target mapping",
            "Migration choices",
            "File-based artifacts",
            "Config-embedded artifacts",
            "Move (Recommended)",
            "Copy and keep original with deprecation marker",
            "Leave with warning",
            "Convert manually",
            "Delete after explicit confirmation",
            "Deprecation marker rules",
            "Multi-runtime portability",
            "Skills are portable",
            "portable-manifest-sha256",
            "Backup directory naming",
            "migration_id",
            "external-symlink",
            "File-based migration procedure",
            "Migration ledger schema",
            ".agents-system-setup/migration.jsonl",
            ".agents-system-setup/.bak/",
            "digest_source",
            "digest_target",
            "Hook safety warning",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Operational state directory is artifact-free",
            "misplaced-artifacts-migration",
            "Misplaced artifacts",
            "migration.jsonl",
            "Writing runtime artifacts under `.agents-system-setup/`",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Path migration:",
            "moved=",
            "manual=",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "skill-format.md",
        (
            ".agents-system-setup/skills/",
            "misplaced-artifacts-migration",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            ".agents-system-setup/",
            "misplaced-artifacts-migration",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "platforms.md",
        (
            "Operational state directory",
            "misplaced-artifacts-migration",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "local-tracking.md",
        (
            "Operational state directory",
            "misplaced-artifacts-migration",
        ),
    )


def check_no_orchestrator_subagent_emission() -> None:
    """v1.3.0: the orchestrator role lives in AGENTS.md › Orchestration
    Operating Model and is read by the host CLI session. No runtime emits
    an orchestrator subagent file. The skill, references, validator, and
    misplaced-artifacts migration must all reflect this invariant.
    """
    # 1. The three orchestrator template files must NOT exist.
    forbidden_templates = (
        "orchestrator.agent.md.template",
        "orchestrator.claude.md.template",
        "orchestrator.opencode.md.template",
    )
    for name in forbidden_templates:
        path = SKILL_ROOT / "assets" / name
        if path.exists():
            err(
                f"{path.relative_to(REPO).as_posix()}: must not exist (v1.3.0 "
                "removed orchestrator subagent templates; orchestration lives in "
                "AGENTS.md › Orchestration Operating Model)"
            )

    # 2. SKILL.md must NOT reference orchestrator template files or
    # orchestrator subagent file paths in any prescriptive context.
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    for needle in forbidden_templates:
        if needle in skill:
            err(
                f"plugins/agents-system-setup/skills/agents-system-setup/SKILL.md: "
                f"contains banned reference `{needle}` (v1.3.0 hard rule #33; "
                "orchestrator lives in AGENTS.md)"
            )

    # 3. AGENTS.md.template must contain the new Orchestration Operating
    # Model section with all consolidated markers from the deleted templates.
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Orchestration Operating Model",
            "host CLI session",
            "routing alias for that host/root session",
            "### Role and Delegation Stance",
            "### Core Hard Rules",
            "### Required Minimum for Every Task Assignment",
            "### Subagent Routing",
            "Plan Handoff Contract",
            "Security & Audit Matrix",
            "Threat Model",
            "Architecture & Design Pattern Decisions",
            "MCP",
            "Reflect & Learn",
            "Content Quality Review",
            "@agent-quality-curator",
            "Security Team Scope",
            "Security Team Operating Model",
            "authorization scope",
            "Requirements Triage",
            "@requirements-triage",
            "triage: skipped",
            "I own final decisions and approval gates",
            "subtask slice",
            "Task assignment quality: ok | warn | fail",
            "agents-system-setup:wave-execution",
            "fan out",
            "parallel-safe",
            "wave",
        ),
    )

    # 4. SKILL.md must contain hard rule #33 and the orchestrator anti-pattern.
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "The orchestrator is the host CLI session, not a subagent file",
            "Never emit `orchestrator.agent.md`",
            "OpenCode's `permission.task` gate moves to `opencode.json`",
            "Emitting an `orchestrator` subagent file",
            "Codex CLI has never emitted an orchestrator TOML",
            "OpenCode root-session task gate",
        ),
    )

    # 5. SKILL.md Phase 4 must say orchestrator content lives in AGENTS.md.
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "never emit as a subagent file",
            "Orchestration Operating Model",
            "subagent files are for specialized roles only",
        ),
    )

    # 6. misplaced-artifacts-migration.md must document the orchestrator
    # deprecation choices.
    require_contains(
        SKILL_ROOT / "references" / "misplaced-artifacts-migration.md",
        (
            "Deprecated orchestrator subagent files",
            ".github/agents/orchestrator.agent.md",
            ".claude/agents/orchestrator.md",
            ".opencode/agents/orchestrator.md",
            ".gemini/agents/orchestrator.md",
            "Back up and delete (Recommended)",
            "Keep but mark deprecated",
            "Back up + report custom additions for manual review",
            "Skip",
            "orchestrator-deprecation-deleted",
            "orchestrator-deprecation-marked",
            "orchestrator-deprecation-reviewed",
            "orchestrator-deprecation-skipped",
            "has_custom_content",
            "permission.task` migration",
            "agents-system-setup:permission-task-approved",
        ),
    )

    # 7. topology.md must clarify @orchestrator is the host session.
    require_contains(
        SKILL_ROOT / "references" / "topology.md",
        (
            "The orchestrator is the host CLI session",
            "routing alias for that host/root session",
            "No runtime emits a separate `orchestrator.agent.md`",
            "Subagent files in the table below are for **specialized roles only**",
        ),
    )

    # 8. handoff.md per-runtime handoff surfaces table must show
    # orchestrator role lives in AGENTS.md for every runtime.
    handoff_text = (SKILL_ROOT / "references" / "handoff.md").read_text(encoding="utf-8")
    for runtime_marker in (
        "Orchestrator role: `AGENTS.md` › Orchestration Operating Model",
        "No `orchestrator.agent.md` file is emitted",
        "No `.claude/agents/orchestrator.md` file is emitted",
        "No `.opencode/agents/orchestrator.md` file is emitted",
        "No `.gemini/agents/orchestrator.md` file is emitted",
        "No `.codex/agents/orchestrator.toml` is emitted",
    ):
        if runtime_marker not in handoff_text:
            err(
                f"plugins/agents-system-setup/skills/agents-system-setup/references/handoff.md: "
                f"missing v1.3.0 marker `{runtime_marker}`"
            )

    # 9. agent-format.md must mark AGENTS.md as canonical orchestrator
    # location and route OpenCode permission.task to opencode.json.
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "Never emit a `.codex/agents/orchestrator.toml`",
            "canonical pattern for every supported runtime as of v1.3.0",
            "the root-session `permission.task` subagent-gating lives in `opencode.json`",
        ),
    )

    # 10. replication.md must classify orchestrator as RootRoleIR.
    require_contains(
        SKILL_ROOT / "references" / "replication.md",
        (
            "Orchestrator role is RootRoleIR, not AgentIR",
            "merged into the target's `AGENTS.md` › Orchestration Operating Model",
            "no target emits a `*/orchestrator.*` agent file",
            "Never emit `.codex/agents/orchestrator.toml`",
        ),
    )

    # 11. runtime-updates.md must record the orchestrator elimination finding.
    require_contains(
        SKILL_ROOT / "references" / "runtime-updates.md",
        (
            "Orchestrator elimination",
            "v1.3.0",
            "host CLI session",
        ),
    )

    # 12. Stale conceptual references: flag prescriptive wording that still
    # implies an orchestrator file. The check is line-scoped and excludes
    # negative/historical context (e.g., "never emit ...", "no longer ...").
    stale_patterns = (
        re.compile(r"\bemit\s+orchestrator(?:\s+(?:file|template|subagent))?\b", re.IGNORECASE),
        re.compile(r"\borchestrator\s+(?:agent\s+)?file\b", re.IGNORECASE),
        re.compile(r"\borchestrator\s*\+\s*N\s+subagents\b", re.IGNORECASE),
        re.compile(r"\borchestrator\s*/\s*subagents\b", re.IGNORECASE),
        re.compile(r"\borchestrator\s+templates?\b", re.IGNORECASE),
        re.compile(r"\bgenerated\s+orchestrators?\b", re.IGNORECASE),
    )
    scan_paths = [
        REPO / "README.md",
        REPO / "DESIGN.md",
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        SKILL_ROOT / "assets" / "GEMINI.md.template",
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        SKILL_ROOT / "assets" / "subagent.claude.md.template",
        SKILL_ROOT / "assets" / "subagent.opencode.md.template",
        SKILL_ROOT / "assets" / "subagent.gemini.md.template",
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
    ]
    # Exclude CHANGELOG.md: historical entries are by design and must not
    # be rewritten retroactively. The CHANGELOG-1.3.0 entry itself is
    # written with the new terminology; older entries describe what each
    # past release did at the time.
    scan_paths.extend(sorted((SKILL_ROOT / "references").glob("*.md")))
    for path in scan_paths:
        if not path.is_file():
            continue
        rel = path.relative_to(REPO).as_posix()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for pat in stale_patterns:
                if pat.search(line) and not _has_negative_context(line):
                    err(
                        f"{rel}:{line_no}: stale conceptual reference suggests "
                        f"an orchestrator subagent file still exists: `{line.strip()[:120]}`"
                    )

    # 13. output-contract.md "Try it" Copilot example must tell users to
    # describe the task directly to the host session, never to type
    # `@orchestrator` as an invokable agent (regression guard for the v1.8.1
    # fix; the host CLI session is the orchestrator per hard rule #33).
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "describe the task directly to the session",
            "there is no `@orchestrator` agent to type",
        ),
    )
    require_not_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "> @orchestrator",
            "`@orchestrator <task>`",
        ),
    )


def check_pointer_files_to_agents_md() -> None:
    """When Claude Code or Gemini CLI are targets, the pointer files
    (`CLAUDE.md`, `GEMINI.md`) must surface `AGENTS.md` so the host root
    session reads the Orchestration Operating Model. This check verifies
    the templates and link-helper scripts; per-project pointer files are
    runtime-verified by the generated scripts at Phase 4.
    """
    # GEMINI.md.template must point at AGENTS.md.
    require_contains(
        SKILL_ROOT / "assets" / "GEMINI.md.template",
        (
            "AGENTS.md",
        ),
    )

    # SKILL.md must reference the project-memory linking step for Claude
    # (and document Gemini's pointer/sync copy).
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Project-memory linking",
            "link-project-memory.sh",
            "link-project-memory.ps1",
            "GEMINI.md",
            "CLAUDE.md",
        ),
    )

    # Linker scripts must exist when documented (CI smoke tests verify
    # cross-OS execution; this is a presence check).
    for rel in (
        "plugins/agents-system-setup/skills/agents-system-setup/scripts/link-project-memory.sh",
        "plugins/agents-system-setup/skills/agents-system-setup/scripts/link-project-memory.ps1",
    ):
        if not (REPO / rel).is_file():
            err(f"{rel}: required project-memory linker script is missing")


def check_opencode_root_task_gate() -> None:
    """When OpenCode is among the selected runtimes, the host-root
    `permission.task` gate must live in `opencode.json` (since v1.3.0 no
    `orchestrator.opencode.md` is emitted). This check enforces:

    1. SKILL.md describes the gate relocation with a separate config
       approval gate (not the MCP gate).
    2. `references/misplaced-artifacts-migration.md` documents extracting
       and preserving existing user customizations rather than replacing
       them with the generic template.
    3. Any `opencode.json` file actually present in the repo (samples,
       fixtures, or generated reference output) carries an explicit
       `agent.<root>.permission.task` gate with `"*"` set to `"deny"` or
       `"ask"`, never `"allow"`.
    """
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "OpenCode root-session task gate",
            "opencode.json",
            "agent.<root>.permission.task",
            "separate config approval gate",
            "opencode_task_gate: declined",
            "fan-out not permission-constrained",
        ),
    )

    require_contains(
        SKILL_ROOT / "references" / "misplaced-artifacts-migration.md",
        (
            "OpenCode `permission.task` migration",
            "first parse and extract",
            "Preserve",
            "never replace user customizations",
            "separate OpenCode config approval gate",
            "agents-system-setup:permission-task-approved",
        ),
    )

    # Inspect any opencode.json files in the repo (samples / fixtures).
    # The plugin itself does not ship one, but if a future commit adds an
    # OpenCode fixture, this gate catches an unsafe `"*": "allow"`.
    for path in REPO.rglob("opencode.json"):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            warn(f"{path.relative_to(REPO).as_posix()}: could not parse JSON ({exc}); skipping task-gate check")
            continue
        agent_map = data.get("agent") if isinstance(data, dict) else None
        if not isinstance(agent_map, dict):
            err(
                f"{path.relative_to(REPO).as_posix()}: missing top-level `agent` map; "
                "OpenCode root-session `permission.task` gate must be defined under "
                "`agent.<root>.permission.task` (v1.3.0)"
            )
            continue
        found_gate = False
        for root_name, root_cfg in agent_map.items():
            if not isinstance(root_cfg, dict):
                continue
            perm = root_cfg.get("permission") if isinstance(root_cfg.get("permission"), dict) else None
            task = perm.get("task") if perm and isinstance(perm.get("task"), dict) else None
            if not task:
                continue
            found_gate = True
            star = task.get("*")
            if star == "allow":
                err(
                    f"{path.relative_to(REPO).as_posix()}: `agent.{root_name}.permission.task[\"*\"]` "
                    "must be `deny` or `ask`, never `allow` (host-orchestrator safety gate)"
                )
        if not found_gate:
            err(
                f"{path.relative_to(REPO).as_posix()}: missing `agent.<root>.permission.task` gate "
                "(v1.3.0 host-orchestrator task gate is mandatory for OpenCode root agents)"
            )


def check_opencode_root_skill_gate() -> None:
    """When OpenCode is selected and the plugin emits host-loaded skills
    (`task-handoff`, `code-change-build-gate`), the host root agent in
    `opencode.json` must also have a `permission.skill` gate. Without it,
    the host cannot load the skill and `Skills Referenced: task-handoff
    loaded=true` packet evidence is false.

    This check enforces SKILL.md and CHANGELOG describe the gate; the
    OpenCode JSON inspector reuses the same star-value safety check as
    the task gate (allow is unsafe by default).
    """
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "OpenCode root-session skill gate",
            "permission.skill",
            "Skills Referenced: task-handoff loaded=true",
            "opencode_skill_gate: declined",
            "inline fail-closed minimum",
        ),
    )

    for path in REPO.rglob("opencode.json"):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        agent_map = data.get("agent") if isinstance(data, dict) else None
        if not isinstance(agent_map, dict):
            continue
        for root_name, root_cfg in agent_map.items():
            if not isinstance(root_cfg, dict):
                continue
            perm = root_cfg.get("permission") if isinstance(root_cfg.get("permission"), dict) else None
            skill = perm.get("skill") if perm and isinstance(perm.get("skill"), dict) else None
            if not skill:
                continue
            star = skill.get("*")
            if star == "allow":
                err(
                    f"{path.relative_to(REPO).as_posix()}: `agent.{root_name}.permission.skill[\"*\"]` "
                    "must be `deny` or `ask`, never `allow` (host-loaded skill safety gate)"
                )


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
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "Required Minimum for Every Task Assignment",
            "Plan Handoff Contract",
            "Context freshness: recent",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        (
            "## Context Load Order",
            "Keep the response concise",
            "## Acceptance Checklist",
            "## Reporting Template",
            "question_request",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.claude.md.template",
        (
            "## Acceptance Checklist",
            "## Reporting Template",
            "question_request",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.opencode.md.template",
        (
            "## Acceptance Checklist",
            "## Reporting Template",
            "question_request",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.gemini.md.template",
        (
            "## Acceptance Checklist",
            "## Reporting Template",
            "question_request",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "Context Load Order",
            "Outcome first",
            "summary + pointer rule",
            "Task Assignment Acceptance Checklist",
            "question_request",
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
        err(f"{rel}: Codex developer_instructions block is {body_lines} lines; hard limit is <= 80 (apply summary + pointer rule).")
    elif body_lines > 65:
        warn(f"{rel}: Codex developer_instructions block is {body_lines} lines; target is <= 65 (apply summary + pointer rule).")


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
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "Plan Handoff Contract",
            "## Orchestration Operating Model",
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


# ---------- 15b: prompt handoff quality ----------

def check_prompt_handoff_quality_policy() -> None:
    """Guard the main-agent to subagent prompt-assignment contract."""

    prompt_ref = SKILL_ROOT / "references" / "prompt-guidelines.md"
    if not prompt_ref.is_file():
        err(f"{prompt_ref.relative_to(REPO).as_posix()}: required prompt guidelines reference is missing")
        return

    require_contains(
        prompt_ref,
        (
            "Prompt Guidelines for Main-to-Subagent Handoff",
            "Orchestrator Assignment Format",
            "Context Packet",
            "Allowed Capabilities",
            "Skills Referenced",
            "Stop / Escalation Conditions",
            "Task assignment quality: ok | warn | fail",
            "provider-neutral",
            "subtask slice",
            "do not load this reference by default",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
            "Task Assignment / Prompt Contract",
            "prompt-guidelines.md",
            "assignment_quality_status",
            "Context Packet",
            "Allowed Capabilities",
            "Skills Referenced",
            "Instructions / Workflow",
            "Stop / Escalation Conditions",
            "Output Schema",
            "Task assignment quality: ok | warn | fail",
            "These twelve fields are mandatory",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "Prompt assignment quality",
            "Context packet rule",
            "Capabilities and skills",
            "Assignment marker",
            "Task assignment quality: ok | warn | fail",
            "Platform-native delegation",
            "OpenAI Codex (CLI + App)",
            ".codex/agents/*.toml",
            "Codex uses this root `AGENTS.md` section",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "GEMINI.md.template",
        (
            "Plan Handoff Contract",
            "subtask slice",
            "Task assignment quality",
            "## Lifecycle",
            "## Delegation Packet",
            "Requirements Triage",
            "Content Quality / Anti-Slop Review",
            "root session",
        ),
    )
    for name in (
        "AGENTS.md.template",
        "GEMINI.md.template",
    ):
        require_contains(
            SKILL_ROOT / "assets" / name,
            (
                "## Wave Execution",
                "agents-system-setup:wave-execution",
                "fan out",
                "parallel-safe",
                "wave",
            ),
        )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "{{OPTIONAL_BACKGROUND_LINE}}",
            "background: true",
            "permission-task-roster: skipped",
            "named roster allows",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "context-optimization.md",
        (
            "Prompt guidelines",
            "Context Packet rule",
            "prompt-contract-review",
            "embedded Assignment Intake",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "output-contract.md",
        (
            "Task assignment quality: <ok|warn|fail",
            "Task-assignment findings",
            "Full Task Assignment / Prompt Contract quality findings",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "replication.md",
        (
            "Context Packet",
            "Allowed Capabilities",
            "Skills Referenced",
            "Stop / Escalation Conditions",
            "Task assignment quality",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Main-to-subagent handoff is structured",
            "prompt-guidelines.md",
            "Orchestrator Assignment Format",
            "Task assignment quality",
        ),
    )

    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "Required Minimum for Every Task Assignment",
            "subtask slice",
            "Task assignment quality: ok | warn | fail",
        ),
    )

    for name in (
        "subagent.agent.md.template",
        "subagent.claude.md.template",
        "subagent.opencode.md.template",
        "subagent.gemini.md.template",
    ):
        path = SKILL_ROOT / "assets" / name
        require_contains(
            path,
            (
                "## Assignment Intake / Preflight",
                "Context Packet",
                "Allowed Capabilities",
                "Skills Referenced",
                "Task assignment quality: ok | warn | fail",
                "{{HANDOFF_TRIAGE_STATUS}}",
                "{{HANDOFF_CONTENT_QUALITY_STATUS}}",
                "{{HANDOFF_CONTEXT_FRESHNESS}}",
            ),
        )
        text = path.read_text(encoding="utf-8")
        if "prompt-guidelines.md" in text:
            err(f"assets/{name}: subagent templates must not load prompt-guidelines.md by default")

    opencode_template = (SKILL_ROOT / "assets" / "subagent.opencode.md.template").read_text(encoding="utf-8")
    if "Use `permission:`" not in opencode_template:
        err("assets/subagent.opencode.md.template: prompt handoff guidance must use OpenCode `permission` vocabulary")

    codex_path = SKILL_ROOT / "assets" / "subagent.codex.toml.template"
    require_contains(
        codex_path,
        (
            "Assignment Intake / Preflight",
            "Context Packet",
            "Allowed Capabilities",
            "Skills Referenced",
            "Task assignment quality: ok | warn | fail",
            "{{HANDOFF_TRIAGE_STATUS}}",
            "{{HANDOFF_CONTENT_QUALITY_STATUS}}",
            "{{HANDOFF_CONTEXT_FRESHNESS}}",
            "Confirm Context freshness is explicit",
        ),
    )
    structural_toml = _strip_toml_triple_strings(codex_path.read_text(encoding="utf-8"))
    if re.search(
        r"(?m)^\s*(?:tools|question|request_user_input|memory|expected_output|assignment_quality|context_packet|allowed_capabilities)\s*=",
        structural_toml,
    ):
        err("assets/subagent.codex.toml.template: prompt handoff fields must stay in developer_instructions, not TOML fields")


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
            "background: true",
            "OpenCode",
            "Permission keys",
            "permission.task",
            "OpenAI Codex (CLI + App)",
            "job_max_runtime_seconds",
            "spawn_agents_on_csv",
            "Gemini CLI",
            "Supported",
            ".gemini/agents/*.md",
            "extension `agents/*.md`",
            "mcp_servers",
            "mcpServers",
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
            "background: true",
            "Permission keys",
            "permission.task",
            "job_max_runtime_seconds",
            "spawn_agents_on_csv",
            ".gemini/agents/<name>.md",
            "extension `agents/*.md`",
            "mcp_servers",
            "mcpServers",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agent-format.md",
        (
            "Emitter rule: keep writing `.github/agents/<name>.agent.md`",
            "Schema split",
            "Plugin-shipped agents",
            "Permission keys",
            "{{OPTIONAL_BACKGROUND_LINE}}",
            "permission-task-roster: skipped",
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
        "check_human_input_protocol",
        "Human Input / Question Tool Matrix",
        "check_self_update_preflight_policy",
        "Phase -1 — Self-Update Preflight",
        "check_requirements_triage_policy",
        "Requirements Triage",
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
                negative_context = re.search(
                    r"\b(no|not|never|without|don't|do not|avoid|nonexistent|does not|there is no)\b",
                    line,
                    re.IGNORECASE,
                )
                if not negative_context:
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
    # Orchestrator role lives in AGENTS.md › Orchestration Operating Model;
    # no separate orchestrator subagent file is emitted. The Standard Tool
    # Profile is now applied to edit-capable specialized subagents only.
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Orchestration Operating Model",
            "host CLI session",
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

    # v1.3.0: orchestrator.agent.md.template is removed; the host CLI session
    # is the orchestrator and reads AGENTS.md directly. No tools-list check
    # is needed for a file that no longer exists.

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
            "Native vs plugin-managed learning",
            "| Runtime | Native memory / learning surface | Setup behavior |",
            "Copilot Memory",
            "Claude Code",
            "OpenCode",
            "OpenAI Codex CLI + App",
            "Gemini CLI",
            "plugin-managed project learning",
            "native_learning_surface",
            "save_memory",
            "autoMemory",
            "activate_skill",
            "Do not emit `memory` in `.codex/agents/*.toml`",
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
            "{{NATIVE_LEARNING_SURFACE}}",
            "{{LEARNING_MEMORY_OWNER}}",
            "{{LEARNING_MEMORY_PATH}}",
            "Native vs plugin-managed",
            "provider-native memory is complementary",
            "plugin-managed Learning Check stays active",
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
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "Reflect & Learn",
            "Learning Check",
            "overwrite",
            "Never store secrets or raw credentials",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
            "host-orchestrator and security-owner approval",
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


def check_instruction_memory_audit_policy() -> None:
    """Keep project memory canonical, adapters thin, and reusable workflows in skills."""
    require_contains(
        SKILL_ROOT / "references" / "instruction-memory-audit.md",
        (
            "Instruction Memory Audit",
            "Artifact classification",
            "Canonical project memory",
            "Runtime adapter",
            "Skill workflow",
            "Path-scoped rule",
            "adapter-drift",
            "duplicate-policy",
            "skill-candidate",
            "path-scoped-candidate",
            "Instruction memory audit: ok|warn|fail|n/a",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "instruction-memory-audit",
            "CLAUDE.md",
            "GEMINI.md",
            "Instruction Memory Audit",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Instruction Memory Audit",
            "{{INSTRUCTION_MEMORY_AUDIT_STATUS}}",
            "{{INSTRUCTION_MEMORY_AUDIT_SIGNALS}}",
            "CLAUDE.md` adapter: import, symlink, or copy",
            "adapter symlinks/copies are expected and not conflicts",
            "instruction-memory-audit",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "platforms.md",
        (
            "Instruction memory adapter rule",
            "canonical cross-runtime",
            "runtime adapter",
            "not duplicate-policy findings",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "context-optimization.md",
        (
            "Runtime memory adapters",
            "Instruction Memory Audit",
            "instruction-memory-audit",
            "adapter drift",
        ),
    )


def check_upgrade_mismatch_detection_policy() -> None:
    """Upgrade mode runs version-stamp playbook + structural mismatch/deprecation diff."""
    migration_ref = SKILL_ROOT / "references" / "misplaced-artifacts-migration.md"
    require_contains(
        migration_ref,
        (
            "v1.4.0 → v1.5.0",
            "task-handoff",
            "code-change-build-gate",
            "build-runner",
            "change-bug-hunter",
            "change-validator",
            "Build Gate (SDLC)",
            "Mismatch & Deprecation Detection (upgrade mode)",
            "stale-stamp",
            "missing-section",
            "missing-skill",
            "missing-role",
            "deprecated-artifact",
            "stale-prose",
            "unsupported-runtime-field",
            "adapter-drift",
            "missing-overflow-link",
            "Upgrade procedure",
            "Mismatch report shape",
            "migration-backup",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "mismatch--deprecation-detection-upgrade-mode",
            "structural diff",
            "missing sections/skills/roles",
            "deprecated artifacts",
            "migration-backup",
        ),
    )


def check_sdlc_build_gate_policy() -> None:
    """Ensure SDLC Build Gate is wired across reference, templates, AGENTS.md, SKILL.md, and topology."""
    require_contains(
        SKILL_ROOT / "references" / "sdlc-build-gate.md",
        (
            "SDLC Build Gate",
            "Diff bucket model",
            "max(size_bucket, criticality_bucket)",
            "Criticality bucket",
            "Auth / authz / session middleware",
            "Crypto / signing / token handling",
            "Public API / exported symbols / ABI",
            "Schema / migration / database model",
            "Dependency manifest / lockfile",
            "Feature flag / config default",
            "Permission / policy / IaC",
            "Gate matrix",
            "build-runner",
            "change-bug-hunter",
            "change-validator",
            "Mutual-exclusion routing",
            "evidence integrator",
            "fail-closed",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "build-gate-matrix.snippet.md",
        (
            "agents-system-setup:build-gate-matrix:start",
            "agents-system-setup:build-gate-matrix:end",
            "{{BUILD_GATE_STRICTNESS}}",
            "Diff buckets",
            "Required gates per bucket",
            "change-bug-hunter",
            "change-validator",
            "Wave assignment",
        ),
    )
    skill_path = (
        SKILL_ROOT
        / "assets"
        / "skills"
        / "code-change-build-gate.skill.md.template"
    )
    require_contains(
        skill_path,
        (
            "name: code-change-build-gate",
            "agents-system-setup:skill-kind: sdlc-build-gate",
            "max(size_bucket, criticality_bucket)",
            "build-runner",
            "change-bug-hunter",
            "change-validator",
            "Mutual-exclusion routing",
            "Strictness modifier",
            "Build gate: bucket=",
            ".codex/skills/code-change-build-gate/SKILL.md",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Build Gate (SDLC)",
            "{{BUILD_GATE_STRICTNESS}}",
            "{{BUILD_GATE_MATRIX}}",
            "{{BUILD_GATE_REFERENCE}}",
            "code-change-build-gate",
            "change-bug-hunter",
            "change-validator",
            "max(size_bucket, criticality_bucket)",
            "n/a — non-software project | user skipped",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Build Gate (SDLC)",
            "build_gate_strictness",
            "sdlc-build-gate",
            "code-change-build-gate",
            "build-gate-matrix",
            "max(size_bucket, criticality_bucket)",
            "change-bug-hunter",
            "change-validator",
            "merge `change-validator` into `@reviewer`",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "topology.md",
        (
            "Software-Dev Universal Subagents (Build Gate)",
            "build-runner",
            "change-bug-hunter",
            "change-validator",
            "evidence integrator",
            "mutual-exclusion",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "interview.md",
        (
            "9d. SDLC Build Gate",
            "build_gate_strictness",
            "Standard (Recommended)",
            "Strict",
            "Light",
            "Skip",
        ),
    )


def check_code_quality_policy() -> None:
    """Ensure the Code Quality & Maintainability subsystem is wired across
    reference, skill template, snippet, AGENTS.md, SKILL.md, topology, interview,
    the Build Gate cross-link, and the subagent/task-handoff propagation markers.

    Code quality = authoring craft for project source code; complementary to the
    Build Gate (verification) and distinct from content-quality (agent prose).
    The propagation markers are asserted so the standards actually reach the
    code-writing subagents, not just the docs.
    """
    require_contains(
        SKILL_ROOT / "references" / "code-quality.md",
        (
            "# Code Quality & Maintainability Standards",
            "Rule 0 — Conform to existing conventions first",
            ".editorconfig",
            "ISO/IEC 25010",
            "cyclomatic complexity",
            "code_quality_strictness",
            "code-quality-reviewer",
            "convention-drift",
            "swallowed-error",
            "Skills Referenced: code-quality loaded=true",
            "Code quality: <ok|warn|fail|n/a>; reviewer=<separate|merged|skipped>; signals=<list|none>",
            "content-quality",
            "advisory",
        ),
    )
    skill_path = (
        SKILL_ROOT / "assets" / "skills" / "code-quality.skill.md.template"
    )
    require_contains(
        skill_path,
        (
            "name: code-quality",
            "agents-system-setup:skill-kind: code-quality",
            "Conform before you write (Rule 0)",
            "code_quality_strictness",
            "code-bearing",
            "Skills Referenced: code-quality loaded=true",
            "Code quality: ok | warn | fail | n/a; signals=<list|none>",
            ".codex/skills/code-quality/SKILL.md",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "code-quality-standards.snippet.md",
        (
            "agents-system-setup:code-quality-standards:start",
            "agents-system-setup:code-quality-standards:end",
            "{{CODE_QUALITY_STRICTNESS}}",
            "Rule 0 — Conform to existing conventions first",
            "Code quality: <ok|warn|fail|n/a>; reviewer=<separate|merged|skipped>; signals=<list|none>",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Code Quality & Maintainability",
            "{{CODE_QUALITY_STRICTNESS}}",
            "{{CODE_QUALITY_STANDARDS}}",
            "{{CODE_QUALITY_REFERENCE}}",
            "{{CODE_QUALITY_OWNER}}",
            "{{CODE_QUALITY_SKILL_PATHS}}",
            "{{CODE_QUALITY_STATUS}}",
            "code-quality-reviewer",
            "Code quality: n/a — non-software project",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Code quality & maintainability is mandatory for software-dev",
            "conform to the project's existing conventions first",
            "code_quality_strictness",
            "code-quality-reviewer",
            "code-quality-standards",
            "Code Quality & Maintainability emission",
            "code-bearing repo → `advisory`",
            "`code-quality` for code-bearing projects",
            "Skills Referenced: code-quality loaded=true",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "topology.md",
        (
            "code-quality-reviewer",
            "Code Quality Sizing Rule",
            "code_quality_reviewer = merged",
            "Code quality: ok|warn|fail|n/a",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "interview.md",
        (
            "code_quality_strictness",
            "code-quality",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "sdlc-build-gate.md",
        (
            "@code-quality-reviewer",
            "Code quality: ok|warn|fail|n/a; signals=<list|none>",
            "code-quality",
        ),
    )
    # Propagation: the Code quality reporting marker must reach every code-writing
    # surface (subagent templates + the host-side task-handoff skill).
    propagation_targets = [
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        SKILL_ROOT / "assets" / "subagent.claude.md.template",
        SKILL_ROOT / "assets" / "subagent.opencode.md.template",
        SKILL_ROOT / "assets" / "subagent.gemini.md.template",
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        SKILL_ROOT / "assets" / "skills" / "task-handoff.skill.md.template",
    ]
    for path in propagation_targets:
        require_contains(
            path,
            ("Code quality: ok | warn | fail | n/a; signals=<list|none>",),
        )
    # Apply contract: edit-capable/reviewer subagent templates must instruct the
    # agent to APPLY the standards while working, not merely report the marker.
    apply_instruction_targets = [
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        SKILL_ROOT / "assets" / "subagent.claude.md.template",
        SKILL_ROOT / "assets" / "subagent.opencode.md.template",
        SKILL_ROOT / "assets" / "subagent.gemini.md.template",
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
    ]
    for path in apply_instruction_targets:
        require_contains(path, ("Code Quality & Maintainability",))
    require_contains(
        SKILL_ROOT / "assets" / "skills" / "task-handoff.skill.md.template",
        ("Skills Referenced: code-quality loaded=true",),
    )


def check_layered_context_hard_rule() -> None:
    """Ensure hard rule #37 (layered context & self-contained subagents) is declared in SKILL.md and the supporting snippets exist with the canonical content."""
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "Layered context & self-contained subagents",
            "subagent_count >= 2",
            "**Audience:** all | host-orchestrator | subagents",
            "subagent-digest:managed:start",
            "audience-tags snippet",
            "project-standard-digest snippet",
            "explorer-agents",
        ),
    )
    audience_path = SKILL_ROOT / "assets" / "audience-tags.snippet.md"
    require_contains(
        audience_path,
        (
            "**Audience:**",
            "all",
            "host-orchestrator",
            "subagents",
            "subagent_count >= 2",
            "balanced",
            "Subagent Self-Contained Notice",
        ),
    )
    digest_path = SKILL_ROOT / "assets" / "project-standard-digest.snippet.md"
    require_contains(
        digest_path,
        (
            "subagent-digest:managed:start v=",
            "subagent-digest:managed:end",
            "sha256",
            "task-handoff",
            "Codex variant",
        ),
    )


def check_audience_tags_in_agents_md() -> None:
    """Ensure AGENTS.md.template carries the audience-tag placeholders and Project Snapshot has the **Audience:** all marker."""
    template = SKILL_ROOT / "assets" / "AGENTS.md.template"
    require_contains(
        template,
        (
            "{{AUDIENCE_TAGS_BLOCK}}",
            "{{SUBAGENT_SELF_CONTAINED_NOTICE}}",
            "{{PROJECT_SNAPSHOT_AUDIENCE}}",
        ),
    )


def check_subagent_self_containment() -> None:
    """Ensure every subagent template carries the digest managed-block markers and placeholder; Codex uses the 3-line literal variant."""
    md_templates = [
        SKILL_ROOT / "assets" / "subagent.agent.md.template",
        SKILL_ROOT / "assets" / "subagent.claude.md.template",
        SKILL_ROOT / "assets" / "subagent.opencode.md.template",
        SKILL_ROOT / "assets" / "subagent.gemini.md.template",
    ]
    for path in md_templates:
        require_contains(
            path,
            (
                "<!-- subagent-digest:managed:start v=",
                "{{PROJECT_STANDARD_DIGEST}}",
                "<!-- subagent-digest:managed:end -->",
            ),
        )
    codex_path = SKILL_ROOT / "assets" / "subagent.codex.toml.template"
    require_contains(
        codex_path,
        (
            "<!-- subagent-digest:managed:start v=",
            "Project standard digest (managed by agents-system-setup):",
            "Boundary: least privilege",
            "Handoff: consult `task-handoff` skill",
            "<!-- subagent-digest:managed:end -->",
        ),
    )


def check_explorer_agents_reference() -> None:
    """Ensure explorer-agents.md exists with verified per-runtime mapping and SKILL.md Phase 1 references it."""
    explorer_path = SKILL_ROOT / "references" / "explorer-agents.md"
    require_contains(
        explorer_path,
        (
            "GitHub Copilot CLI",
            "`task` tool, `agent_type: \"explore\"`",
            "`Explore` built-in subagent",
            "`explore` built-in subagent",
            "`explorer` built-in agent",
            "`codebase_investigator` built-in subagent",
            "source_files > 50",
            "top_level_dirs > 8",
            "frameworks_detected > 3",
            "recon_threads_requested > 2",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "explorer-agents",
            "native explorer subagent",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "platforms.md",
        (
            "Native explorer agents",
            "explorer-agents",
        ),
    )


def check_host_builtins_routing_reference() -> None:
    """Ensure host-builtins-routing reference and snippet preserve required routing anchors and literals."""
    reference_path = SKILL_ROOT / "references" / "host-builtins-routing.md"
    require_contains(
        reference_path,
        (
            "# Host Builtins Routing",
            "## Source citations table",
            "## Routing decision rules",
            "## Per-runtime routing inventory",
            "### GitHub Copilot CLI",
            "### Claude Code",
            "### OpenCode",
            "### OpenAI Codex CLI and App",
            "### Gemini CLI",
            "host_builtins_routing: declined",
            "Subagent rule",
        ),
    )

    snippet_path = SKILL_ROOT / "assets" / "host-builtins-routing.snippet.md"
    require_contains(
        snippet_path,
        (
            "<!-- agents-system-setup:host-builtins-routing -->",
            "### Native Runtime Agents",
            "host_builtins_routing: declined",
        ),
    )
    try:
        snippet = snippet_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return
    except UnicodeDecodeError:
        return
    rel = snippet_path.relative_to(REPO).as_posix()
    if snippet.count("<!-- agents-system-setup:host-builtins-routing -->") < 2:
        err(f"{rel}: host-builtins-routing anchor must appear at least twice")
    if snippet.count("### Native Runtime Agents") < 2:
        err(f"{rel}: Native Runtime Agents heading must appear at least twice")


def check_host_builtins_routing_in_agents_md() -> None:
    """Ensure AGENTS.md.template contains the host-builtins placeholder in the orchestrator section."""
    template = SKILL_ROOT / "assets" / "AGENTS.md.template"
    require_contains(template, ("{{HOST_BUILTINS_ROUTING_BLOCK}}",))
    rel = template.relative_to(REPO).as_posix()
    try:
        lines = template.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return
    except UnicodeDecodeError:
        return

    platform_line = next(
        (i for i, line in enumerate(lines, start=1) if line == "### Platform-native delegation"),
        None,
    )
    placeholder_line = next(
        (i for i, line in enumerate(lines, start=1) if "{{HOST_BUILTINS_ROUTING_BLOCK}}" in line),
        None,
    )
    wave_line = next(
        (i for i, line in enumerate(lines, start=1) if line == "## Wave Execution"),
        None,
    )
    if not platform_line or not placeholder_line or not wave_line:
        err(f"{rel}: cannot verify host builtins placeholder placement")
        return
    if not (platform_line < placeholder_line < wave_line):
        err(
            f"{rel}: {{HOST_BUILTINS_ROUTING_BLOCK}} must be between "
            "### Platform-native delegation and ## Wave Execution"
        )


def check_tool_catalog_json_schema() -> None:
    """Ensure the v1.8.0 tool catalog has the expected runtime schema."""
    catalog_path = SKILL_ROOT / "assets" / "tool-catalog.json"
    rel = catalog_path.relative_to(REPO).as_posix()
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        err(f"{rel}: required tool catalog file is missing")
        return
    except json.JSONDecodeError as e:
        err(f"{rel}: invalid JSON: {e}")
        return
    except UnicodeDecodeError:
        err(f"{rel}: not valid UTF-8")
        return

    for key in ("catalog_version", "last_updated", "runtimes"):
        if key not in catalog:
            err(f"{rel}: missing top-level field `{key}`")
    if not isinstance(catalog.get("catalog_version"), str) or not catalog.get("catalog_version"):
        err(f"{rel}: `catalog_version` must be a non-empty string")

    runtimes = catalog.get("runtimes")
    expected_runtimes = {
        "copilot-cli",
        "vscode-copilot",
        "claude-code",
        "opencode",
        "codex",
        "gemini-cli",
    }
    if not isinstance(runtimes, dict):
        err(f"{rel}: `runtimes` must be an object")
        return
    if set(runtimes) != expected_runtimes:
        err(f"{rel}: `runtimes` keys must be exactly {sorted(expected_runtimes)}")
        return

    allowed_audit_kinds = {
        "name-allowlist",
        "permission-policy",
        "n/a-unless-explicit",
    }
    for runtime_id, runtime in runtimes.items():
        if not isinstance(runtime, dict):
            err(f"{rel}: `runtimes.{runtime_id}` must be an object")
            continue
        for key in ("display_name", "audit_kind", "source_url"):
            if key not in runtime:
                err(f"{rel}: missing field `runtimes.{runtime_id}.{key}`")
        audit_kind = runtime.get("audit_kind")
        if audit_kind not in allowed_audit_kinds:
            err(f"{rel}: `runtimes.{runtime_id}.audit_kind` has unsupported value `{audit_kind}`")

        profiles = runtime.get("profiles")
        if audit_kind == "name-allowlist" and profiles:
            tools = runtime.get("tools")
            if not isinstance(tools, list):
                err(f"{rel}: `runtimes.{runtime_id}.tools` must be a list for profile validation")
                continue
            tool_names = {
                tool.get("name")
                for tool in tools
                if isinstance(tool, dict) and isinstance(tool.get("name"), str)
            }
            if not isinstance(profiles, dict):
                err(f"{rel}: `runtimes.{runtime_id}.profiles` must be an object")
                continue
            for profile_name, profile_tools in profiles.items():
                if profile_tools is None:
                    continue
                if not isinstance(profile_tools, list):
                    err(f"{rel}: `runtimes.{runtime_id}.profiles.{profile_name}` must be a list or null")
                    continue
                for tool_name in profile_tools:
                    if tool_name not in tool_names:
                        err(
                            f"{rel}: profile `runtimes.{runtime_id}.profiles.{profile_name}` "
                            f"references unknown tool `{tool_name}`"
                        )

    opencode = runtimes["opencode"]
    if opencode.get("audit_kind") != "permission-policy":
        err(f"{rel}: `runtimes.opencode.audit_kind` must be `permission-policy`")
    if not isinstance(opencode.get("permission_keys"), list):
        err(f"{rel}: `runtimes.opencode.permission_keys` must be a list")
    if "tools" not in opencode.get("deprecated_keys", []):
        err(f"{rel}: `runtimes.opencode.deprecated_keys` must include `tools`")

    codex = runtimes["codex"]
    if codex.get("audit_kind") != "n/a-unless-explicit":
        err(f"{rel}: `runtimes.codex.audit_kind` must be `n/a-unless-explicit`")
    if codex.get("default_behavior") != "inherit-session":
        err(f"{rel}: `runtimes.codex.default_behavior` must be `inherit-session`")


def check_tool_catalog_reference() -> None:
    """Ensure the human tool catalog reference keeps stable runtime headings."""
    require_contains(
        SKILL_ROOT / "references" / "tool-catalog.md",
        (
            "# Tool Catalog",
            "Canonical data is `assets/tool-catalog.json`; this reference is the human view of that data.",
            "## GitHub Copilot CLI (`copilot-cli`)",
            "## VS Code Copilot (`vscode-copilot`)",
            "## Claude Code (`claude-code`)",
            "## OpenCode (`opencode`)",
            "## OpenAI Codex (CLI + App) (`codex`)",
            "## Gemini CLI (`gemini-cli`)",
            "## Audit kinds reference",
            "## Anti-patterns",
        ),
    )


def check_tool_catalog_audit_skill_template() -> None:
    """Ensure the host-side read-only tool catalog audit skill template is present."""
    require_contains(
        SKILL_ROOT / "assets" / "skills" / "tool-catalog-audit.skill.md.template",
        (
            "name: tool-catalog-audit",
            "# Tool Catalog Audit (host-side)",
            "Read-only.",
            "name-allowlist",
            "Permission-policy runtime",
            "missing-tool-catalog-stamp",
            "unknown-tool-name",
        ),
    )


def check_tool_catalog_stamp_in_templates() -> None:
    """Ensure generated AGENTS.md and every subagent template carries the catalog stamp."""
    stamp = "agents-system-setup:tool-catalog-version: {{PLUGIN_VERSION}}"
    for template_name in (
        "AGENTS.md.template",
        "subagent.agent.md.template",
        "subagent.claude.md.template",
        "subagent.opencode.md.template",
        "subagent.gemini.md.template",
        "subagent.codex.toml.template",
    ):
        require_contains(SKILL_ROOT / "assets" / template_name, (stamp,))


def check_task_handoff_skill_policy() -> None:
    """Ensure the host-side task-handoff skill is emitted and referenced as the source of truth."""
    skill_path = (
        SKILL_ROOT
        / "assets"
        / "skills"
        / "task-handoff.skill.md.template"
    )
    require_contains(
        skill_path,
        (
            "name: task-handoff",
            "agents-system-setup:skill-kind: host-handoff",
            "Host-only composition",
            "12 required-minimum fields",
            "Skills Referenced: task-handoff loaded=true",
            "subagents are executors",
            "fail-closed",
            ".codex/skills/task-handoff/SKILL.md",
            "Acceptance Checklist",
            "Reporting Template",
            "Build gate:",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "task-handoff",
            "host-side source of truth",
            "Skills Referenced: task-handoff loaded=true",
            "Subagents never re-delegate through this skill",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "{{TASK_HANDOFF_SKILL_PATHS}}",
            "Use the `task-handoff` skill",
            "Skills Referenced: task-handoff loaded=true",
            "executors",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "handoff.md",
        (
            "task-handoff",
            "host-side `task-handoff` skill",
            "Skills Referenced: task-handoff loaded=true",
            "Subagents are executors",
            "return-to-orchestrator",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "platforms.md",
        (
            "Skill auto-load and pointer-fallback rule",
            "task-handoff",
            "code-change-build-gate",
            "Skills Referenced: task-handoff loaded=true",
            "pointer-only is acceptable",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "context-optimization.md",
        (
            "code-change-build-gate",
            "task-handoff",
            "host-only",
        ),
    )
    # Every subagent template (Markdown + Codex TOML) must keep an inline
    # Reporting Template guard with the new Build gate line and a task-handoff
    # source-of-truth pointer.
    for template_name in (
        "subagent.agent.md.template",
        "subagent.claude.md.template",
        "subagent.opencode.md.template",
        "subagent.gemini.md.template",
    ):
        require_contains(
            SKILL_ROOT / "assets" / template_name,
            (
                "task-handoff",
                "fail-closed minimum",
                "Build gate: n/a | bucket=",
                "return-to-orchestrator",
            ),
        )
    require_contains(
        SKILL_ROOT / "assets" / "subagent.codex.toml.template",
        (
            "task-handoff",
            ".codex/skills/task-handoff/SKILL.md",
            "Never use the skill to delegate to another subagent",
            "Build gate:",
            "code-change-build-gate",
        ),
    )


def check_agents_doctor_skill_policy() -> None:
    """Ensure the host-side read-only agents-doctor health check is present and wired.

    The doctor reconciles the generated agent system on disk against the central
    manifest and catches strays (especially a hand-written orchestrator file),
    missing artifacts, checksum drift, and operational-state misroutes.
    """
    skill_path = SKILL_ROOT / "assets" / "skills" / "agents-doctor.skill.md.template"
    require_contains(
        skill_path,
        (
            "name: agents-doctor",
            "agents-system-setup:skill-kind: host-doctor",
            "# Agents Doctor (host-side)",
            "**READ-ONLY**",
            "**HOST-ONLY**",
            "orchestrator-subagent-file",
            "stray-agent",
            ".agents-system-setup/generated.json",
            "python3 .agents-system-setup/agents-doctor.py",
        ),
    )
    script_path = SKILL_ROOT / "assets" / "agents-doctor.py.template"
    require_contains(
        script_path,
        (
            "agents-system-setup:generated-by: {{PLUGIN_VERSION}}",
            "agents-system-setup:tool-kind: host-doctor",
            "This tool NEVER modifies files",
            "generated.json",
            "orchestrator-subagent-file",
            "stray-agent",
            "operational-state-artifact",
            "--json",
            "--strict",
        ),
    )
    require_contains(
        SKILL_ROOT / "SKILL.md",
        (
            "agents-doctor",
            "reconciles on-disk agents against",
            ".agents-system-setup/agents-doctor.py",
            "stray-agent",
            "orchestrator-subagent-file",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "agents-doctor.md",
        (
            "# Agents Doctor — generated-system health check",
            "## Signal catalog",
            "## Reconciliation algorithm",
            "## Exit codes",
            "orchestrator-subagent-file",
            "stray-agent",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "AGENTS.md.template",
        (
            "## Generated-System Health Check",
            "python3 .agents-system-setup/agents-doctor.py",
        ),
    )


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
    check_operational_state_artifacts()
    check_governance_baseline()
    check_human_input_protocol()
    check_self_update_preflight_policy()
    check_requirements_triage_policy()
    check_output_quality_policy()
    check_security_team_policy()
    check_cwd_reconnaissance_policy()
    check_purpose_before_footprint_in_phase_0()
    check_misplaced_artifacts_migration_policy()
    check_no_orchestrator_subagent_emission()
    check_pointer_files_to_agents_md()
    check_opencode_root_task_gate()
    check_opencode_root_skill_gate()
    check_mcp_approval_gate()
    check_central_mcp_approval_evidence()
    check_optional_placeholder_leaks()
    check_optional_placeholder_table()
    check_mcp_secret_shape()
    check_context_optimization()
    check_local_tracking_policy()
    check_plan_handoff_policy()
    check_prompt_handoff_quality_policy()
    check_codex_cli_app_compatibility()
    check_runtime_update_policy()
    check_runtime_invocation_policy()
    check_copilot_tool_profile()
    check_learning_memory_policy()
    check_instruction_memory_audit_policy()
    check_sdlc_build_gate_policy()
    check_code_quality_policy()
    check_layered_context_hard_rule()
    check_audience_tags_in_agents_md()
    check_subagent_self_containment()
    check_explorer_agents_reference()
    check_host_builtins_routing_reference()
    check_host_builtins_routing_in_agents_md()
    check_tool_catalog_json_schema()
    check_tool_catalog_reference()
    check_tool_catalog_audit_skill_template()
    check_tool_catalog_stamp_in_templates()
    check_task_handoff_skill_policy()
    check_agents_doctor_skill_policy()
    check_upgrade_mismatch_detection_policy()

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
