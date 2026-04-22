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

Exits non-zero on any failure. Designed to be invoked from CI on
Linux / macOS / Windows runners with only Python 3.10+ available
(no pip install required: jsonschema is OPTIONAL — when absent we
fall back to ad-hoc field checks).

Usage:
  python3 scripts/_validate.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

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
        err(f"missing manifest: {path.relative_to(REPO)}")
    except json.JSONDecodeError as e:
        err(f"invalid JSON in {path.relative_to(REPO)}: {e}")
    return None


def check_manifests() -> None:
    versions: dict[str, str] = {}
    for path in VERSIONED_MANIFESTS:
        rel = str(path.relative_to(REPO))
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
    rel = str(MARKETPLACE.relative_to(REPO))
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
                target = (MARKETPLACE.parent / sp).resolve() if sp.startswith(".") else (REPO / sp).resolve()
                # marketplace lives at .agents/plugins/marketplace.json; "./" resolves relative to that dir
                # but per Codex spec, source.path is relative to the marketplace root which is the repo
                root_target = (REPO / sp).resolve()
                if not target.exists() and not root_target.exists():
                    err(f"{rel}: plugins[{i}].source.path `{sp}` does not exist on disk")

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


# ---------- main ----------

def main() -> int:
    print(f"Validating {REPO} …")
    check_manifests()
    check_frontmatter_files()
    check_encoding()
    check_internal_links()

    if WARNINGS:
        print("\nWARNINGS:")
        for w in WARNINGS:
            print(f"  ⚠ {w}")
    if ERRORS:
        print("\nERRORS:")
        for e in ERRORS:
            print(f"  ✗ {e}")
        print(f"\n{len(ERRORS)} error(s).")
        return 1
    print(f"\n✓ All checks passed ({len(WARNINGS)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
