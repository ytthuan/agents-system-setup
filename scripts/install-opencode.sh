#!/usr/bin/env bash
# Install agents-system-setup as an OpenCode skill.
# OpenCode plugins are JS/TS hooks, so skills are installed by copy/symlink.
set -euo pipefail

SCOPE="${1:-project}"   # project | global
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)/plugins/agents-system-setup/skills/agents-system-setup"

case "$SCOPE" in
  project)
    DEST_BASE="$(pwd)/.opencode/skills"
    ;;
  global)
    DEST_BASE="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills"
    ;;
  *)
    echo "Usage: $0 [project|global]"
    exit 1
    ;;
esac

mkdir -p "$DEST_BASE"
DEST="$DEST_BASE/agents-system-setup"

if [[ -e "$DEST" ]]; then
  echo "Removing existing $DEST"
  rm -rf "$DEST"
fi

cp -R "$SRC_DIR" "$DEST"
echo "Installed agents-system-setup → $DEST"
echo "Restart opencode to pick up the skill."
