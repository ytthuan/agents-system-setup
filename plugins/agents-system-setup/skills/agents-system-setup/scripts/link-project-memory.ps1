<#
.SYNOPSIS
  Create a thin Claude import adapter without replacing existing files or symlinks.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = (Get-Location).Path
$source = Join-Path $root 'AGENTS.md'
$target = Join-Path $root 'CLAUDE.md'
$sourceItem = Get-Item -LiteralPath $source -Force
if ($sourceItem.PSIsContainer -or ($sourceItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
  throw 'AGENTS.md must be an existing regular file; review symlinks before proceeding.'
}
$utf8 = New-Object Text.UTF8Encoding($false, $true)
$sourceBytes = [IO.File]::ReadAllBytes($source)
$sourceText = $utf8.GetString($sourceBytes)
$versions = [regex]::Matches(
  $sourceText,
  '(?m)^<!-- agents-system-setup:generated-by: (v?\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.+-]+)?) -->\r?$'
)
if ($versions.Count -ne 1) {
  throw 'AGENTS.md must have exactly one valid generated-by stamp.'
}
$content = "<!-- agents-system-setup:generated-by: $($versions[0].Groups[1].Value) -->`n" +
  "<!-- agents-system-setup:memory-adapter: claude-code -->`n`n@AGENTS.md`n"
$bytes = $utf8.GetBytes($content)

if (Test-Path -LiteralPath $target) {
  $existing = Get-Item -LiteralPath $target -Force
  if (-not $existing.PSIsContainer -and
      -not ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -and
      $existing.Length -eq $bytes.Length -and
      [Convert]::ToBase64String([IO.File]::ReadAllBytes($target)) -eq [Convert]::ToBase64String($bytes)) {
    Write-Host 'CLAUDE.md already contains the current import adapter.'
    exit 0
  }
  throw 'CLAUDE.md already exists; propose and approve its migration instead of overwriting it.'
}

$temp = Join-Path $root ('.claude-adapter-' + [IO.Path]::GetRandomFileName())
$tempCreated = $false
try {
  $stream = [IO.File]::Open($temp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
  $tempCreated = $true
  try {
    $stream.Write($bytes, 0, $bytes.Length)
    $stream.Flush()
  } finally {
    $stream.Dispose()
  }
  $currentSource = Get-Item -LiteralPath $source -Force
  if (($currentSource.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
      [Convert]::ToBase64String([IO.File]::ReadAllBytes($source)) -ne [Convert]::ToBase64String($sourceBytes)) {
    throw 'AGENTS.md changed while preparing the adapter; review the new content first.'
  }
  # The two-argument move fails if another writer created the destination.
  [IO.File]::Move($temp, $target)
  $tempCreated = $false
} finally {
  if ($tempCreated) {
    [IO.File]::Delete($temp)
  }
}
Write-Host 'Created CLAUDE.md importing @AGENTS.md; no policy copy or symlink.'
