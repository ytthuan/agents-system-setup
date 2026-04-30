#!/usr/bin/env python3
"""
Atomic version bump across plugin manifests, marketplace metadata, and CHANGELOG.md stub.

Usage:
  python3 scripts/_bump_version.py 0.2.1
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

MANIFESTS = [
    REPO / "plugin.json",
    REPO / ".claude-plugin" / "plugin.json",
    REPO / ".codex-plugin" / "plugin.json",
    REPO / "plugins" / "agents-system-setup" / ".claude-plugin" / "plugin.json",
    REPO / "plugins" / "agents-system-setup" / ".codex-plugin" / "plugin.json",
]
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"

SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$")


def bump_json(path: Path, new_version: str) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    old = data.get("version")
    data["version"] = new_version
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return f"  {path.relative_to(REPO)}: {old} → {new_version}"


def bump_claude_marketplace(new_version: str) -> str:
    data = json.loads(CLAUDE_MARKETPLACE.read_text(encoding="utf-8"))
    old = data.get("metadata", {}).get("version")
    data.setdefault("metadata", {})["version"] = new_version
    for plugin in data.get("plugins", []):
        if isinstance(plugin, dict):
            plugin["version"] = new_version
    CLAUDE_MARKETPLACE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return f"  {CLAUDE_MARKETPLACE.relative_to(REPO)}: {old} → {new_version}"


def bump_changelog(new_version: str) -> str:
    cl = REPO / "CHANGELOG.md"
    text = cl.read_text(encoding="utf-8")
    today = date.today().isoformat()
    stub = f"## [{new_version}] - {today}\n\n### Added\n\n- _TBD_\n\n### Changed\n\n- _TBD_\n\n### Fixed\n\n- _TBD_\n"
    if f"[{new_version}]" in text:
        return f"  CHANGELOG.md: section [{new_version}] already exists, skipped"
    # Insert just above the first existing "## [" line; preserve single blank line before it.
    m = re.search(r"^## \[", text, re.M)
    if m:
        insert_at = m.start()
        new_text = text[:insert_at] + stub + "\n" + text[insert_at:]
    else:
        # No prior versions — append after H1 paragraph.
        new_text = text.rstrip() + "\n\n" + stub
    # Collapse any 3+ consecutive blank lines down to a single blank line.
    new_text = re.sub(r"\n{3,}", "\n\n", new_text)
    cl.write_text(new_text, encoding="utf-8")
    return f"  CHANGELOG.md: prepended [{new_version}] stub"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: bump-version <new-semver>", file=sys.stderr)
        return 2
    nv = sys.argv[1]
    if not SEMVER.match(nv):
        print(f"✗ `{nv}` is not a valid semver", file=sys.stderr)
        return 2

    print(f"Bumping to {nv}:")
    for m in MANIFESTS:
        print(bump_json(m, nv))
    print(bump_claude_marketplace(nv))
    print(bump_changelog(nv))
    print("\nNext steps:")
    print(f"  git checkout -b release/v{nv}")
    print(f"  git add -A && git commit -m 'chore(release): v{nv}'")
    print(f"  # open PR, merge, then:")
    print(f"  git tag v{nv} && git push origin v{nv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
