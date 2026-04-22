#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
& python3 (Join-Path $RepoRoot 'scripts/_bump_version.py') @args
exit $LASTEXITCODE
