[CmdletBinding()]
param(
    [string]$ForgeOSRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$EvidenceDir = "",
    [string]$KernelVersion = "0.1.0"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$forgeRoot = (Resolve-Path $ForgeOSRoot).Path
$repoRoot = (Resolve-Path (Join-Path $forgeRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($EvidenceDir)) {
    $EvidenceDir = Join-Path $repoRoot "tools/_local/evidence"
}
$evidencePath = [System.IO.Path]::GetFullPath($EvidenceDir)
New-Item -ItemType Directory -Path $evidencePath -Force | Out-Null

$boundaryReport = Join-Path $evidencePath "forgeos_import_boundaries_report.json"
$packageReport = Join-Path $evidencePath "forgeos_package_dry_run_report.json"
$pathSeparator = [System.IO.Path]::PathSeparator

Write-Host "[ForgeOS] Running quality gate..."
Write-Host "[ForgeOS] Root: $forgeRoot"
Write-Host "[ForgeOS] Evidence: $evidencePath"

$steps = @(
    @{
        Name = "Import boundary validation"
        Workdir = "$forgeRoot"
        Command = {
            python scripts/validate_import_boundaries.py --root "$forgeRoot" --report "$boundaryReport"
        }
    },
    @{
        Name = "Package dry-run validation"
        Workdir = "$forgeRoot"
        Command = {
            python scripts/package_dry_run.py --root "$forgeRoot" --kernel-version "$KernelVersion" --report "$packageReport"
        }
    },
    @{
        Name = "Kernel tests"
        Workdir = (Join-Path $forgeRoot "platform/forge_kernel")
        Command = {
            $env:PYTHONPATH = @(
                "src",
                "../forge_commons/src",
                "../../products/dummy_product/src",
                "../../products/repo_analyzer/src",
                "../../products/cloudflare_guardian/src",
                "../../products/orchestrator_bridge/src"
            ) -join $pathSeparator
            python -m unittest discover -s tests -p "test_*.py"
        }
    },
    @{
        Name = "Commons tests"
        Workdir = (Join-Path $forgeRoot "platform/forge_commons")
        Command = {
            $env:PYTHONPATH = @(
                "src",
                "../forge_kernel/src"
            ) -join $pathSeparator
            python -m unittest discover -s tests -p "test_*.py"
        }
    },
    @{
        Name = "Repo Analyzer tests"
        Workdir = (Join-Path $forgeRoot "products/repo_analyzer")
        Command = {
            $env:PYTHONPATH = @(
                "src",
                "../../platform/forge_kernel/src",
                "../../platform/forge_commons/src"
            ) -join $pathSeparator
            python -m unittest discover -s tests -p "test_*.py"
        }
    },
    @{
        Name = "Cloudflare Guardian tests"
        Workdir = (Join-Path $forgeRoot "products/cloudflare_guardian")
        Command = {
            $env:PYTHONPATH = @(
                "src",
                "../../platform/forge_kernel/src",
                "../../platform/forge_commons/src"
            ) -join $pathSeparator
            python -m unittest discover -s tests -p "test_*.py"
        }
    },
    @{
        Name = "Orchestrator Bridge tests"
        Workdir = (Join-Path $forgeRoot "products/orchestrator_bridge")
        Command = {
            $env:PYTHONPATH = @(
                "src",
                "../../platform/forge_kernel/src",
                "../../platform/forge_commons/src"
            ) -join $pathSeparator
            python -m unittest discover -s tests -p "test_*.py"
        }
    }
)

foreach ($step in $steps) {
    Write-Host "[ForgeOS] $($step.Name)..."
    Push-Location $step.Workdir
    try {
        & $step.Command
    }
    finally {
        Pop-Location
    }
}

Write-Host "[ForgeOS] Quality gate PASSED."
