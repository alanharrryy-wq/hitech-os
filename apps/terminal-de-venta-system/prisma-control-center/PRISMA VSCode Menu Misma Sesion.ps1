# PRISMA_COMPAT_PS51_PATCHED

$ErrorActionPreference = "Stop"

$Code = "C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"
$Workspace = "F:\repos\hitech-os"
$TasksPath = "F:\repos\hitech-os\.vscode\tasks.json"
$SettingsPath = "F:\repos\hitech-os\.vscode\settings.json"
$LauncherJson = "F:\repos\hitech-os\.vscode\prisma-launcher.json"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function ConvertTo-HashtableCompat($InputObject) {
  if ($null -eq $InputObject) { return $null }

  if ($InputObject -is [System.Collections.IDictionary]) {
    $hash = @{}
    foreach ($key in $InputObject.Keys) {
      $hash[$key] = ConvertTo-HashtableCompat $InputObject[$key]
    }
    return $hash
  }

  if ($InputObject -is [System.Collections.IEnumerable] -and $InputObject -isnot [string]) {
    $array = @()
    foreach ($item in $InputObject) {
      $array += ,(ConvertTo-HashtableCompat $item)
    }
    return $array
  }

  if ($InputObject -is [pscustomobject]) {
    $hash = @{}
    foreach ($prop in $InputObject.PSObject.Properties) {
      $hash[$prop.Name] = ConvertTo-HashtableCompat $prop.Value
    }
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
  $Data | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Quote-PS([string]$s) {
  return "'" + ($s -replace "'", "''") + "'"
}

function Show-MainMenu {
  $form = New-Object System.Windows.Forms.Form
  $form.Text = "PRISMA al abrir VS Code"
  $form.Size = New-Object System.Drawing.Size(460, 310)
  $form.StartPosition = "CenterScreen"
  $form.TopMost = $true
  $form.FormBorderStyle = "FixedDialog"
  $form.MaximizeBox = $false
  $form.MinimizeBox = $false

  $title = New-Object System.Windows.Forms.Label
  $title.Text = "¿Qué quieres levantar?"
  $title.Font = New-Object System.Drawing.Font("Segoe UI", 16, [System.Drawing.FontStyle]::Bold)
  $title.AutoSize = $true
  $title.Location = New-Object System.Drawing.Point(24, 22)
  $form.Controls.Add($title)

  $sub = New-Object System.Windows.Forms.Label
  $sub.Text = "Se abrirá VS Code normal, usando tu sesión actual."
  $sub.Font = New-Object System.Drawing.Font("Segoe UI", 9)
  $sub.AutoSize = $true
  $sub.Location = New-Object System.Drawing.Point(27, 58)
  $form.Controls.Add($sub)

  $choices = @(
    @("all-local", "🚀 Levantar todos local"),
    @("all", "🌩️ Levantar todos + Cloudflare"),
    @("custom", "🧩 Elegir algunos"),
    @("none", "🛑 No levantar nada")
  )

  $y = 92
  foreach ($c in $choices) {
    $b = New-Object System.Windows.Forms.Button
    $b.Text = $c[1]
    $b.Tag = $c[0]
    $b.Size = New-Object System.Drawing.Size(390, 38)
    $b.Location = New-Object System.Drawing.Point(28, $y)
    $b.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    $b.Add_Click({
      $form.Tag = $this.Tag
      $form.Close()
    })
    $form.Controls.Add($b)
    $y += 44
  }

  [void]$form.ShowDialog()
  return [string]$form.Tag
}

function Show-ServicePicker($Services) {
  $form = New-Object System.Windows.Forms.Form
  $form.Text = "PRISMA servicios"
  $form.Size = New-Object System.Drawing.Size(560, 520)
  $form.StartPosition = "CenterScreen"
  $form.TopMost = $true

  $label = New-Object System.Windows.Forms.Label
  $label.Text = "Selecciona qué levantar"
  $label.Font = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
  $label.AutoSize = $true
  $label.Location = New-Object System.Drawing.Point(18, 16)
  $form.Controls.Add($label)

  $list = New-Object System.Windows.Forms.CheckedListBox
  $list.CheckOnClick = $true
  $list.Size = New-Object System.Drawing.Size(505, 350)
  $list.Location = New-Object System.Drawing.Point(20, 55)
  $list.Font = New-Object System.Drawing.Font("Segoe UI", 10)

  foreach ($svc in $Services) {
    [void]$list.Items.Add($svc.name)
  }
  $form.Controls.Add($list)

  $ok = New-Object System.Windows.Forms.Button
  $ok.Text = "Levantar seleccionados"
  $ok.Size = New-Object System.Drawing.Size(190, 36)
  $ok.Location = New-Object System.Drawing.Point(215, 425)
  $ok.Add_Click({
    $form.Tag = "ok"
    $form.Close()
  })
  $form.Controls.Add($ok)

  $cancel = New-Object System.Windows.Forms.Button
  $cancel.Text = "Nada"
  $cancel.Size = New-Object System.Drawing.Size(100, 36)
  $cancel.Location = New-Object System.Drawing.Point(420, 425)
  $cancel.Add_Click({
    $form.Tag = "cancel"
    $form.Close()
  })
  $form.Controls.Add($cancel)

  [void]$form.ShowDialog()

  if ($form.Tag -ne "ok") { return @() }

  $selected = @()
  foreach ($item in $list.CheckedItems) {
    $selected += [string]$item
  }
  return $selected
}

function Update-PrismaTasks($SelectedNames) {
  $tasks = Read-JsonFile $TasksPath @{ version = "2.0.0"; tasks = @() }
  if (-not $tasks.ContainsKey("version")) { $tasks["version"] = "2.0.0" }
  if (-not $tasks.ContainsKey("tasks")) { $tasks["tasks"] = @() }

  
# BEGIN PRISMA_DEV_ROUTE_WARMER_PATCH_V2
function Start-PrismaDevRouteWarmup {
  try {
    $WarmPs1 = Join-Path $PSScriptRoot "internal\wrappers\warm_dev_routes.ps1"
    if (-not (Test-Path -LiteralPath $WarmPs1)) { return }

    $exe = $null
    $cmd = Get-Command pwsh.exe -ErrorAction SilentlyContinue
    if ($cmd) { $exe = $cmd.Source }
    if (-not $exe) {
      $cmd = Get-Command powershell.exe -ErrorAction SilentlyContinue
      if ($cmd) { $exe = $cmd.Source }
    }
    if (-not $exe) { return }

    $argLine = "-NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Minimized -File `"$WarmPs1`" -WaitSeconds 180 -TimeoutSeconds 25 -MaxWorkers 14 -NoPause"
    Start-Process -FilePath $exe -ArgumentList $argLine -WindowStyle Minimized | Out-Null
  } catch {
    # El warm-up es auxiliar. Nunca debe bloquear VS Code.
  }
}
# END PRISMA_DEV_ROUTE_WARMER_PATCH_V2

$cfg = Read-JsonFile $LauncherJson @{ services = @() }
  $services = @($cfg.services)

  $kept = @()
  foreach ($t in @($tasks.tasks)) {
    $label = [string]$t.label
    if ($label -eq "PRISMA AUTO: SELECCION") { continue }
    if ($label.StartsWith("PRISMA AUTO: ")) { continue }

    if ($label.StartsWith("PRISMA:")) {
      if (-not $t.ContainsKey("presentation")) { $t["presentation"] = @{} }
      $t.presentation.Remove("group")
      $t.presentation["panel"] = "dedicated"
      $t.presentation["reveal"] = "always"
      $t.presentation["clear"] = $false
      $t.presentation["echo"] = $true
      $t.presentation["focus"] = $false

      if ($t.ContainsKey("runOptions")) {
        $t.runOptions.Remove("runOn")
        if ($t.runOptions.Count -eq 0) { $t.Remove("runOptions") }
      }
    }

    $kept += $t
  }

  $autoTasks = @()
  $selectedLabels = @()

  foreach ($svc in $services) {
    $name = [string]$svc.name
    $label = "PRISMA AUTO: $name"
    $cmd = "`$env:PYTHONUTF8='1'; `$env:PYTHONIOENCODING='utf-8:replace'; `$env:NO_COLOR='1'; Set-Location -LiteralPath $(Quote-PS ([string]$svc.cwd)); $($svc.command)"

    $task = [ordered]@{
      label = $label
      type = "shell"
      command = $cmd
      isBackground = $true
      problemMatcher = @()
      presentation = [ordered]@{
        reveal = "always"
        panel = "dedicated"
        clear = $false
        echo = $true
        focus = $false
      }
      options = [ordered]@{
        shell = [ordered]@{
          executable = "pwsh.exe"
          args = @("-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command")
        }
      }
    }

    $autoTasks += $task

    if ($SelectedNames -contains $name) {
      $selectedLabels += $label
    }
  }

  $finalTasks = @()
  $finalTasks += $kept
  $finalTasks += $autoTasks

  if ($selectedLabels.Count -gt 0) {
    $compound = [ordered]@{
      label = "PRISMA AUTO: SELECCION"
      dependsOrder = "parallel"
      dependsOn = $selectedLabels
      problemMatcher = @()
      runOptions = [ordered]@{
        runOn = "folderOpen"
      }
    }
    $finalTasks += $compound
  }

  $tasks.tasks = $finalTasks
  Write-JsonFile $TasksPath $tasks

  $settings = Read-JsonFile $SettingsPath @{}
  $settings["task.allowAutomaticTasks"] = "on"
  $settings["terminal.integrated.tabs.enabled"] = $true
  Write-JsonFile $SettingsPath $settings
}

$cfg = Read-JsonFile $LauncherJson @{ services = @() }
$services = @($cfg.services)

$mode = Show-MainMenu

if ([string]::IsNullOrWhiteSpace($mode)) {
  exit 0
}

$selectedNames = @()

if ($mode -eq "all-local") {
  $selectedNames = @($services | Where-Object { $_.group -eq "local" } | ForEach-Object { $_.name })
} elseif ($mode -eq "all") {
  $selectedNames = @($services | Where-Object { $_.group -eq "local" -or $_.group -eq "cloudflare" } | ForEach-Object { $_.name })
} elseif ($mode -eq "custom") {
  $selectedNames = @(Show-ServicePicker $services)
} elseif ($mode -eq "none") {
  $selectedNames = @()
}

Update-PrismaTasks $selectedNames

Start-Process -FilePath $Code -ArgumentList @("--new-window", $Workspace)

# BEGIN PRISMA_DEV_ROUTE_WARMER_CALL_V2
try {
  if ((Get-Command Start-PrismaDevRouteWarmup -ErrorAction SilentlyContinue) -and @($selectedNames).Count -gt 0) {
    Start-PrismaDevRouteWarmup
  }
} catch {}
# END PRISMA_DEV_ROUTE_WARMER_CALL_V2
