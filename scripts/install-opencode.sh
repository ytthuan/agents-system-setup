#!/usr/bin/env bash
# Install the OpenCode skill and /agents-system-setup command.
set -euo pipefail

SCOPE="${1:-project}"   # project | global
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)/plugins/agents-system-setup/skills/agents-system-setup"

case "$SCOPE" in
  project)
    CONFIG_BASE="$(pwd)/.opencode"
    STATE_BASE="$(pwd)/.agents-system-setup/installer-backups"
    ;;
  global)
    CONFIG_BASE="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
    STATE_BASE="$CONFIG_BASE/.agents-system-setup/installer-backups"
    ;;
  *)
    echo "Usage: $0 [project|global]"
    exit 1
    ;;
esac

DEST="$CONFIG_BASE/skills/agents-system-setup"
COMMAND="$CONFIG_BASE/commands/agents-system-setup.md"
for path in "$CONFIG_BASE" "$CONFIG_BASE/skills" "$CONFIG_BASE/commands" \
  "$(dirname "$STATE_BASE")" "$STATE_BASE" "$DEST" "$COMMAND"; do
  if [[ -L "$path" ]]; then
    echo "Refusing symlink: $path" >&2
    exit 1
  fi
done
if [[ -e "$DEST" && ! -d "$DEST" ]] || [[ -e "$COMMAND" && ! -f "$COMMAND" ]]; then
  echo "Installation destination has an unexpected file type." >&2
  exit 1
fi

mkdir -p "$STATE_BASE" "$CONFIG_BASE/skills" "$CONFIG_BASE/commands"
BACKUP="$(mktemp -d "$STATE_BASE/install-XXXXXXXX")"
# Stage the complete install before replacing anything. Backups are outside
# skill/command discovery roots so an old SKILL.md cannot become a duplicate.
cp -R "$SRC_DIR" "$BACKUP/new-skill"
cp "$SRC_DIR/assets/agents-system-setup.command.md" "$BACKUP/new-command.md"
MOVED_SKILL=0 MOVED_COMMAND=0 INSTALLED_SKILL=0 INSTALLED_COMMAND=0
restore_on_error() {
  local status=$?
  if [[ $status -ne 0 ]]; then
    local recovery=0
    if [[ $INSTALLED_COMMAND -eq 1 ]]; then
      mv "$COMMAND" "$BACKUP/failed-command.md" || recovery=1
    fi
    if [[ $INSTALLED_SKILL -eq 1 ]]; then
      mv "$DEST" "$BACKUP/failed-skill" || recovery=1
    fi
    if [[ $MOVED_SKILL -eq 1 ]]; then
      if [[ -e "$DEST" || -L "$DEST" ]]; then
        recovery=1
      else
        mv "$BACKUP/skill" "$DEST" || recovery=1
      fi
    fi
    if [[ $MOVED_COMMAND -eq 1 ]]; then
      if [[ -e "$COMMAND" || -L "$COMMAND" ]]; then
        recovery=1
      else
        mv "$BACKUP/command.md" "$COMMAND" || recovery=1
      fi
    fi
    if [[ $recovery -eq 0 ]]; then
      echo "Install failed; prior files restored. Recovery files: $BACKUP" >&2
    else
      echo "Install failed; manual recovery needed from $BACKUP" >&2
    fi
  fi
  return "$status"
}
trap restore_on_error EXIT
if [[ -e "$DEST" ]]; then
  mv "$DEST" "$BACKUP/skill"
  MOVED_SKILL=1
fi
if [[ -e "$COMMAND" ]]; then
  mv "$COMMAND" "$BACKUP/command.md"
  MOVED_COMMAND=1
fi
mv "$BACKUP/new-skill" "$DEST"
INSTALLED_SKILL=1
mv "$BACKUP/new-command.md" "$COMMAND"
INSTALLED_COMMAND=1
trap - EXIT
echo "Installed agents-system-setup → $DEST"
echo "Previous install (when present): $BACKUP/skill and $BACKUP/command.md"
echo "To restore: move the current skill/command aside, then move those backups to their original paths."
echo "OpenCode reloads automatically; use /reload if needed."
echo "Try: /agents-system-setup migrate monolithic --dry-run"
