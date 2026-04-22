#!/usr/bin/env python3
"""
Atomic version bump across all four manifests + CHANGELOG.md stub.

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
]

SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$")


def bump_json(path: Path, new_version: str) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    old = data.get("version")
    data["version"] = new_version
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return f"  {path.relative_to(REPO)}: {old} → {new_version}"


def bump_changelog(new_version: str) -> str:
    cl = REPO / "CHANGELOG.md"
    text = cl.read_text(encoding="utf-8")
    today = date.today().isoformat()
    stub = f"## [{new_version}] - {today}\n\n### Added\n\n- _TBD_\n\n### Changed\n\n- _TBD_\n\n### Fixed\n\n- _TBD_\n\n"
    if f"[{new_version}]" in text:
        return f"  CHANGELOG.md: section [{new_version}] already exists, skipped"
    # Insert after the first H1 (top of file).
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    inserted = False
    for i, ln in enumerate(lines):
        out.append(ln)
        if not inserted and ln.startswith("# "):
            # Skip until we hit the first '## ' to insert just above it.
            j = i + 1
            while j < len(lines) and not lines[j].startswith("## "):
                out.append(lines[j])
                j += 1
            out.append("\n" + stub)
            out.extend(lines[j:])
            inserted = True
            break
    if not inserted:
        out = [stub, "\n"] + lines
    cl.write_text("".join(out), encoding="utf-8")
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
    print(bump_changelog(nv))
    print("\nNext steps:")
    print(f"  git checkout -b release/v{nv}")
    print(f"  git add -A && git commit -m 'chore(release): v{nv}'")
    print(f"  # open PR, merge, then:")
    print(f"  git tag v{nv} && git push origin v{nv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
