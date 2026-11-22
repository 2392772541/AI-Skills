$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$python = if ($env:AI_SKILLS_PYTHON -and (Test-Path -LiteralPath $env:AI_SKILLS_PYTHON)) { $env:AI_SKILLS_PYTHON } else { (Get-Command python -ErrorAction Stop).Source }
$creatorValidator = 'C:\Users\win10\.codex\skills\.system\skill-creator\scripts\quick_validate.py'

function Invoke-Checked {
    param([string]$Label, [scriptblock]$Command)
    Write-Host "[RUN] $Label" -ForegroundColor Cyan
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
    Write-Host "[PASS] $Label" -ForegroundColor Green
}

$pythonFiles = @(Get-ChildItem -LiteralPath (Join-Path $root 'scripts') -Filter '*.py' | ForEach-Object FullName)
$pythonFiles += @(Get-ChildItem -LiteralPath (Join-Path $root 'skills\skill-product-manager\scripts') -Filter '*.py' | ForEach-Object FullName)

Invoke-Checked 'Python syntax' { & $python -m py_compile @pythonFiles }
Invoke-Checked 'Unit tests' { & $python -m unittest discover -s (Join-Path $root 'tests') -p 'test_*.py' -v }
Invoke-Checked 'Skill structure' { & $python $creatorValidator (Join-Path $root 'skills\skill-product-manager') }
Invoke-Checked 'Build registry' { & $python (Join-Path $root 'scripts\skillctl.py') build }
Invoke-Checked 'Strict audit' { & $python (Join-Path $root 'scripts\audit_skills.py') --registry (Join-Path $root 'registry\skills.json') --strict --output (Join-Path $root '_reports\skill-audit.json') --markdown (Join-Path $root '_reports\skill-audit.md') }
Invoke-Checked 'Routing regression' { & $python (Join-Path $root 'scripts\skillctl.py') test }
Invoke-Checked 'Router catalog' { & $python (Join-Path $root 'scripts\generate_router_catalog.py') --registry (Join-Path $root 'registry\skills.json') --output (Join-Path $root 'skills\00-skill-router\references\generated-catalog.md') }
Invoke-Checked 'Final registry refresh' { & $python (Join-Path $root 'scripts\skillctl.py') build }

Write-Host '[PASS] Skill governance system verified.' -ForegroundColor Green