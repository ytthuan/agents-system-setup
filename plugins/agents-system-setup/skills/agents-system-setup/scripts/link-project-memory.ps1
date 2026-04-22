<#
.SYNOPSIS
  Keep CLAUDE.md in sync with AGENTS.md on Windows.
  Tries a symlink first (requires Developer Mode or admin); falls back to copy
  with a regenerable header so re-running the script keeps them in sync.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath 'AGENTS.md')) {
  Write-Error 'AGENTS.md not found in current directory — generate it first.'
  exit 1
}

# If existing CLAUDE.md is a symlink to AGENTS.md, we're done.
$existing = Get-Item -LiteralPath 'CLAUDE.md' -ErrorAction SilentlyContinue
if ($existing -and $existing.LinkType -eq 'SymbolicLink' -and $existing.Target -contains 'AGENTS.md') {
  Write-Host '✅ CLAUDE.md already symlinked to AGENTS.md.'
  exit 0
}

# Back up an existing real file before replacing.
if ($existing -and -not $existing.LinkType) {
  Copy-Item -LiteralPath 'CLAUDE.md' -Destination 'CLAUDE.md.bak' -Force
  Write-Host 'ℹ️  Existing CLAUDE.md backed up to CLAUDE.md.bak'
  Remove-Item -LiteralPath 'CLAUDE.md' -Force
}

# Try symlink (Developer Mode or admin).
$symlinked = $false
try {
  New-Item -ItemType SymbolicLink -Path 'CLAUDE.md' -Target 'AGENTS.md' | Out-Null
  $symlinked = $true
  Write-Host '✅ CLAUDE.md → AGENTS.md (symlink).'
} catch {
  Write-Host 'ℹ️  Symlink not permitted — falling back to copy with header.'
}

if (-not $symlinked) {
  $header = '<!-- generated from AGENTS.md by agents-system-setup — re-copied on every update. Do not edit directly. -->' + [Environment]::NewLine
  $body   = Get-Content -LiteralPath 'AGENTS.md' -Raw
  [IO.File]::WriteAllText(
    (Join-Path (Get-Location) 'CLAUDE.md'),
    ($header + $body),
    (New-Object Text.UTF8Encoding($false))
  )
  Write-Host '✅ CLAUDE.md copied from AGENTS.md (with regen header).'
}
