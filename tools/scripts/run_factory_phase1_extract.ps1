<#
.SYNOPSIS
Daily launcher for factory operator phase1-extract.

.EXAMPLE
.\tools\scripts\run_factory_phase1_extract.ps1

.EXAMPLE
.\tools\scripts\run_factory_phase1_extract.ps1 -DryRun -NoOpenVscode -NoOpenRunboard

.EXAMPLE
.\tools\scripts\run_factory_phase1_extract.ps1 -DoctorOnly

.NOTES
- Safe for Windows PowerShell 5.1 and PowerShell 7+.
- Uses robust async capture for stdout/stderr to avoid pipe deadlocks.
#>
param(
  [string]$BaseRef = "HEAD",
  [string]$RunId = "",
  [switch]$StrictRunId,
  [switch]$DryRun,
  [switch]$NoOpenVscode,
  [switch]$NoOpenRunboard,
  [switch]$NoOpenFinalReport,
  [switch]$DoctorOnly,
  [switch]$SkipDoctor,
  [switch]$Quiet,
  [switch]$VerboseLog,
  [switch]$NoLogs,
  [int]$TimeoutSec = 0,
  [int]$FailureTailLines = 40,
  [string[]]$ExtraArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$EXIT_OK = 0
$EXIT_DOCTOR_PROCESS = 10
$EXIT_DOCTOR_JSON = 11
$EXIT_DOCTOR_STATUS = 12
$EXIT_DOCTOR_TIMEOUT = 13
$EXIT_OPERATOR_PROCESS = 20
$EXIT_OPERATOR_JSON = 21
$EXIT_OPERATOR_STATUS = 22
$EXIT_OPERATOR_TIMEOUT = 23
$EXIT_MISSING_PYTHON = 90
$EXIT_MISSING_GIT = 91
$EXIT_REPO_INVALID = 92
$EXIT_IMPORT_CHECK = 93

$script:CurrentChildProcess = $null

# Encoding safety for JSON output rendering.
try {
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [Console]::OutputEncoding = $utf8NoBom
  $OutputEncoding = $utf8NoBom
} catch { }

function Write-Factory {
  param(
    [string]$Message = "",
    [string]$Color = ""
  )
  if ($Quiet) {
    return
  }
  if ($Color) {
    Write-Host $Message -ForegroundColor $Color
  } else {
    Write-Host $Message
  }
}

function Write-FactoryAlways {
  param(
    [string]$Message = "",
    [string]$Color = ""
  )
  if ($Color) {
    Write-Host $Message -ForegroundColor $Color
  } else {
    Write-Host $Message
  }
}

function Get-UtcIso8601 {
  return (Get-Date).ToUniversalTime().ToString("o")
}

function Ensure-Command {
  param([Parameter(Mandatory = $true)][string]$Name)
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $cmd) {
    throw "Missing required command in PATH: $Name"
  }
  if ($cmd -is [System.Array]) {
    return [string]$cmd[0].Source
  }
  return [string]$cmd.Source
}

function Ensure-Dir {
  param([Parameter(Mandatory = $true)][string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
  }
}

function Trim-Tail {
  param(
    [string]$Text,
    [int]$LineCount = 40
  )
  if ([string]::IsNullOrEmpty($Text)) {
    return ""
  }
  $all = $Text -split "`r?`n"
  if ($all.Count -le $LineCount) {
    return ($all -join "`r`n")
  }
  return ($all[($all.Count - $LineCount) .. ($all.Count - 1)] -join "`r`n")
}

function Quote-Argument {
  param([string]$Value)
  if ($null -eq $Value -or $Value -eq "") {
    return '""'
  }
  if ($Value -notmatch '[\s"]') {
    return $Value
  }
  $escaped = $Value -replace '(\\*)"', '$1$1\"'
  $escaped = $escaped -replace '(\\+)$', '$1$1'
  return '"' + $escaped + '"'
}

function Join-Arguments {
  param([string[]]$Values)
  return ($Values | ForEach-Object { Quote-Argument -Value $_ }) -join " "
}

function Write-LogFile {
  param(
    [string]$Path,
    [string]$Content
  )
  if ([string]::IsNullOrWhiteSpace($Path) -or $NoLogs) {
    return
  }
  Ensure-Dir (Split-Path -Parent $Path)
  Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Rotate-Logs {
  param(
    [Parameter(Mandatory = $true)][string]$Dir,
    [int]$Keep = 200
  )
  if ($NoLogs -or -not (Test-Path -LiteralPath $Dir)) {
    return
  }
  $files = @(Get-ChildItem -LiteralPath $Dir -File | Sort-Object -Property LastWriteTime, Name -Descending)
  if ($files.Count -le $Keep) {
    return
  }
  $drop = $files[$Keep .. ($files.Count - 1)]
  foreach ($item in $drop) {
    try {
      Remove-Item -LiteralPath $item.FullName -Force -ErrorAction Stop
    } catch { }
  }
}

function Get-FactorySchemaScore {
  param([object]$Value)
  if ($null -eq $Value) {
    return -1
  }
  $props = @($Value.PSObject.Properties.Name)
  if (-not $props -or $props.Count -eq 0) {
    return -1
  }
  $keys = @("status", "run_id", "command", "stage_last_completed", "stage_failed", "resume_hint", "reason")
  $score = 0
  foreach ($key in $keys) {
    if ($props -contains $key) {
      $score += 1
    }
  }
  return $score
}

function Get-ObjectPropertyValue {
  param(
    [object]$Object,
    [string]$Name,
    [object]$Default = ""
  )
  if ($null -eq $Object) {
    return $Default
  }
  $prop = $Object.PSObject.Properties[$Name]
  if ($null -eq $prop) {
    return $Default
  }
  return $prop.Value
}

function Get-LastJsonObjectFromText {
  param([string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) {
    return $null
  }

  $best = $null
  $bestScore = -1
  $bestOrder = -1

  try {
    $whole = $Text | ConvertFrom-Json -ErrorAction Stop
    $wholeScore = Get-FactorySchemaScore $whole
    if ($wholeScore -ge 0) {
      $best = $whole
      $bestScore = $wholeScore
      $bestOrder = [int]::MaxValue
    }
  } catch { }

  $regex = [regex]::new('\{(?:[^{}]|(?<o>\{)|(?<-o>\}))*\}(?(o)(?!))', [System.Text.RegularExpressions.RegexOptions]::Singleline)
  $matches = $regex.Matches($Text)
  for ($i = 0; $i -lt $matches.Count; $i++) {
    $candidate = $matches[$i].Value
    try {
      $obj = $candidate | ConvertFrom-Json -ErrorAction Stop
      $score = Get-FactorySchemaScore $obj
      if ($score -lt 0) {
        continue
      }
      if ($score -gt $bestScore -or ($score -eq $bestScore -and $i -ge $bestOrder)) {
        $best = $obj
        $bestScore = $score
        $bestOrder = $i
      }
    } catch { }
  }

  return $best
}

function Invoke-PythonCapture {
  param(
    [Parameter(Mandatory = $true)][string]$PythonPath,
    [Parameter(Mandatory = $true)][string[]]$CommandArgs,
    [string]$LogFile = "",
    [int]$TimeoutSec = 0
  )

  $argLine = Join-Arguments -Values $CommandArgs
  $workDir = (Get-Location).Path
  $timedOut = $false
  $process = New-Object System.Diagnostics.Process
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $PythonPath
  $psi.WorkingDirectory = $workDir
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.Arguments = $argLine
  $psi.EnvironmentVariables["PYTHONUTF8"] = "1"
  $psi.EnvironmentVariables["PYTHONFAULTHANDLER"] = "1"
  $process.StartInfo = $psi

  $stdout = ""
  $stderr = ""
  $exitCode = -1
  try {
    $null = $process.Start()
    $script:CurrentChildProcess = $process
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()

    if ($TimeoutSec -gt 0) {
      $done = $process.WaitForExit($TimeoutSec * 1000)
      if (-not $done) {
        $timedOut = $true
        try {
          $process.Kill()
        } catch { }
      }
    }
    $process.WaitForExit()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    $exitCode = $process.ExitCode
  } finally {
    $script:CurrentChildProcess = $null
  }

  $parts = @()
  if (-not [string]::IsNullOrWhiteSpace($stdout)) { $parts += $stdout.TrimEnd() }
  if (-not [string]::IsNullOrWhiteSpace($stderr)) { $parts += $stderr.TrimEnd() }
  $allText = ($parts -join "`r`n").Trim()

  $meta = @(
    "----- META -----",
    "time_utc: $(Get-UtcIso8601)",
    "cwd: $workDir",
    "exe: $PythonPath",
    "args: $argLine",
    "exit_code: $exitCode",
    "timed_out: $timedOut",
    "ps_edition: $($PSVersionTable.PSEdition)",
    "ps_version: $($PSVersionTable.PSVersion)",
    "----- STDOUT -----",
    $stdout,
    "----- STDERR -----",
    $stderr,
    "----- COMBINED -----",
    $allText
  ) -join "`r`n"
  Write-LogFile -Path $LogFile -Content $meta

  return [pscustomobject]@{
    ExitCode = $exitCode
    TimedOut = $timedOut
    StdOut = $stdout
    StdErr = $stderr
    AllText = $allText
    LogFile = $(if ($NoLogs) { "<disabled>" } else { $LogFile })
    CmdLine = "$PythonPath $argLine"
  }
}

function Test-RepoRoot {
  param([Parameter(Mandatory = $true)][string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    return $false
  }
  $expected = @(
    (Join-Path $Path ".git"),
    (Join-Path $Path "tools\codex"),
    (Join-Path $Path "tools\codex\factory")
  )
  foreach ($entry in $expected) {
    if (-not (Test-Path -LiteralPath $entry)) {
      return $false
    }
  }
  return $true
}

function Test-GitDirty {
  param([string]$GitPath)
  $tag = "factory_git_status_$PID"
  $outPath = Join-Path $env:TEMP "$tag.stdout.tmp"
  $errPath = Join-Path $env:TEMP "$tag.stderr.tmp"
  $proc = Start-Process -FilePath $GitPath -ArgumentList @("status", "--porcelain=v1") -WorkingDirectory (Get-Location).Path -NoNewWindow -PassThru -Wait -RedirectStandardOutput $outPath -RedirectStandardError $errPath
  try {
    $out = ""
    if (Test-Path -LiteralPath $outPath) {
      $out = Get-Content -LiteralPath $outPath -Raw
    }
    if (-not [string]::IsNullOrWhiteSpace($out)) {
      Write-Factory "[factory] Warning: working tree has local changes." "Yellow"
    }
  } finally {
    Remove-Item -LiteralPath $outPath -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $errPath -ErrorAction SilentlyContinue
    $null = $proc
  }
}

function Test-BaseRef {
  param(
    [string]$GitPath,
    [string]$Ref
  )
  if ([string]::IsNullOrWhiteSpace($Ref)) {
    return $false
  }
  $args = @("rev-parse", "--verify", "--quiet", "$Ref`^{commit}")
  $tag = "factory_git_ref_$PID"
  $outPath = Join-Path $env:TEMP "$tag.stdout.tmp"
  $errPath = Join-Path $env:TEMP "$tag.stderr.tmp"
  $p = Start-Process -FilePath $GitPath -ArgumentList $args -WorkingDirectory (Get-Location).Path -NoNewWindow -PassThru -Wait -RedirectStandardOutput $outPath -RedirectStandardError $errPath
  $ok = ($p.ExitCode -eq 0)
  if (-not $ok) {
    Write-Factory "[factory] Warning: base-ref '$Ref' did not resolve with git rev-parse." "Yellow"
  }
  Remove-Item -LiteralPath $outPath -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath $errPath -ErrorAction SilentlyContinue
  return $ok
}

trap [System.Management.Automation.PipelineStoppedException] {
  if ($script:CurrentChildProcess -and -not $script:CurrentChildProcess.HasExited) {
    try {
      $script:CurrentChildProcess.Kill()
    } catch { }
  }
  throw
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$doctorLog = "<disabled>"
$phaseLog = "<disabled>"
$finalStatus = ""
$finalRunId = ""

Push-Location $repoRoot
try {
  $psMode = if ($PSVersionTable.PSEdition -eq "Desktop") { "WindowsPowerShell" } else { "PowerShellCore" }
  Write-Factory "[factory] Shell: $psMode $($PSVersionTable.PSVersion)"

  if (-not (Test-RepoRoot $repoRoot)) {
    Write-FactoryAlways "[factory] Invalid repo root or missing expected structure: $repoRoot" "Red"
    exit $EXIT_REPO_INVALID
  }

  if ([string]::IsNullOrWhiteSpace($BaseRef)) {
    Write-FactoryAlways "[factory] --BaseRef must be non-empty." "Red"
    exit $EXIT_OPERATOR_STATUS
  }

  try {
    $pythonPath = Ensure-Command "python"
  } catch {
    Write-FactoryAlways "[factory] $($_.Exception.Message)" "Red"
    exit $EXIT_MISSING_PYTHON
  }
  try {
    $gitPath = Ensure-Command "git"
  } catch {
    Write-FactoryAlways "[factory] $($_.Exception.Message)" "Red"
    exit $EXIT_MISSING_GIT
  }

  if (-not $NoLogs) {
    $logDir = Join-Path $repoRoot "tools\codex\_logs"
    Ensure-Dir $logDir
    Rotate-Logs -Dir $logDir -Keep 200
    $ts = Get-Date -Format "yyyyMMdd_HHmmss"
    $doctorLog = Join-Path $logDir ("doctor_{0}.log" -f $ts)
    $phaseLog = Join-Path $logDir ("phase1-extract_{0}.log" -f $ts)
  } else {
    $logDir = "<disabled>"
  }

  Write-Factory "[factory] Repo: $repoRoot"
  Write-Factory "[factory] Python: $pythonPath"
  Write-Factory "[factory] Git: $gitPath"
  Write-Factory "[factory] BaseRef: $BaseRef"
  if ($RunId) {
    Write-Factory "[factory] RunId override: $RunId"
  }

  # Validate module importability before doctor/operator.
  Write-Factory "[factory] Running python import check..."
  $importRun = Invoke-PythonCapture -PythonPath $pythonPath -CommandArgs @("-X", "faulthandler", "-c", "import tools.codex.factory") -TimeoutSec $(if ($TimeoutSec -gt 0) { $TimeoutSec } else { 30 })
  if ($importRun.TimedOut -or $importRun.ExitCode -ne 0) {
    Write-FactoryAlways "[factory] Python import check failed: import tools.codex.factory" "Red"
    Write-FactoryAlways "[factory] Cmd: $($importRun.CmdLine)" "Yellow"
    Write-FactoryAlways "[factory] ExitCode: $($importRun.ExitCode)" "Yellow"
    if (-not [string]::IsNullOrWhiteSpace($importRun.AllText)) {
      Write-FactoryAlways "[factory] Tail:" "Yellow"
      Write-FactoryAlways (Trim-Tail -Text $importRun.AllText -LineCount $FailureTailLines)
    }
    exit $EXIT_IMPORT_CHECK
  }
  Write-Factory "[factory] Import check passed."

  # Optional diagnostics.
  Test-GitDirty -GitPath $gitPath
  $null = Test-BaseRef -GitPath $gitPath -Ref $BaseRef

  if ($RunId -and $StrictRunId) {
    $occupied = @(
      @(
        (Join-Path $repoRoot "tools\codex\runs\$RunId"),
        (Join-Path $repoRoot "tools\codex\prompts\$RunId"),
        (Join-Path $repoRoot "tools\codex\worktrees\$RunId")
      ) | Where-Object { Test-Path -LiteralPath $_ }
    )
    if ($occupied.Count -gt 0) {
      Write-FactoryAlways "[factory] strict run-id appears occupied: $RunId" "Red"
      Write-FactoryAlways "[factory] Use --RunId auto/empty, or choose a new run id." "Red"
      exit $EXIT_OPERATOR_STATUS
    }
  }

  if (-not $SkipDoctor) {
    Write-Factory "[factory] Running doctor..."
    $doctorRun = Invoke-PythonCapture -PythonPath $pythonPath -CommandArgs @("-X", "faulthandler", "-m", "tools.codex.factory", "doctor") -LogFile $doctorLog -TimeoutSec $TimeoutSec
    $doctor = Get-LastJsonObjectFromText $doctorRun.AllText

    if ($doctorRun.TimedOut) {
      Write-FactoryAlways "[factory] Doctor timed out." "Red"
      Write-FactoryAlways "[factory] Log: $($doctorRun.LogFile)" "Yellow"
      exit $EXIT_DOCTOR_TIMEOUT
    }
    if (-not $doctor) {
      Write-FactoryAlways "[factory] Doctor JSON parse failed." "Red"
      Write-FactoryAlways "[factory] Log: $($doctorRun.LogFile)" "Yellow"
      if (-not [string]::IsNullOrWhiteSpace($doctorRun.AllText)) {
        Write-FactoryAlways (Trim-Tail -Text $doctorRun.AllText -LineCount $FailureTailLines) "Yellow"
      }
      exit $EXIT_DOCTOR_JSON
    }
    if ($doctorRun.ExitCode -ne 0) {
      Write-FactoryAlways "[factory] Doctor process failed (exit=$($doctorRun.ExitCode))." "Red"
      Write-FactoryAlways "[factory] Log: $($doctorRun.LogFile)" "Yellow"
      exit $EXIT_DOCTOR_PROCESS
    }
    $doctorStatus = [string](Get-ObjectPropertyValue -Object $doctor -Name "status" -Default "")
    if ($doctorStatus -ne "PASS") {
      Write-FactoryAlways "[factory] Doctor status: $doctorStatus" "Red"
      Write-FactoryAlways "[factory] Resolve doctor blockers before phase1-extract." "Red"
      Write-FactoryAlways "[factory] Log: $($doctorRun.LogFile)" "Yellow"
      exit $EXIT_DOCTOR_STATUS
    }
    if ($DoctorOnly) {
      $finalStatus = "PASS"
      if ($Quiet) {
        Write-FactoryAlways "status=$finalStatus"
        Write-FactoryAlways "doctor_log=$($doctorRun.LogFile)"
      } else {
        Write-FactoryAlways "[factory] DoctorOnly completed with PASS." "Green"
        Write-FactoryAlways "[factory] doctor_log: $($doctorRun.LogFile)"
      }
      exit $EXIT_OK
    }
  } elseif ($DoctorOnly) {
    Write-FactoryAlways "[factory] -DoctorOnly cannot be used with -SkipDoctor." "Red"
    exit $EXIT_DOCTOR_STATUS
  } else {
    Write-Factory "[factory] Skipping doctor by request."
  }

  $cmd = @(
    "-X", "faulthandler",
    "-m", "tools.codex.factory",
    "operator", "phase1-extract",
    "--base-ref", $BaseRef
  )
  if ($RunId) { $cmd += @("--run-id", $RunId) }
  if ($StrictRunId) { $cmd += "--strict-run-id" }
  if ($DryRun) { $cmd += "--dry-run" }
  if ($NoOpenVscode) { $cmd += "--no-open-vscode" }
  if ($NoOpenRunboard) { $cmd += "--no-open-runboard" }
  if ($NoOpenFinalReport) { $cmd += "--no-open-final-report" }
  if ($ExtraArgs) { $cmd += $ExtraArgs }

  Write-Factory "[factory] Launching phase1-extract..."
  Write-Factory "[factory] Cmd: $pythonPath $(Join-Arguments $cmd)" "DarkGray"

  $phaseRun = Invoke-PythonCapture -PythonPath $pythonPath -CommandArgs $cmd -LogFile $phaseLog -TimeoutSec $TimeoutSec
  $phase = Get-LastJsonObjectFromText $phaseRun.AllText

  if ($phaseRun.TimedOut) {
    Write-FactoryAlways "[factory] phase1-extract timed out." "Red"
    Write-FactoryAlways "[factory] Log: $($phaseRun.LogFile)" "Yellow"
    exit $EXIT_OPERATOR_TIMEOUT
  }

  if (-not $phase) {
    Write-FactoryAlways "[factory] phase1-extract JSON parse failed." "Red"
    Write-FactoryAlways "[factory] Log: $($phaseRun.LogFile)" "Yellow"
    if (-not [string]::IsNullOrWhiteSpace($phaseRun.AllText)) {
      Write-FactoryAlways "[factory] Tail:" "Yellow"
      Write-FactoryAlways (Trim-Tail -Text $phaseRun.AllText -LineCount $FailureTailLines) "Yellow"
    }
    if ($phaseRun.ExitCode -ne 0) {
      exit $EXIT_OPERATOR_PROCESS
    }
    exit $EXIT_OPERATOR_JSON
  }

  $finalRunId = [string](Get-ObjectPropertyValue -Object $phase -Name "run_id" -Default "")
  $finalStatus = [string](Get-ObjectPropertyValue -Object $phase -Name "status" -Default "")
  $phaseStageLast = [string](Get-ObjectPropertyValue -Object $phase -Name "stage_last_completed" -Default "")
  $phaseStageFailed = [string](Get-ObjectPropertyValue -Object $phase -Name "stage_failed" -Default "")
  $phaseReason = [string](Get-ObjectPropertyValue -Object $phase -Name "reason" -Default "")
  $phaseResumeHint = [string](Get-ObjectPropertyValue -Object $phase -Name "resume_hint" -Default "")

  if ($Quiet) {
    Write-FactoryAlways "run_id=$finalRunId"
    Write-FactoryAlways "status=$finalStatus"
    Write-FactoryAlways "phase_log=$($phaseRun.LogFile)"
  } else {
    Write-FactoryAlways ""
    Write-FactoryAlways "[factory] run_id: $finalRunId"
    Write-FactoryAlways "[factory] status: $finalStatus"
    if (-not [string]::IsNullOrWhiteSpace($phaseStageLast)) {
      Write-FactoryAlways "[factory] stage_last_completed: $phaseStageLast"
    }
    if (-not [string]::IsNullOrWhiteSpace($phaseStageFailed)) {
      Write-FactoryAlways "[factory] stage_failed: $phaseStageFailed" "Yellow"
    }
    if (-not [string]::IsNullOrWhiteSpace($phaseReason)) {
      Write-FactoryAlways "[factory] reason: $phaseReason" "Yellow"
    }
    if (-not [string]::IsNullOrWhiteSpace($phaseResumeHint)) {
      Write-FactoryAlways "[factory] resume_hint: $phaseResumeHint"
    }
  }

  if ($StrictRunId -and [string]::IsNullOrWhiteSpace($finalRunId)) {
    Write-FactoryAlways "[factory] Strict run-id requested but response did not include run_id." "Red"
    Write-FactoryAlways "[factory] Log: $($phaseRun.LogFile)" "Yellow"
    exit $EXIT_OPERATOR_STATUS
  }

  if ($phaseRun.ExitCode -ne 0 -and $VerboseLog) {
    Write-FactoryAlways "[factory] operator exit code: $($phaseRun.ExitCode)" "Yellow"
  }
  if ($VerboseLog -and -not [string]::IsNullOrWhiteSpace($phaseRun.AllText)) {
    Write-FactoryAlways "[factory] Raw output (tail):" "DarkGray"
    Write-FactoryAlways (Trim-Tail -Text $phaseRun.AllText -LineCount $FailureTailLines) "DarkGray"
  }

  $runFolderRel = if ([string]::IsNullOrWhiteSpace($finalRunId)) { "tools/codex/runs/<RUN_ID>" } else { "tools/codex/runs/$finalRunId" }
  $reportRel = "$runFolderRel/Z_integrator/FINAL_REPORT.txt"

  if ($finalStatus -ne "PASS") {
    Write-FactoryAlways "[factory] phase1-extract returned non-PASS status." "Red"
    Write-FactoryAlways "[factory] Log: $($phaseRun.LogFile)" "Yellow"
    if (-not [string]::IsNullOrWhiteSpace($phaseRun.AllText)) {
      Write-FactoryAlways (Trim-Tail -Text $phaseRun.AllText -LineCount $FailureTailLines) "Yellow"
    }
    exit $EXIT_OPERATOR_STATUS
  }

  if (-not $Quiet) {
    Write-FactoryAlways ""
    Write-FactoryAlways "[factory] Manual worker step:"
    Write-FactoryAlways "Ctrl+Alt+P -> New Codex Agent -> paste PROMPT_WORKER.txt"
    Write-FactoryAlways "[factory] Final report path:"
    Write-FactoryAlways $reportRel
    Write-FactoryAlways "[factory] Run folder path:"
    Write-FactoryAlways $runFolderRel
    Write-FactoryAlways ""
    Write-FactoryAlways "[factory] Summary:"
    Write-FactoryAlways "[factory] status=$finalStatus run_id=$finalRunId"
    Write-FactoryAlways "[factory] logs doctor=$doctorLog phase=$phaseLog"
    Write-FactoryAlways "[factory] next=Open $reportRel"
  }

  exit $EXIT_OK
} catch {
  Write-FactoryAlways "[factory] internal_error: $($_.Exception.Message)" "Red"
  if ($VerboseLog) {
    Write-FactoryAlways "[factory] internal_error_detail: $($_.ScriptStackTrace)" "DarkGray"
  }
  exit $EXIT_OPERATOR_PROCESS
} finally {
  Pop-Location
}
