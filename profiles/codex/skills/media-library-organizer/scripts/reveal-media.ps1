param(
    [Parameter(Mandatory = $true)]
    [string]$LibraryRoot,

    [Parameter(Mandatory = $true)]
    [string]$Uri
)

$ErrorActionPreference = 'Stop'

try {
    $root = [System.IO.Path]::GetFullPath($LibraryRoot).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $request = [System.Uri]$Uri
    if ($request.Scheme -ne 'materiallib') {
        throw "Unsupported protocol: $($request.Scheme)"
    }

    $relativePath = $null
    foreach ($pair in $request.Query.TrimStart('?').Split('&', [System.StringSplitOptions]::RemoveEmptyEntries)) {
        $parts = $pair.Split('=', 2)
        if ([System.Uri]::UnescapeDataString($parts[0]) -eq 'path' -and $parts.Count -eq 2) {
            $relativePath = [System.Uri]::UnescapeDataString($parts[1])
            break
        }
    }
    if ([string]::IsNullOrWhiteSpace($relativePath) -or [System.IO.Path]::IsPathRooted($relativePath)) {
        throw 'The media path is missing or is not relative.'
    }

    $relativePath = $relativePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    $target = [System.IO.Path]::GetFullPath((Join-Path $root $relativePath))
    $rootPrefix = $root + [System.IO.Path]::DirectorySeparatorChar
    if (-not $target.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'The requested file is outside the media library.'
    }
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        throw "Media file not found: $target"
    }

    & (Join-Path $env:WINDIR 'explorer.exe') "/select,`"$target`""
} catch {
    $log = Join-Path $env:TEMP 'media-library-reveal-error.log'
    "$(Get-Date -Format o) $($_.Exception.Message)" | Add-Content -LiteralPath $log -Encoding UTF8
    exit 1
}
