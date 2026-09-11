Option Explicit
Dim shell, command
Set shell = CreateObject("WScript.Shell")
command = """C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"" -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ""D:\AI-Skills\scripts\governance-healthcheck.ps1"" -Root ""D:\AI-Skills"" -WatcherTaskName ""AI-Skills Governance Watcher"" -WebTaskName ""AI-Skills Web Console"""
shell.Run command, 0, True
