param(
    [string]$Root = 'D:\AI-Skills',
    [string]$PythonPath = '',
    [int]$DebounceSeconds = 8
)

$ErrorActionPreference = 'Stop'
$utf8Console = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8Console
$OutputEncoding = $utf8Console
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
$logDir = Join-Path $Root '_logs'
$logFile = Join-Path $logDir 'governance-watcher.log'
$statusFile = Join-Path $logDir 'governance-status.json'
$verifyScript = Join-Path $Root 'verify-governance.ps1'
$script:lastVerificationReason = 'process start'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = 'INFO')
    $line = '{0} [{1}] {2}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Level, $Message
    [System.IO.File]::AppendAllText($logFile, $line + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
}

function Write-Status {
    param([string]$State, [int]$ExitCode, [string]$Reason)
    $data = [ordered]@{
        state = $State
        exit_code = $ExitCode
        reason = $Reason
        process_id = $PID
        updated_at = (Get-Date).ToString('o')
        log_file = $logFile
    } | ConvertTo-Json
    [System.IO.File]::WriteAllText($statusFile, $data, [System.Text.UTF8Encoding]::new($false))
}

function Invoke-GovernanceVerification {
    param([string]$Reason)
    $script:lastVerificationReason = $Reason
    Write-Log "Verification started. reason=$Reason"
    Write-Status -State 'running-verification' -ExitCode 0 -Reason $Reason
    try {
        # unittest writes normal progress to stderr. Capture it without turning it into a PowerShell terminating error.
        $previousErrorPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $verifyScript 2>&1
        $exitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousErrorPreference
        foreach ($line in $output) { Write-Log ([string]$line) 'VERIFY' }
        if ($exitCode -ne 0) { throw "verify-governance.ps1 exited with $exitCode" }
        Write-Log 'Verification passed.' 'PASS'
        Write-Status -State 'watching' -ExitCode 0 -Reason $Reason
    }
    catch {
        Write-Log ("Verification failed: " + $_.Exception.Message) 'ERROR'
        Write-Status -State 'watching-after-failure' -ExitCode 1 -Reason $Reason
    }
}

function Test-IgnoredPath {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $true }
    $normalized = $Path.Replace('/', '\')
    # The registry directory is watched only because overrides.json is an input.
    # Generated registry and report files must not trigger another verification loop.
    if ($normalized.IndexOf('\registry\', [System.StringComparison]::OrdinalIgnoreCase) -ge 0 -and -not $normalized.EndsWith('\registry\overrides.json', [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }
    return (
        $normalized -match '\\.git(\\|$)' -or
        $normalized -match '\\__pycache__(\\|$)' -or
        $normalized -match '\\.pytest_cache(\\|$)' -or
        $normalized -match '\\.DS_Store$' -or
        $normalized -match '\\00-skill-router\\references\\generated-catalog\.md$' -or
        $normalized -match '\\desktop\.ini$' -or
        $normalized -match '~$'
    )
}

if (-not (Test-Path -LiteralPath $verifyScript)) {
    Write-Log "Missing verification script: $verifyScript" 'FATAL'
    Write-Status -State 'fatal' -ExitCode 2 -Reason 'missing verification script'
    exit 2
}

if ($PythonPath -and (Test-Path -LiteralPath $PythonPath)) {
    $env:AI_SKILLS_PYTHON = $PythonPath
}

$watchRoots = @(
    (Join-Path $Root 'skills'),
    (Join-Path $Root 'tests'),
    (Join-Path $Root 'scripts'),
    (Join-Path $Root 'registry\overrides.json'),
    'C:\Users\win10\.codex\skills'
)

$watchDirs = New-Object System.Collections.Generic.List[string]
foreach ($item in $watchRoots) {
    if (Test-Path -LiteralPath $item -PathType Container) {
        $watchDirs.Add($item)
    }
    elseif (Test-Path -LiteralPath $item -PathType Leaf) {
        $watchDirs.Add((Split-Path -Parent $item))
    }
}
$watchDirs = @($watchDirs | Sort-Object -Unique)

$watchers = @()
$subscriptions = @()
try {
    foreach ($dir in $watchDirs) {
        $fsw = New-Object System.IO.FileSystemWatcher
        $fsw.Path = $dir
        $fsw.IncludeSubdirectories = $true
        $fsw.NotifyFilter = [System.IO.NotifyFilters]'FileName, DirectoryName, LastWrite, CreationTime, Size'
        $fsw.InternalBufferSize = 32768
        $fsw.EnableRaisingEvents = $true
        $watchers += $fsw
        foreach ($eventName in @('Changed', 'Created', 'Deleted', 'Renamed')) {
            $subscriptions += Register-ObjectEvent -InputObject $fsw -EventName $eventName
        }
        Write-Log "Watching: $dir"
    }

    Write-Log "Watcher started. pid=$PID debounce=${DebounceSeconds}s"
    Write-Status -State 'starting' -ExitCode 0 -Reason 'process start'
    Invoke-GovernanceVerification -Reason 'watcher startup'

    $pending = $false
    $lastRelevantEvent = Get-Date
    $lastHeartbeat = Get-Date
    $changedPaths = New-Object System.Collections.Generic.HashSet[string]

    while ($true) {
        $evt = Wait-Event -Timeout 1
        if ($null -ne $evt) {
            $path = [string]$evt.SourceEventArgs.FullPath
            Remove-Event -EventIdentifier $evt.EventIdentifier -ErrorAction SilentlyContinue
            if (-not (Test-IgnoredPath -Path $path)) {
                [void]$changedPaths.Add($path)
                $pending = $true
                $lastRelevantEvent = Get-Date
            }
        }

        if (((Get-Date) - $lastHeartbeat).TotalSeconds -ge 60) {
            Write-Status -State 'watching' -ExitCode 0 -Reason $script:lastVerificationReason
            $lastHeartbeat = Get-Date
        }

        if ($pending -and ((Get-Date) - $lastRelevantEvent).TotalSeconds -ge $DebounceSeconds) {
            $sample = (@($changedPaths) | Select-Object -First 5) -join '; '
            $count = $changedPaths.Count
            $changedPaths.Clear()
            $pending = $false
            Invoke-GovernanceVerification -Reason "filesystem change count=$count sample=$sample"
        }
    }
}
catch {
    Write-Log ("Watcher crashed: " + $_.Exception.ToString()) 'FATAL'
    Write-Status -State 'crashed' -ExitCode 3 -Reason $_.Exception.Message
    exit 3
}
finally {
    foreach ($sub in $subscriptions) { Unregister-Event -SubscriptionId $sub.Id -ErrorAction SilentlyContinue }
    foreach ($fsw in $watchers) { $fsw.Dispose() }
}