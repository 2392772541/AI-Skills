param(
    [string]$TaskName = 'AI-Skills Governance Watcher',
    [string]$HealthTaskName = 'AI-Skills Governance Healthcheck'
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
& (Join-Path $root 'install-web-console.ps1')
$watcher = Join-Path $root 'scripts\governance-watcher.ps1'
$healthcheck = Join-Path $root 'scripts\governance-healthcheck.ps1'
$python = (Get-Command python -ErrorAction Stop).Source
$userId = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$psExe = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited
$existingWatcher = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingWatcher) { Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue; Start-Sleep -Milliseconds 500 }
$existingHealth = Get-ScheduledTask -TaskName $HealthTaskName -ErrorAction SilentlyContinue
if ($existingHealth) { Stop-ScheduledTask -TaskName $HealthTaskName -ErrorAction SilentlyContinue }
$watcherArgs = '-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "{0}" -Root "{1}" -PythonPath "{2}"' -f $watcher, $root, $python
$watcherAction = New-ScheduledTaskAction -Execute $psExe -Argument $watcherArgs -WorkingDirectory $root
$watcherTrigger = New-ScheduledTaskTrigger -AtLogOn -User $userId
$watcherSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $watcherAction -Trigger $watcherTrigger -Principal $principal -Settings $watcherSettings -Description 'Continuously verifies and refreshes the local AI Skills registry after logon and file changes.' -Force | Out-Null
$healthArgs = '-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "{0}" -Root "{1}" -WatcherTaskName "{2}" -WebTaskName "AI-Skills Web Console"' -f $healthcheck, $root, $TaskName
$healthAction = New-ScheduledTaskAction -Execute $psExe -Argument $healthArgs -WorkingDirectory $root
$healthTrigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddMinutes(1)) -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration (New-TimeSpan -Days 3650)
$healthSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $HealthTaskName -Action $healthAction -Trigger $healthTrigger -Principal $principal -Settings $healthSettings -Description 'Checks both AI Skills watcher and web console every two minutes and restarts unhealthy processes.' -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName; Start-ScheduledTask -TaskName $HealthTaskName; Start-Sleep -Seconds 2
Write-Host '[PASS] Governance watcher, web console, and healthcheck are installed.' -ForegroundColor Green