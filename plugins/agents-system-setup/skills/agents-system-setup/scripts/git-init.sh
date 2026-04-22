#!/usr/bin/env bash
# git-init.sh — initialize a git repo for the current project after agents scaffolding.
# Usage: bash scripts/git-init.sh [<lang-block-path>]
set -euo pipefail

if [ -d .git ]; then
  echo "✅ .git already present — skipping init."
  exit 0
fi

git init -b main >/dev/null

if [ ! -f .gitignore ]; then
  TEMPLATE="${1:-}"
  if [ -n "$TEMPLATE" ] && [ -f "$TEMPLATE" ]; then
    cp "$TEMPLATE" .gitignore
  else
    cat > .gitignore <<'EOF'
# OS / editor
.DS_Store
Thumbs.db
desktop.ini
*.log
*.bak
.env
.env.local
.env.*.local
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json
.idea/
*.swp

# Common build / dep dirs
node_modules/
dist/
build/
.venv/
__pycache__/
*.pyc
target/
bin/
obj/

# Agent runtime local state — keep config, ignore caches/sessions
.copilot/session-state/
.claude/.cache/
.claude/sessions/
.opencode/.cache/
.opencode/sessions/

# Generated project memory (re-derived from AGENTS.md on Windows)
# Comment out if you commit CLAUDE.md as a copy.
# CLAUDE.md
EOF
  fi
  echo "✅ Wrote .gitignore"
fi

git add -A
# Also drop a .gitattributes for cross-OS line endings (LF for source, CRLF for *.ps1).
ATTR_TEMPLATE="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)/assets/gitattributes.template"
if [ ! -f .gitattributes ] && [ -f "$ATTR_TEMPLATE" ]; then
  cp "$ATTR_TEMPLATE" .gitattributes
  git add .gitattributes
  echo "✅ Wrote .gitattributes"
fi

git -c user.email="agents@local" -c user.name="agents-system-setup" \
    commit -m "chore: scaffold multi-platform agent system

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" >/dev/null

echo "✅ git initialized on branch main with initial commit."
