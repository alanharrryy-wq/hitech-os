param(
    [string]$RepoRoot = 'F:epos\hitech-ospps	erminal-de-venta-system',
    [string]$OutRoot = 'F:\descargasf\PRISMA_COMMERCIAL_RELEASES',
    [string]$Version = '1.0.0-pilot.1',
    [string]$ClientId = 'pilot-001',
    [string]$BranchId = 'matriz-001'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Builder = Join-Path $RepoRoot 'tooling\productization\commercial_release_builder\commercial_release_builder.py'
py -3 $Builder --repo-root $RepoRoot --out-root $OutRoot --version $Version --client-id $ClientId --branch-id $BranchId --channel 'pilot-paid'
