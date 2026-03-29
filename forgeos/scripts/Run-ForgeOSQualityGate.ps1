Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[ForgeOS] Running quality gate..."

$root = "F:\repos\hitech-os\forgeos"

$steps = @(
    @{
        Name = "Import boundary validation"
        Workdir = "$root"
        Command = {
            python scripts\validate_import_boundaries.py --root "F:\repos\hitech-os\forgeos" --report "F:\repos\hitech-os\tools\_local\evidence\forgeos_import_boundaries_report.json"
        }
    },
    @{
        Name = "Package dry-run validation"
        Workdir = "$root"
        Command = {
            python scripts\package_dry_run.py --root "F:\repos\hitech-os\forgeos" --kernel-version "0.1.0" --report "F:\repos\hitech-os\tools\_local\evidence\forgeos_package_dry_run_report.json"
        }
    },
    @{
        Name = "Kernel tests"
        Workdir = "$root\platform\forge_kernel"
        Command = {
            $env:PYTHONPATH = "src;..\forge_commons\src;..\..\products\dummy_product\src;..\..\products\repo_analyzer\src;..\..\products\cloudflare_guardian\src;..\..\products\orchestrator_bridge\src"
            python -m unittest discover -s tests -p "test_*.py"
        }
    },
    @{
        Name = "Commons tests"
        Workdir = "$root\platform\forge_commons"
        Command = {
            $env:PYTHONPATH = "src;..\forge_kernel\src"
            python -m unittest discover -s tests -p "test_*.py"
        }
    },
    @{
        Name = "Repo Analyzer tests"
        Workdir = "$root\products\repo_analyzer"
        Command = {
            $env:PYTHONPATH = "src;..\..\platform\forge_kernel\src;..\..\platform\forge_commons\src"
            python -m unittest discover -s tests -p "test_*.py"
        }
    },
    @{
        Name = "Cloudflare Guardian tests"
        Workdir = "$root\products\cloudflare_guardian"
        Command = {
            $env:PYTHONPATH = "src;..\..\platform\forge_kernel\src;..\..\platform\forge_commons\src"
            python -m unittest discover -s tests -p "test_*.py"
        }
    },
    @{
        Name = "Orchestrator Bridge tests"
        Workdir = "$root\products\orchestrator_bridge"
        Command = {
            $env:PYTHONPATH = "src;..\..\platform\forge_kernel\src;..\..\platform\forge_commons\src"
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
