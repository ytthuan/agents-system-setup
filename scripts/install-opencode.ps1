#!/usr/bin/env pwsh
# Install agents-system-setup as an OpenCode skill on Windows / cross-platform PowerShell.
param(
    [ValidateSet('project','global')]
    [string]$Scope = 'project'
)

$ErrorActionPreference = 'Stop'
$SrcDir = Join-Path (Split-Path $PSScriptRoot -Parent) 'skills/agents-system-setup'

switch ($Scope) {
    'project' { $DestBase = Join-Path (Get-Location) '.opencode/skills' }
    'global'  {
        $cfg = $env:XDG_CONFIG_HOME
        if (-not $cfg) { $cfg = Join-Path $HOME '.config' }
        $DestBase = Join-Path $cfg 'opencode/skills'
    }
}

New-Item -ItemType Directory -Force -Path $DestBase | Out-Null
$Dest = Join-Path $DestBase 'agents-system-setup'

if (Test-Path $Dest) {
    Write-Host "Removing existing $Dest"
    Remove-Item -Recurse -Force $Dest
}

Copy-Item -Recurse -Path $SrcDir -Destination $Dest
Write-Host "Installed agents-system-setup -> $Dest"
Write-Host "Restart opencode to pick up the skill."
