# PRISMA_COMPAT_PS51_PATCHED
# PRISMA_VSCODE_SAME_SESSION_MENU_V2_3160_SAFE
param(
  [ValidateSet("menu", "all-local", "all", "custom", "none", "cloud-command-center-3160")]
  [string]$Mode = "menu",
  [switch]$NoOpenVSCode,
  [switch]$NoWarmup
)

$ErrorActionPreference = "Stop"
$Workspace = "F:\repos\hitech-os"
$ControlRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TasksPath = Join-Path $Workspace ".vscode\tasks.json"
$SettingsPath = Join-Path $Workspace ".vscode\settings.json"
$LauncherJson = Join-Path $Workspace ".vscode\prisma-launcher.json"
$FallbackServicesJson = Join-Path $ControlRoot "internal\config\services.json"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function ConvertTo-HashtableCompat($InputObject) {
  if ($null -eq $InputObject) { return $null }
  if ($InputObject -is [System.Collections.IDictionary]) {
    $hash = @{}
    foreach ($key in $InputObject.Keys) { $hash[$key] = ConvertTo-HashtableCompat $InputObject[$key] }
    return $hash
  }
  if ($InputObject -is [System.Collections.IEnumerable] -and $InputObject -isnot [string]) {
    $array = @()
    foreach ($item in $InputObject) { $array += ,(ConvertTo-HashtableCompat $item) }
    return $array
  }
  if ($InputObject -is [pscustomobject]) {
    $hash = @{}
    foreach ($prop in $InputObject.PSObject.Properties) { $hash[$prop.Name] = ConvertTo-HashtableCompat $prop.Value }
    return $hash
  }
  return $InputObject
}

function Read-JsonFile([string]$Path, $Default) {
  if (-not (Test-Path -LiteralPath $Path)) { return $Default }
  $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
  if ([string]::IsNullOrWhiteSpace($raw)) { return $Default }
  return ConvertTo-HashtableCompat ($raw | ConvertFrom-Json)
}

function Write-JsonFile([string]$Path, $Data) {
  $parent = Split-Path -Parent $Path
  if ($parent -and -not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
  $Data | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Quote-PS([string]$s) { return "'" + ($s -replace "'", "''") + "'" }

function New-PrismaMenuService {
  param([string]$Id,[string]$Name,[string]$Group,[string]$Cwd,[string]$Command,[string]$Kind="generic",[bool]$Foreground=$false)
  return [ordered]@{ id=$Id; name=$Name; group=$Group; cwd=$Cwd; command=$Command; kind=$Kind; foreground=$Foreground }
}

function Test-IsCloudCommandCenterService($Service) {
  $name = [string]$Service.name
  $id = [string]$Service.id
  $kind = [string]$Service.kind
  $cmd = [string]$Service.command
  return ($id -eq "cloud-command-center-3160" -or $kind -eq "cloud-command-center" -or $name -match "3160" -or $cmd -match "cloud_command_center_3160\.ps1")
}

function Get-PrismaMenuServices {
  $cfg = Read-JsonFile $LauncherJson @{ services = @() }
  $services = @($cfg.services)
  if ($services.Count -eq 0 -and (Test-Path -LiteralPath $FallbackServicesJson)) {
    $fallback = Read-JsonFile $FallbackServicesJson @{ services = @() }
    foreach ($svc in @($fallback.services)) {
      $svcId = [string]$svc.id; $svcName = [string]$svc.name
      if ([string]::IsNullOrWhiteSpace($svcId) -or [string]::IsNullOrWhiteSpace($svcName)) { continue }
      $cmd = "& {0} -ServiceId {1}" -f (Quote-PS (Join-Path $ControlRoot "internal\wrappers\module_cloudflare.ps1")), (Quote-PS $svcId)
      $services += New-PrismaMenuService -Id $svcId -Name $svcName -Group "local" -Cwd $ControlRoot -Command $cmd -Kind "configured-module" -Foreground $false
    }
  }
  $has3160 = $false
  foreach ($svc in @($services)) { if (Test-IsCloudCommandCenterService $svc) { $has3160 = $true } }
  if (-not $has3160) {
    $cmd3160 = "& {0}" -f (Quote-PS (Join-Path $ControlRoot "internal\wrappers\cloud_command_center_3160.ps1"))
    $services += New-PrismaMenuService -Id "cloud-command-center-3160" -Name "PRISMA Cloud Command Center 3160" -Group "local" -Cwd $ControlRoot -Command $cmd3160 -Kind "cloud-command-center" -Foreground $true
  }
  return @($services)
}

function Show-MainMenu {
  $form = New-Object System.Windows.Forms.Form
  $form.Text = "PRISMA al abrir VS Code"; $form.Size = New-Object System.Drawing.Size(500, 360); $form.StartPosition = "CenterScreen"; $form.TopMost = $true
  $form.FormBorderStyle = "FixedDialog"; $form.MaximizeBox = $false; $form.MinimizeBox = $false
  $title = New-Object System.Windows.Forms.Label; $title.Text = "¿Qué quieres levantar?"; $title.Font = New-Object System.Drawing.Font("Segoe UI",16,[System.Drawing.FontStyle]::Bold); $title.AutoSize = $true; $title.Location = New-Object System.Drawing.Point(24,22); $form.Controls.Add($title)
  $sub = New-Object System.Windows.Forms.Label; $sub.Text = "Usa la sesión actual de VS Code. El 3160 queda foreground y sin navegador."; $sub.Font = New-Object System.Drawing.Font("Segoe UI",9); $sub.AutoSize = $true; $sub.Location = New-Object System.Drawing.Point(27,58); $form.Controls.Add($sub)
  $choices = @(@("all-local","🚀 Levantar todos local"),@("all","🌩️ Levantar todos + Cloudflare"),@("cloud-command-center-3160","🧭 Solo PRISMA Cloud Command Center 3160"),@("custom","🧩 Elegir algunos"),@("none","🛑 No levantar nada"))
  $y = 92
  foreach ($c in $choices) { $b = New-Object System.Windows.Forms.Button; $b.Text=$c[1]; $b.Tag=$c[0]; $b.Size=New-Object System.Drawing.Size(430,38); $b.Location=New-Object System.Drawing.Point(28,$y); $b.Font=New-Object System.Drawing.Font("Segoe UI",10); $b.Add_Click({ $form.Tag=$this.Tag; $form.Close() }); $form.Controls.Add($b); $y += 44 }
  [void]$form.ShowDialog(); return [string]$form.Tag
}

function Show-ServicePicker($Services) {
  $form = New-Object System.Windows.Forms.Form
  $form.Text = "PRISMA servicios"; $form.Size = New-Object System.Drawing.Size(600,540); $form.StartPosition="CenterScreen"; $form.TopMost=$true
  $label = New-Object System.Windows.Forms.Label; $label.Text="Selecciona qué levantar"; $label.Font=New-Object System.Drawing.Font("Segoe UI",14,[System.Drawing.FontStyle]::Bold); $label.AutoSize=$true; $label.Location=New-Object System.Drawing.Point(18,16); $form.Controls.Add($label)
  $hint = New-Object System.Windows.Forms.Label; $hint.Text="El 3160 se ejecuta en foreground dentro de VS Code, sin navegador automático."; $hint.Font=New-Object System.Drawing.Font("Segoe UI",9); $hint.AutoSize=$true; $hint.Location=New-Object System.Drawing.Point(20,43); $form.Controls.Add($hint)
  $list = New-Object System.Windows.Forms.CheckedListBox; $list.CheckOnClick=$true; $list.Size=New-Object System.Drawing.Size(545,340); $list.Location=New-Object System.Drawing.Point(20,72); $list.Font=New-Object System.Drawing.Font("Segoe UI",10)
  foreach ($svc in $Services) { [void]$list.Items.Add($svc.name) }
  $form.Controls.Add($list)
  $ok = New-Object System.Windows.Forms.Button; $ok.Text="Levantar seleccionados"; $ok.Size=New-Object System.Drawing.Size(190,36); $ok.Location=New-Object System.Drawing.Point(255,430); $ok.Add_Click({ $form.Tag="ok"; $form.Close() }); $form.Controls.Add($ok)
  $cancel = New-Object System.Windows.Forms.Button; $cancel.Text="Nada"; $cancel.Size=New-Object System.Drawing.Size(100,36); $cancel.Location=New-Object System.Drawing.Point(460,430); $cancel.Add_Click({ $form.Tag="cancel"; $form.Close() }); $form.Controls.Add($cancel)
  [void]$form.ShowDialog(); if ($form.Tag -ne "ok") { return @() }
  $selected=@(); foreach ($item in $list.CheckedItems) { $selected += [string]$item }; return $selected
}

function New-PrismaTaskFromService($Service) {
  $name=[string]$Service.name; $cwd=[string]$Service.cwd; $command=[string]$Service.command; $is3160=Test-IsCloudCommandCenterService $Service
  if ([string]::IsNullOrWhiteSpace($cwd)) { $cwd = $ControlRoot }
  if ($is3160) {
    $command = "`$env:PYTHONUTF8='1'; `$env:PYTHONIOENCODING='utf-8:replace'; `$env:NO_COLOR='1'; Set-Location -LiteralPath $(Quote-PS $ControlRoot); & $(Quote-PS (Join-Path $ControlRoot 'internal\wrappers\cloud_command_center_3160.ps1'))"
  } else {
    $command = "`$env:PYTHONUTF8='1'; `$env:PYTHONIOENCODING='utf-8:replace'; `$env:NO_COLOR='1'; Set-Location -LiteralPath $(Quote-PS $cwd); $command"
  }
  return [ordered]@{ label="PRISMA AUTO: $name"; type="shell"; command=$command; isBackground=(-not $is3160); problemMatcher=@(); presentation=[ordered]@{ reveal="always"; panel="dedicated"; clear=$false; echo=$true; focus=$is3160 }; options=[ordered]@{ shell=[ordered]@{ executable="pwsh.exe"; args=@("-NoLogo","-NoProfile","-ExecutionPolicy","Bypass","-Command") } } }
}

function Update-PrismaTasks($SelectedNames) {
  $tasks = Read-JsonFile $TasksPath @{ version="2.0.0"; tasks=@() }
  if (-not $tasks.ContainsKey("version")) { $tasks["version"]="2.0.0" }
  if (-not $tasks.ContainsKey("tasks")) { $tasks["tasks"]=@() }
  $services = @(Get-PrismaMenuServices)
  $kept=@()
  foreach ($t in @($tasks.tasks)) {
    $label=[string]$t.label
    if ($label -eq "PRISMA AUTO: SELECCION") { continue }
    if ($label.StartsWith("PRISMA AUTO: ")) { continue }
    if ($label.StartsWith("PRISMA:")) {
      if (-not $t.ContainsKey("presentation")) { $t["presentation"]=@{} }
      $t.presentation.Remove("group"); $t.presentation["panel"]="dedicated"; $t.presentation["reveal"]="always"; $t.presentation["clear"]=$false; $t.presentation["echo"]=$true; $t.presentation["focus"]=$false
      if ($t.ContainsKey("runOptions")) { $t.runOptions.Remove("runOn"); if ($t.runOptions.Count -eq 0) { $t.Remove("runOptions") } }
    }
    $kept += $t
  }
  $autoTasks=@(); $selectedLabels=@()
  foreach ($svc in $services) { $name=[string]$svc.name; $label="PRISMA AUTO: $name"; $autoTasks += (New-PrismaTaskFromService $svc); if ($SelectedNames -contains $name) { $selectedLabels += $label } }
  $finalTasks=@(); $finalTasks += $kept; $finalTasks += $autoTasks
  if ($selectedLabels.Count -gt 0) { $finalTasks += [ordered]@{ label="PRISMA AUTO: SELECCION"; dependsOrder="parallel"; dependsOn=$selectedLabels; problemMatcher=@(); runOptions=[ordered]@{ runOn="folderOpen" } } }
  $tasks.tasks=$finalTasks; Write-JsonFile $TasksPath $tasks
  $settings=Read-JsonFile $SettingsPath @{}; $settings["task.allowAutomaticTasks"]="on"; $settings["terminal.integrated.tabs.enabled"]=$true; Write-JsonFile $SettingsPath $settings
}

function Test-RunningInsideVSCode { return (-not [string]::IsNullOrWhiteSpace($env:VSCODE_PID) -or $env:TERM_PROGRAM -eq "vscode") }
function Get-VSCodeCommand { $candidates=@($env:PRISMA_VSCODE_CODE,"C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd","code.cmd","code") | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }; foreach ($candidate in $candidates) { if (Test-Path -LiteralPath $candidate) { return $candidate }; $cmd=Get-Command $candidate -ErrorAction SilentlyContinue; if ($cmd) { return $cmd.Source } }; return $null }
function Open-VSCodeWorkspaceReuseWindow { if ($NoOpenVSCode) { return }; if (Test-RunningInsideVSCode) { Write-Host "[PRISMA] Ya estoy dentro de VS Code; no abro otra ventana." -ForegroundColor Green; return }; $code=Get-VSCodeCommand; if (-not $code) { Write-Host "[PRISMA] WARN no encontre code.cmd/code en PATH. Abre VS Code manualmente en $Workspace." -ForegroundColor Yellow; return }; Write-Host "[PRISMA] Abriendo VS Code con --reuse-window: $Workspace" -ForegroundColor Cyan; & $code --reuse-window $Workspace | Out-Null }

$services = @(Get-PrismaMenuServices)
if ($Mode -eq "menu") { $mode = Show-MainMenu } else { $mode = $Mode }
if ([string]::IsNullOrWhiteSpace($mode)) { exit 0 }
$selectedNames=@()
if ($mode -eq "all-local") { $selectedNames = @($services | Where-Object { $_.group -eq "local" } | ForEach-Object { $_.name }) }
elseif ($mode -eq "all") { $selectedNames = @($services | Where-Object { $_.group -eq "local" -or $_.group -eq "cloudflare" } | ForEach-Object { $_.name }) }
elseif ($mode -eq "cloud-command-center-3160") { $selectedNames = @($services | Where-Object { Test-IsCloudCommandCenterService $_ } | ForEach-Object { $_.name }) }
elseif ($mode -eq "custom") { $selectedNames = @(Show-ServicePicker $services) }
elseif ($mode -eq "none") { $selectedNames = @() }
Update-PrismaTasks $selectedNames
Open-VSCodeWorkspaceReuseWindow
if ($NoWarmup) { Write-Host "[PRISMA] Warm-up omitido por parametro -NoWarmup." -ForegroundColor DarkGray } else { Write-Host "[PRISMA] Warm-up externo desactivado: no se lanza proceso minimizado desde este menu." -ForegroundColor DarkGray }
