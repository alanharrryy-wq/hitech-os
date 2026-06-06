param(
  [ValidateSet('discovery','quick','full','critical')]
  [string]$Mode = 'quick',

  [int]$Workers = 6,

  [switch]$NoScreenshots,

  [int]$Shards = 1,

  [switch]$FullPage,

  [switch]$AllowPartial
)

$ErrorActionPreference = 'Stop'

$Central = 'F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1'
if (!(Test-Path -LiteralPath $Central)) {
  throw "Central Plawright Mamastrophic runner missing: $Central"
}

$argsList = @('-Mode', $Mode, '-Workers', $Workers, '-Shards', $Shards)
if ($NoScreenshots) { $argsList += '-NoScreenshots' }
if ($FullPage) { $argsList += '-FullPage' }
if ($AllowPartial) { $argsList += '-AllowPartial' }

& powershell -NoProfile -ExecutionPolicy Bypass -File $Central @argsList
exit $LASTEXITCODE
