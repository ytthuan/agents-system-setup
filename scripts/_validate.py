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


def parse_scalar(value: str) -> Any:
    raw = value.strip()
    if not raw:
        return ""
    if raw in {"|", ">"}:
        return raw
    if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
        return raw[1:-1]
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
    """Tiny fallback for the top-level YAML shapes used by runtime frontmatter."""
    lines = [line.rstrip("\r") for line in body.splitlines()]
    significant = [line for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if not significant:
        return {}
    if significant[0].lstrip().startswith("- "):
        items: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        for line in significant:
            stripped = line.strip()
            if stripped.startswith("- "):
                current = {}
                items.append(current)
                stripped = stripped[2:].strip()
                if not stripped:
                    continue
            if current is not None and ":" in stripped:
                key, _, value = stripped.partition(":")
                current[key.strip()] = parse_scalar(value)
        return items

    out: dict[str, Any] = {}
    current_list_key: str | None = None
    for line in significant:
        stripped = line.strip()
        if current_list_key and stripped.startswith("- "):
            out.setdefault(current_list_key, []).append(parse_scalar(stripped[2:]))
            continue
        current_list_key = None
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        if not value:
            out[key] = []
            current_list_key = key
        else:
            out[key] = parse_scalar(value)
    return out


def parse_yaml_document(body: str) -> Any:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(body) or {}
    except ImportError:
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
            "delegation-packet-canonical-schema",
            "Context freshness: recent",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.claude.md.template",
        (
            "## Delegation Packet",
            "delegation-packet-canonical-schema",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.opencode.md.template",
        (
            "## Delegation Packet",
            "delegation-packet-canonical-schema",
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
            "{{PLATFORM_FORMAT_NOTES}}",
            "{{HANDOFF_EVIDENCE}}",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.agent.md.template",
        (
            "Plan Handoff Contract",
            "delegation-packet-canonical-schema",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.claude.md.template",
        (
            "agents-system-setup:platform: claude-code",
            "Plan Handoff Contract",
            "delegation-packet-canonical-schema",
        ),
    )
    require_contains(
        SKILL_ROOT / "assets" / "orchestrator.opencode.md.template",
        (
            "agents-system-setup:platform: opencode",
            "mode: primary",
            "delegation-packet-canonical-schema",
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
            "Last verified: 2026-04-29",
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
            "mcp_servers",
            "agent_card_url",
            "agent_card_json",
        ),
    )
    require_contains(
        SKILL_ROOT / "references" / "marketplaces.md",
        (
            "Last verified: 2026-04-29",
            "Gemini CLI",
            ".gemini/agents/*.md",
            "skills`, `mcpServers`, `apps`",
        ),
    )
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


def check_learning_memory_policy() -> None:
    """Keep the generated memory and reinforcement-learning loop intact."""
    require_contains(
        SKILL_ROOT / "references" / "learning-memory.md",
        (
            "Memory and Learning System",
            "Learning Check contract",
            "overwrite requires orchestrator approval",
            "no secrets or raw credentials",
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
    check_context_optimization()
    check_local_tracking_policy()
    check_plan_handoff_policy()
    check_codex_cli_app_compatibility()
    check_runtime_update_policy()
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
