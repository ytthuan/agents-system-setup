#!/usr/bin/env bash
# link-project-memory.sh — keep CLAUDE.md in sync with AGENTS.md.
# - macOS/Linux: symlink CLAUDE.md → AGENTS.md (zero drift).
# - Windows / non-POSIX: copy with a generated header (re-run on update).
# Idempotent: safe to run repeatedly.
set -euo pipefail

if [ ! -f AGENTS.md ]; then
  echo "❌ AGENTS.md not found in $(pwd) — generate it first." >&2
  exit 1
fi

OS="$(uname -s 2>/dev/null || echo Unknown)"

case "$OS" in
  Darwin|Linux)
    if [ -L CLAUDE.md ] && [ "$(readlink CLAUDE.md)" = "AGENTS.md" ]; then
      echo "✅ CLAUDE.md already symlinked to AGENTS.md."
      exit 0
    fi
    if [ -e CLAUDE.md ]; then
      cp CLAUDE.md CLAUDE.md.bak
      echo "ℹ️  Existing CLAUDE.md backed up to CLAUDE.md.bak"
      rm CLAUDE.md
    fi
    ln -s AGENTS.md CLAUDE.md
    echo "✅ CLAUDE.md → AGENTS.md (symlink)."
    ;;
  *)
    if [ -f CLAUDE.md ] && ! grep -q "generated from AGENTS.md" CLAUDE.md; then
      cp CLAUDE.md CLAUDE.md.bak
      echo "ℹ️  Existing CLAUDE.md backed up to CLAUDE.md.bak"
    fi
    {
      echo "<!-- generated from AGENTS.md by agents-system-setup — re-copied on every update. Do not edit directly. -->"
      cat AGENTS.md
    } > CLAUDE.md
    echo "✅ CLAUDE.md copied from AGENTS.md (Windows/non-POSIX path)."
    ;;
esac
