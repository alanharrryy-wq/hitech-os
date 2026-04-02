[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("quality-gate", "validate-boundaries", "package-dry-run", "repo-analyzer")]
    [string]$Action = "quality-gate",
    [string]$RepoRoot = "",
    [string]$ForgeOSRoot = "",
    [string]$PythonExe = "python",
    [string]$EvidenceDir = "",
    [string]$KernelVersion = "0.1.0",
    [string]$TargetRoot = "",
    [string]$OutputPath = "",
    [string]$Query = "",
    [int]$SearchLimit = 50,
    [string]$PreviewPath = "",
    [int]$PreviewLines = 80,
    [switch]$FailFast
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-DefaultRepoRoot {
    param([string]$Value)
    if (-not [string]::IsNullOrWhiteSpace($Value)) {
        return [System.IO.Path]::GetFullPath($Value)
    }
    return [System.IO.Path]::GetFullPath($PSScriptRoot)
}

function Assert-PathExists {
    param(
        [string]$PathValue,
        [string]$Label
    )
    if (-not (Test-Path -LiteralPath $PathValue)) {
        throw "$Label no existe: $PathValue"
    }
}

$repoRootResolved = Resolve-DefaultRepoRoot -Value $RepoRoot
$forgeRootResolved = if ([string]::IsNullOrWhiteSpace($ForgeOSRoot)) {
    Join-Path $repoRootResolved "forgeos"
} else {
    [System.IO.Path]::GetFullPath($ForgeOSRoot)
}
$entrypointResolved = Join-Path $repoRootResolved "forgeos_entrypoint.py"
$targetRootResolved = if ([string]::IsNullOrWhiteSpace($TargetRoot)) { $repoRootResolved } else { [System.IO.Path]::GetFullPath($TargetRoot) }
$evidenceResolved = if ([string]::IsNullOrWhiteSpace($EvidenceDir)) {
    Join-Path $repoRootResolved "tools\_local\evidence"
} else {
    [System.IO.Path]::GetFullPath($EvidenceDir)
}

Assert-PathExists -PathValue $repoRootResolved -Label "Repo root"
Assert-PathExists -PathValue $forgeRootResolved -Label "ForgeOS root"
Assert-PathExists -PathValue $entrypointResolved -Label "forgeos_entrypoint.py"
New-Item -ItemType Directory -Force -Path $evidenceResolved | Out-Null

Write-Progress -Activity "ForgeOS Root Authority" -Status "Resolviendo rutas" -PercentComplete 10
Write-Host "[ForgeOS] Repo root: $repoRootResolved"
Write-Host "[ForgeOS] ForgeOS root: $forgeRootResolved"
Write-Host "[ForgeOS] Action: $Action"

$argList = @($entrypointResolved, $Action)

switch ($Action) {
    "quality-gate" {
        $argList += @("--kernel-version", $KernelVersion, "--evidence-dir", $evidenceResolved)
        if ($FailFast) { $argList += "--fail-fast" }
    }
    "validate-boundaries" {
        $argList += @("--evidence-dir", $evidenceResolved)
    }
    "package-dry-run" {
        $argList += @("--kernel-version", $KernelVersion, "--evidence-dir", $evidenceResolved)
    }
    "repo-analyzer" {
        $argList += @("--kernel-version", $KernelVersion, "--target-root", $targetRootResolved)
        if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
            $argList += @("--output", ([System.IO.Path]::GetFullPath($OutputPath)))
        }
        if (-not [string]::IsNullOrWhiteSpace($Query)) {
            $argList += @("--query", $Query, "--search-limit", $SearchLimit)
        }
        if (-not [string]::IsNullOrWhiteSpace($PreviewPath)) {
            $argList += @("--preview-path", ([System.IO.Path]::GetFullPath($PreviewPath)), "--preview-lines", $PreviewLines)
        }
    }
}

Write-Progress -Activity "ForgeOS Root Authority" -Status "Ejecutando $Action" -PercentComplete 55
Push-Location $repoRootResolved
try {
    & $PythonExe @argList
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

if ($exitCode -ne 0) {
    Write-Progress -Activity "ForgeOS Root Authority" -Status "$Action falló" -PercentComplete 100
    throw "ForgeOS action '$Action' falló con código $exitCode"
}

Write-Progress -Activity "ForgeOS Root Authority" -Status "$Action completada" -PercentComplete 100
Write-Host "[ForgeOS] Acción completada sin pedos: $Action"
