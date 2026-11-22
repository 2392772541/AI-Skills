param(
    [string]$TaskName = 'AI-Skills Governance Watcher',
    [string]$HealthTaskName = 'AI-Skills Governance Healthcheck',
    [string]$WebTaskName = 'AI-Skills Web Console'
)
$ErrorActionPreference='Stop';$root=$PSScriptRoot;$failed=$false
foreach($name in @($TaskName,$HealthTaskName,$WebTaskName)){ $task=Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue;if(-not $task){Write-Host "[FAIL] Missing task: $name" -ForegroundColor Red;$failed=$true;continue};$info=Get-ScheduledTaskInfo -TaskName $name;Write-Host "Task: $name";Write-Host "State: $($task.State)";Write-Host "Last run: $($info.LastRunTime)";Write-Host "Last result: $($info.LastTaskResult)";Write-Host '' }
try{$web=Invoke-RestMethod -Uri 'http://127.0.0.1:8765/api/health' -TimeoutSec 3;Write-Host "Web: http://127.0.0.1:8765 [healthy, pid=$($web.pid)]"}catch{Write-Host 'Web: http://127.0.0.1:8765 [unreachable]' -ForegroundColor Red;$failed=$true}
$statusFile=Join-Path $root '_logs\governance-status.json';if(Test-Path $statusFile){Write-Host "`nWatcher status:";Get-Content $statusFile -Encoding UTF8}
if($failed){exit 1}