<#
.SYNOPSIS
  Initialize a git repo for the current project after agents scaffolding.
  Windows-native equivalent of git-init.sh.

.PARAMETER GitignoreTemplate
  Optional path to a .gitignore template to copy.
#>
[CmdletBinding()]
param(
  [string]$GitignoreTemplate
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw 'git not found on PATH'
}

if (Test-Path -LiteralPath '.git' -PathType Container) {
  Write-Host '✅ .git already present — skipping init.'
  exit 0
}

git init -b main *> $null

if (-not (Test-Path -LiteralPath '.gitignore')) {
  if ($GitignoreTemplate -and (Test-Path -LiteralPath $GitignoreTemplate)) {
    Copy-Item -LiteralPath $GitignoreTemplate -Destination '.gitignore'
  } else {
    $content = @'
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

# Agent runtime local state
.copilot/session-state/
.claude/.cache/
.claude/sessions/
.opencode/.cache/
.opencode/sessions/
'@
    [IO.File]::WriteAllText(
      (Join-Path (Get-Location) '.gitignore'),
      $content,
      (New-Object Text.UTF8Encoding($false))
    )
  }
  Write-Host '✅ Wrote .gitignore'
}

# Also drop a .gitattributes for cross-OS line endings, if missing.
$attrTemplate = Join-Path $PSScriptRoot '..\assets\gitattributes.template'
if ((-not (Test-Path -LiteralPath '.gitattributes')) -and (Test-Path -LiteralPath $attrTemplate)) {
  Copy-Item -LiteralPath $attrTemplate -Destination '.gitattributes'
  Write-Host '✅ Wrote .gitattributes (LF for source, CRLF for *.ps1)'
}

git add -A *> $null
git -c user.email='agents@local' -c user.name='agents-system-setup' `
    commit -m @'
chore: scaffold multi-platform agent system

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
'@ *> $null

Write-Host '✅ git initialized on branch main with initial commit.'
