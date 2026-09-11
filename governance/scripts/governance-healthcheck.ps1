param(
    [string]$Root = 'D:\AI-Skills',
    [string]$WatcherTaskName = 'AI-Skills Governance Watcher',
    [string]$WebTaskName = 'AI-Skills Web Console',
    [int]$WebPort = 8765,
    [int]$StaleMinutes = 5
)
$ErrorActionPreference = 'Stop'
$logDir = Join-Path $Root '_logs'
$logFile = Join-Path $logDir 'governance-healthcheck.log'
$statusFile = Join-Path $logDir 'governance-status.json'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
function Write-HealthLog([string]$Message) { $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message; [IO.File]::AppendAllText($logFile, $line + [Environment]::NewLine, [Text.UTF8Encoding]::new($false)) }

$task = Get-ScheduledTask -TaskName $WatcherTaskName -ErrorAction SilentlyContinue
if (-not $task) { Write-HealthLog "FAIL missing watcher task: $WatcherTaskName" }
else {
    $needsRestart = $task.State -ne 'Running'; $reason = "task state=$($task.State)"
    if (-not $needsRestart) {
        if (-not (Test-Path -LiteralPath $statusFile)) { $needsRestart = $true; $reason = 'status file missing' }
        else {
            try {
                $status = Get-Content -LiteralPath $statusFile -Raw -Encoding UTF8 | ConvertFrom-Json
                $updated = [DateTimeOffset]::Parse([string]$status.updated_at).LocalDateTime
                $age = ((Get-Date) - $updated).TotalMinutes
                $processAlive = $null -ne (Get-Process -Id ([int]$status.process_id) -ErrorAction SilentlyContinue)
                if ($status.state -eq 'crashed' -or -not $processAlive -or $age -gt $StaleMinutes) { $needsRestart = $true; $reason = "state=$($status.state) processAlive=$processAlive ageMinutes=$([Math]::Round($age,1))" }
            } catch { $needsRestart = $true; $reason = 'invalid status file: ' + $_.Exception.Message }
        }
    }
    if ($needsRestart) { Stop-ScheduledTask -TaskName $WatcherTaskName -ErrorAction SilentlyContinue; Start-ScheduledTask -TaskName $WatcherTaskName; Write-HealthLog "RESTART watcher $reason" }
    else { Write-HealthLog 'PASS watcher healthy' }
}

$webTask = Get-ScheduledTask -TaskName $WebTaskName -ErrorAction SilentlyContinue
if (-not $webTask) { Write-HealthLog "FAIL missing web task: $WebTaskName" }
else {
    $webHealthy = $false
    if ($webTask.State -eq 'Running') { try { $response = Invoke-RestMethod -Uri "http://127.0.0.1:$WebPort/api/health" -TimeoutSec 3; $webHealthy = $response.ok -eq $true } catch { $webHealthy = $false } }
    if (-not $webHealthy) { Stop-ScheduledTask -TaskName $WebTaskName -ErrorAction SilentlyContinue; Start-ScheduledTask -TaskName $WebTaskName; Write-HealthLog "RESTART web console state=$($webTask.State) port=$WebPort" }
    else { Write-HealthLog 'PASS web console healthy' }
}