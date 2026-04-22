#!/usr/bin/env bash
# POSIX wrapper around scripts/_validate.py.
# Also performs line-ending checks that need git/file metadata.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

python_bin=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    python_bin="$cand"
    break
  fi
done
if [[ -z "$python_bin" ]]; then
  echo "[FAIL] Python 3 is required (python3 or python on PATH)." >&2
  exit 2
fi

# Try to install PyYAML lazily; fall back to ad-hoc parser inside _validate.py
"$python_bin" -c "import yaml" 2>/dev/null || \
  "$python_bin" -m pip install --quiet --user --disable-pip-version-check pyyaml 2>/dev/null || true

"$python_bin" scripts/_validate.py
status=$?

# Line-ending policy: *.sh must be LF, *.ps1 must be CRLF (per .gitattributes).
fail=0
while IFS= read -r -d '' f; do
  if grep -qU $'\r' "$f"; then
    echo "[FAIL] $f contains CRLF (must be LF)"
    fail=1
  fi
done < <(find . -type f -name '*.sh' -not -path './.git/*' -print0)

# .ps1 CRLF check is only enforceable on a freshly checked-out tree; on macOS/Linux
# editors typically save LF, and git normalizes on commit/checkout. We warn instead.
while IFS= read -r -d '' f; do
  if ! grep -qU $'\r' "$f"; then
    echo "[WARN] $f is LF (will be CRLF on Windows checkout via .gitattributes)"
  fi
done < <(find . -type f -name '*.ps1' -not -path './.git/*' -print0)

if [[ $fail -ne 0 ]]; then
  exit 1
fi
exit $status
