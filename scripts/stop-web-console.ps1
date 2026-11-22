$ErrorActionPreference = 'SilentlyContinue'

$TaskName = 'AI-Skills Web Console'
$Port = 8765

# 1. 尝试结束计划任务
Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
& C:\Windows\System32\schtasks.exe /End /TN $TaskName 2>$null

# 2. 查找并杀死相关的 python/pythonw 进程
$serverScript = "D:\AI-Skills\web\server.py"
$procs = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*$serverScript*" -or ($_.CommandLine -like "*AI-Skills*" -and $_.CommandLine -like "*server.py*")
}
foreach ($p in $procs) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}

# 3. 检查 8765 端口监听者
$conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($conns) {
    foreach ($conn in $conns) {
        if ($conn.OwningProcess -gt 4) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "AI-Skills Web Console stopped."
exit 0
