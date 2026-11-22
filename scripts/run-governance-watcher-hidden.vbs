Option Explicit
Dim shell, command
Set shell = CreateObject("WScript.Shell")
command = """C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"" -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File ""D:\AI-Skills\scripts\governance-watcher.ps1"" -Root ""D:\AI-Skills"" -PythonPath ""E:\app\Miniconda\python.exe"""
shell.Run command, 0, True
