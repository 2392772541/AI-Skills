param(
    [string]$TaskName = 'AI-Skills Web Console',
    [int]$Port = 8765
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$server = Join-Path $root 'web\server.py'
$python = (Get-Command python -ErrorAction Stop).Source
$pythonw = Join-Path (Split-Path -Parent $python) 'pythonw.exe'
if (-not (Test-Path -LiteralPath $pythonw)) { $pythonw = $python }
if (-not (Test-Path -LiteralPath $server)) { throw "Missing web server: $server" }
$userId = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) { Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue; Start-Sleep -Milliseconds 500 }
$action = New-ScheduledTaskAction -Execute $pythonw -Argument ('"{0}"' -f $server) -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $userId
$principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Local AI Skills web console on http://127.0.0.1:$Port" -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName
$deadline = (Get-Date).AddSeconds(20)
do {
    Start-Sleep -Milliseconds 500
    try { $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 2 } catch { $health = $null }
} while (-not $health.ok -and (Get-Date) -lt $deadline)
if (-not $health.ok) { throw "Web console did not become healthy on port $Port" }
Write-Host '[PASS] Skill manager web console installed and started.' -ForegroundColor Green
Write-Host "URL: http://127.0.0.1:$Port"
Write-Host "Task: $TaskName"
Write-Host "PID: $($health.pid)"