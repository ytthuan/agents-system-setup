#!/usr/bin/env pwsh
# PowerShell wrapper around scripts/_validate.py.
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$python = $null
foreach ($cand in @('python3', 'python')) {
    if (Get-Command $cand -ErrorAction SilentlyContinue) {
        $python = $cand
        break
    }
}
if (-not $python) {
    Write-Error 'Python 3 is required (python3 or python on PATH).'
    exit 2
}

# Best-effort PyYAML install
try {
    & $python -c "import yaml" 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        & $python -m pip install --quiet --user --disable-pip-version-check pyyaml 2>$null | Out-Null
    }
} catch {}

& $python scripts/_validate.py
$status = $LASTEXITCODE

# Line-ending checks
$fail = 0
foreach ($f in Get-ChildItem -Recurse -File -Filter '*.sh' -Exclude '.git') {
    $bytes = [IO.File]::ReadAllBytes($f.FullName)
    if ($bytes -contains 0x0D) {
        Write-Host "✗ $($f.FullName) contains CRLF (must be LF)"
        $fail = 1
    }
}
foreach ($f in Get-ChildItem -Recurse -File -Filter '*.ps1' -Exclude '.git') {
    $bytes = [IO.File]::ReadAllBytes($f.FullName)
    if (-not ($bytes -contains 0x0D)) {
        Write-Host "⚠ $($f.FullName) is LF (will be CRLF on Windows checkout via .gitattributes)"
    }
}

if ($fail -ne 0) { exit 1 }
exit $status
