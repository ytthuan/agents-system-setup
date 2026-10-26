#!/usr/bin/env pwsh
# Install the OpenCode skill and /agents-system-setup command with backups.
param(
    [ValidateSet('project','global')]
    [string]$Scope = 'project'
)

$ErrorActionPreference = 'Stop'
$SrcDir = Join-Path (Split-Path $PSScriptRoot -Parent) 'plugins/agents-system-setup/skills/agents-system-setup'

switch ($Scope) {
    'project' {
        $ConfigBase = Join-Path (Get-Location) '.opencode'
        $StateBase = Join-Path (Get-Location) '.agents-system-setup/installer-backups'
    }
    'global'  {
        $cfg = $env:XDG_CONFIG_HOME
        if (-not $cfg) { $cfg = Join-Path $HOME '.config' }
        $ConfigBase = Join-Path $cfg 'opencode'
        $StateBase = Join-Path $ConfigBase '.agents-system-setup/installer-backups'
    }
}

$SkillBase = Join-Path $ConfigBase 'skills'
$CommandBase = Join-Path $ConfigBase 'commands'
$Dest = Join-Path $SkillBase 'agents-system-setup'
$Command = Join-Path $CommandBase 'agents-system-setup.md'
foreach ($path in @($ConfigBase, $SkillBase, $CommandBase, (Split-Path $StateBase -Parent), $StateBase, $Dest, $Command)) {
    $item = Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
    if ($item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Refusing symlink/reparse point: $path"
    }
}
if (((Test-Path -LiteralPath $Dest) -and -not (Test-Path -LiteralPath $Dest -PathType Container)) -or
    ((Test-Path -LiteralPath $Command) -and -not (Test-Path -LiteralPath $Command -PathType Leaf))) {
    throw 'Installation destination has an unexpected file type.'
}
New-Item -ItemType Directory -Force -Path $StateBase, $SkillBase, $CommandBase | Out-Null
$Backup = Join-Path $StateBase ('install-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $Backup | Out-Null
Copy-Item -Recurse -LiteralPath $SrcDir -Destination (Join-Path $Backup 'new-skill')
Copy-Item -LiteralPath (Join-Path $SrcDir 'assets/agents-system-setup.command.md') -Destination (Join-Path $Backup 'new-command.md')
$MovedSkill = $false
$MovedCommand = $false
$InstalledSkill = $false
$InstalledCommand = $false
try {
    if (Test-Path -LiteralPath $Dest) {
        Move-Item -LiteralPath $Dest -Destination (Join-Path $Backup 'skill')
        $MovedSkill = $true
    }
    if (Test-Path -LiteralPath $Command) {
        Move-Item -LiteralPath $Command -Destination (Join-Path $Backup 'command.md')
        $MovedCommand = $true
    }
    Move-Item -LiteralPath (Join-Path $Backup 'new-skill') -Destination $Dest
    $InstalledSkill = $true
    Move-Item -LiteralPath (Join-Path $Backup 'new-command.md') -Destination $Command
    $InstalledCommand = $true
} catch {
    $InstallError = $_
    $RecoveryFailed = $false
    $RecoverySteps = @(
        @{ Enabled = $InstalledCommand; From = $Command; To = (Join-Path $Backup 'failed-command.md') }
        @{ Enabled = $InstalledSkill; From = $Dest; To = (Join-Path $Backup 'failed-skill') }
        @{ Enabled = $MovedSkill; From = (Join-Path $Backup 'skill'); To = $Dest }
        @{ Enabled = $MovedCommand; From = (Join-Path $Backup 'command.md'); To = $Command }
    )
    foreach ($step in $RecoverySteps) {
        if (-not $step.Enabled) { continue }
        try {
            if (Get-Item -LiteralPath $step.To -Force -ErrorAction SilentlyContinue) {
                throw "Recovery destination already exists: $($step.To)"
            }
            Move-Item -LiteralPath $step.From -Destination $step.To
        } catch {
            $RecoveryFailed = $true
            Write-Warning "Recovery step failed: $($_.Exception.Message)"
        }
    }
    if ($RecoveryFailed) {
        Write-Warning "Install failed; manual recovery needed from $Backup"
    } else {
        Write-Host "Install failed; prior files restored. Recovery files: $Backup"
    }
    throw $InstallError
}
Write-Host "Installed agents-system-setup -> $Dest"
Write-Host "Previous install (when present): $Backup/skill and $Backup/command.md"
Write-Host 'To restore: move the current skill/command aside, then move those backups to their original paths.'
Write-Host 'OpenCode reloads automatically; use /reload if needed.'
Write-Host 'Try: /agents-system-setup migrate monolithic --dry-run'
