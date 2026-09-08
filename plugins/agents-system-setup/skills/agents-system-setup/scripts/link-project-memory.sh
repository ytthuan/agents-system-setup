#!/usr/bin/env bash
# Create a thin Claude import adapter; existing content requires reviewed migration.
set -euo pipefail

command -v python3 >/dev/null 2>&1 || {
  echo "Python 3 is required to create the memory adapter safely." >&2
  exit 1
}

python3 - <<'PY'
import os
from pathlib import Path
import re
import sys
import tempfile

source = Path("AGENTS.md")
target = Path("CLAUDE.md")
if source.is_symlink() or not source.is_file():
    sys.exit("AGENTS.md must be an existing regular file; review symlinks before proceeding.")
source_bytes = source.read_bytes()
try:
    source_text = source_bytes.decode("utf-8")
except UnicodeDecodeError:
    sys.exit("AGENTS.md is not valid UTF-8.")
versions = re.findall(
    r"(?m)^<!-- agents-system-setup:generated-by: "
    r"(v?\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.+-]+)?) -->\r?$",
    source_text,
)
if len(versions) != 1:
    sys.exit("AGENTS.md must have exactly one valid generated-by stamp.")
content = (
    f"<!-- agents-system-setup:generated-by: {versions[0]} -->\n"
    "<!-- agents-system-setup:memory-adapter: claude-code -->\n"
    "\n@AGENTS.md\n"
).encode("utf-8")

if target.exists() or target.is_symlink():
    if not target.is_symlink() and target.is_file() and target.read_bytes() == content:
        print("CLAUDE.md already contains the current import adapter.")
        sys.exit(0)
    sys.exit("CLAUDE.md already exists; propose and approve its migration instead of overwriting it.")

with tempfile.NamedTemporaryFile(prefix=".claude-adapter-", dir=".") as draft:
    draft.write(content)
    draft.flush()
    if source.is_symlink() or source.read_bytes() != source_bytes:
        sys.exit("AGENTS.md changed while preparing the adapter; review the new content first.")
    try:
        # Linking publishes a complete file atomically and never replaces a raced destination.
        os.link(draft.name, target)
    except FileExistsError:
        sys.exit("CLAUDE.md appeared during generation; it was not replaced.")
print("Created CLAUDE.md importing @AGENTS.md; no policy copy or symlink.")
PY
