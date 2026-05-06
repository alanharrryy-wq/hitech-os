@echo off
setlocal
set "PRISMA_CMD_SELF=%~f0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $path=$env:PRISMA_CMD_SELF; $content=Get-Content -LiteralPath $path -Raw; $start='::POWERSHELL_PAYLOAD_'+'START'; $end='::POWERSHELL_PAYLOAD_'+'END'; $parts=$content -split [regex]::Escape($start),2; if($parts.Count -lt 2){throw 'PowerShell payload start marker missing'}; $script=($parts[1] -split [regex]::Escape($end),2)[0]; Invoke-Expression $script"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" pause
exit /b %RC%

::POWERSHELL_PAYLOAD_START
$ErrorActionPreference = "Stop"
$SystemRoot = (Resolve-Path -LiteralPath (Join-Path (Split-Path -Parent $path) ".")).Path
$OutDir = "F:\descargasf"
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
$Timestamp = Get-Date -Format "yyMMdd_HHmmss"
$AllLog = Join-Path $OutDir ("prisma_cloudflare_all_{0}.log" -f $Timestamp)
$QuickConfig = Join-Path $OutDir "prisma_cloudflare_quick_dev_empty_config.yml"

function Write-RunLog {
  param([string]$Message, [string]$Level = "INFO")
  $line = "[{0}] [{1}] {2}" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"), $Level, $Message
  Write-Host $line
  Add-Content -LiteralPath $AllLog -Value $line -Encoding UTF8
}

function ConvertTo-PsSingleQuoted {
  param([string]$Value)
  return "'" + ($Value -replace "'", "''") + "'"
}

function Test-HttpOk {
  param([string]$Url)
  try {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
    return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
  } catch {
    return $false
  }
}

function Start-QuickTunnel {
  param(
    [string]$Name,
    [int]$Port,
    [string]$Title,
    [string]$Cloudflared
  )
  $url = "http://127.0.0.1:$Port"
  $logPath = Join-Path $OutDir ("prisma_cloudflare_{0}_{1}.log" -f $Name.ToLowerInvariant(), $Timestamp)
  $command = @"
`$Host.UI.RawUI.WindowTitle = $(ConvertTo-PsSingleQuoted $Title)
Set-Location -LiteralPath $(ConvertTo-PsSingleQuoted $SystemRoot)
& $(ConvertTo-PsSingleQuoted $Cloudflared) tunnel --url $(ConvertTo-PsSingleQuoted $url) --config $(ConvertTo-PsSingleQuoted $QuickConfig) 2>&1 | Tee-Object -FilePath $(ConvertTo-PsSingleQuoted $logPath) -Append
"@
  Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $command) -WindowStyle Normal
  Write-RunLog ("Started {0}: cloudflared tunnel --url {1} --config {2}; log={3}" -f $Title, $url, $QuickConfig, $logPath)
}

Write-RunLog ("SystemRoot={0}" -f $SystemRoot)
Write-RunLog "Cloudflare mode: quick/dev tunnels. Industrial engine/forms/eit config is not modified."

$cloudflaredCommand = Get-Command cloudflared.exe -ErrorAction SilentlyContinue
if ($null -eq $cloudflaredCommand) { $cloudflaredCommand = Get-Command cloudflared -ErrorAction SilentlyContinue }
if ($null -eq $cloudflaredCommand) {
  Write-RunLog "[WARN] cloudflared not found in PATH. Local dev still works. Install Cloudflare Tunnel if you need public URLs." "WARN"
  exit 0
}
$Cloudflared = $cloudflaredCommand.Source
Set-Content -LiteralPath $QuickConfig -Value @(
  "# PRISMA quick/dev config. This avoids parsing or mutating the named engine tunnel config.",
  "protocol: quic"
) -Encoding UTF8
Write-RunLog ("Quick/dev config: {0}" -f $QuickConfig)

$services = @(
  @{ Name = "Tablet"; Port = 3120; Url = "http://127.0.0.1:3120/"; Title = "PRISMA Cloudflare Tablet 3120" },
  @{ Name = "PC"; Port = 3130; Url = "http://127.0.0.1:3130/"; Title = "PRISMA Cloudflare PC 3130" },
  @{ Name = "Mobile"; Port = 3140; Url = "http://127.0.0.1:3140/"; Title = "PRISMA Cloudflare Mobile 3140" }
)

foreach ($service in $services) {
  if (Test-HttpOk $service.Url) {
    Write-RunLog ("Local {0} healthy: {1}" -f $service.Name, $service.Url)
  } else {
    Write-RunLog ("Local {0} is not responding at {1}. Tunnel will still start; the app may come up later." -f $service.Name, $service.Url) "WARN"
  }
}

Start-QuickTunnel -Name "tablet" -Port 3120 -Title "PRISMA Cloudflare Tablet 3120" -Cloudflared $Cloudflared
Start-QuickTunnel -Name "pc" -Port 3130 -Title "PRISMA Cloudflare PC 3130" -Cloudflared $Cloudflared
Start-QuickTunnel -Name "mobile" -Port 3140 -Title "PRISMA Cloudflare Mobile 3140" -Cloudflared $Cloudflared

Write-RunLog "Cloudflare quick tunnels started."
Write-RunLog "Watch each tunnel window/log for the generated trycloudflare.com URL."
Write-RunLog "Tablet local: http://127.0.0.1:3120/"
Write-RunLog "PC local:     http://127.0.0.1:3130/"
Write-RunLog "Mobile local: http://127.0.0.1:3140/"
Write-RunLog ("Summary log: {0}" -f $AllLog)
::POWERSHELL_PAYLOAD_END
