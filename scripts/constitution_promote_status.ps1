param(
  [Parameter(Mandatory=$false)]
  [string]$RepoRoot = "F:\repos\hitech-os",

  [Parameter(Mandatory=$true)]
  [ValidateSet("draft","active","deprecated")]
  [string]$NewStatus,

  [Parameter(Mandatory=$false)]
  [ValidateSet("informational","warning","enforced")]
  [string[]]$OnlyAuthority = @("warning","enforced")
)

$ErrorActionPreference="Stop"

function Resolve-PathSafe([string]$p) {
  try { return (Resolve-Path -LiteralPath $p).Path } catch { return $p }
}

$repo = Resolve-PathSafe $RepoRoot
$tablesDir = Join-Path $repo "docs\constitution\tables"
if(!(Test-Path $tablesDir)){ throw "No existe: $tablesDir" }

$files = Get-ChildItem -LiteralPath $tablesDir -Filter "TBL_*.json" -File
if($files.Count -eq 0){ throw "No hay tablas TBL_*.json en $tablesDir" }

Write-Progress -Activity "Promoting constitution tables" -Status "Leyendo tablas..." -PercentComplete 10

$changed = 0
$i = 0
foreach($f in $files){
  $i++
  $pct = [int](10 + (80 * ($i / [double]$files.Count)))
  Write-Progress -Activity "Promoting constitution tables" -Status ("Procesando " + $f.Name) -PercentComplete $pct

  $obj = Get-Content -LiteralPath $f.FullName -Raw | ConvertFrom-Json
  if($OnlyAuthority -contains $obj.authority_level){
    if($obj.status -ne $NewStatus){
      $obj.status = $NewStatus
      ($obj | ConvertTo-Json -Depth 32) + "`n" | Set-Content -LiteralPath $f.FullName -Encoding UTF8
      $changed++
    }
  }
}

Write-Progress -Activity "Promoting constitution tables" -Completed
Write-Host "✅ Updated status -> '$NewStatus' for $changed table(s)." -ForegroundColor Green
