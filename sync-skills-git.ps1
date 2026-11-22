$ErrorActionPreference = 'Stop'
$python = (Get-Command python -ErrorAction Stop).Source
& $python (Join-Path $PSScriptRoot 'scripts\skillctl.py') git-sync
if ($LASTEXITCODE -ne 0) { throw 'Skills Git synchronization failed. Existing skills were not modified.' }
