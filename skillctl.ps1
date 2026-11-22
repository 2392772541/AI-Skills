param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('build','audit','route','compare','promote','test')]
    [string]$Command,

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

$python = 'python'
$entry = Join-Path $PSScriptRoot 'scripts\skillctl.py'
& $python $entry $Command @RemainingArgs
exit $LASTEXITCODE