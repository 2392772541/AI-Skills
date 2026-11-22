param(
    [string]$TaskName = 'AI-Skills Governance Watcher',
    [string]$HealthTaskName = 'AI-Skills Governance Healthcheck',
    [string]$WebTaskName = 'AI-Skills Web Console'
)
$ErrorActionPreference = 'Stop'
foreach ($name in @($HealthTaskName,$WebTaskName,$TaskName)) { $task=Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue; if($task){Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue;Unregister-ScheduledTask -TaskName $name -Confirm:$false;Write-Host "[PASS] Removed: $name" -ForegroundColor Green}else{Write-Host "[PASS] Already absent: $name"} }