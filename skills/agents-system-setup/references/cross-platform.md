# Cross-Platform Compatibility (Linux, macOS, Windows)

This skill must operate identically on **Linux**, **macOS**, and **Windows**. Generated projects must also work for users on any of those OSes.

## OS Detection (use first, branch later)

```bash
# POSIX shells (bash on macOS/Linux, Git Bash, WSL):
case "$(uname -s 2>/dev/null)" in
  Darwin)            OS=macos ;;
  Linux)             OS=linux ;;
  MINGW*|MSYS*|CYGWIN*) OS=windows-bash ;;  # Git Bash / WSL
  *)                 OS=unknown ;;
esac
```

```powershell
# PowerShell (Windows native, also works on macOS/Linux pwsh):
$os = if ($IsWindows) { 'windows' } elseif ($IsMacOS) { 'macos' } elseif ($IsLinux) { 'linux' } else { 'unknown' }
```

## Script Selection Rule

Every executable bundled with this skill ships in **two forms**:

| Purpose | POSIX | Windows native |
|---|---|---|
| Init git repo | `scripts/git-init.sh` | `scripts/git-init.ps1` |
| Link project memory | `scripts/link-project-memory.sh` | `scripts/link-project-memory.ps1` |

**Selection logic (the agent runs this, not the user):**

1. If `bash` is available AND OS is `macos` / `linux` / `windows-bash` → use `.sh`.
2. Else (Windows native PowerShell) → use `.ps1` via `pwsh -File <script>` (PowerShell 7+) or `powershell.exe -ExecutionPolicy Bypass -File <script>` (Windows PowerShell 5.1).
3. Never invoke a `.sh` from `cmd.exe` directly.

## Path Conventions in Generated Files

- **In Markdown** (`AGENTS.md`, `SKILL.md`, agent files): always use **forward slashes** (`/`). They render and are interpreted correctly on all OSes.
- **In commands inside docs**: prefer cross-shell forms or document both:
  - macOS/Linux: `bash scripts/foo.sh`
  - Windows: `pwsh scripts\foo.ps1` (or `pwsh -File ./scripts/foo.ps1`)
- **In Directory Architecture globs**: forward slashes only (`src/**`, `tests/**`).

## Line Endings

- Bundle a `.gitattributes` (see `assets/gitattributes.template`) with `* text=auto eol=lf` for source and `*.ps1 text eol=crlf` for PowerShell.
- Without this, Windows users will silently get CRLF in `.sh` and break execution.

## Symlink Caveats (Windows)

- `ln -s` is unreliable on Windows: requires Developer Mode or admin, and Git for Windows often replaces symlinks with text-stub copies.
- **Strategy**: on Windows, never symlink — always **copy with regenerable header**. The `link-project-memory.*` scripts already implement this branching.

## File Modes

- Windows ignores POSIX execute bits. Always invoke scripts via interpreter (`bash script.sh`, `pwsh script.ps1`) — never rely on `./script` working everywhere.

## Encoding

- Always write files as **UTF-8 without BOM**. PowerShell 5.1's default `Out-File` uses UTF-16 — use `Set-Content -Encoding utf8` or `[IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($false))`.

## Tooling Availability Checks

Before invoking, verify the tool exists:

```bash
command -v git >/dev/null 2>&1 || { echo "git not found"; exit 1; }
```

```powershell
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git not found' }
```

## Anti-patterns

- Using `cp` / `rm` / `chmod` in instructions a Windows-PowerShell-only user will run.
- Hardcoded `/tmp` (use `TMPDIR` / `[IO.Path]::GetTempPath()`).
- `bash`-only constructs (`<<<`, `[[ ]]`, process substitution) inside scripts the user might run via `sh`.
- Symlinks on Windows.
- BOM in generated config files (breaks `opencode.json` parsing in some runtimes).
