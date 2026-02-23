<#
.SYNOPSIS
Safely invoke an external command with explicit argument handling.

.DESCRIPTION
Resolves an executable path, runs it with an argument array, captures stdout/stderr,
and returns a deterministic structured object. This avoids argument-loss bugs caused
by PowerShell automatic variables such as $Args.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-ExternalExecutable {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath
  )

  if ([string]::IsNullOrWhiteSpace($ExePath)) {
    throw "Resolve-ExternalExecutable: ExePath is required."
  }

  if (($ExePath.Contains("\") -or $ExePath.Contains("/")) -or [System.IO.Path]::IsPathRooted($ExePath)) {
    if (-not (Test-Path -LiteralPath $ExePath -PathType Leaf)) {
      throw "Executable path does not exist: $ExePath"
    }
    return [pscustomobject]@{
      Path = (Resolve-Path -LiteralPath $ExePath).Path
      Source = "LiteralPath"
    }
  }

  $candidates = @(Get-Command -Name $ExePath -All -ErrorAction Stop)
  if ($candidates.Count -eq 0) {
    throw "Executable not found in PATH: $ExePath"
  }

  $selected = $candidates |
    Where-Object { $_.CommandType -eq "Application" } |
    Select-Object -First 1

  if (-not $selected) {
    $selected = $candidates | Select-Object -First 1
  }

  $resolvedPath = $selected.Source
  if ([string]::IsNullOrWhiteSpace($resolvedPath) -and $selected.Path) {
    $resolvedPath = $selected.Path
  }
  if ([string]::IsNullOrWhiteSpace($resolvedPath)) {
    throw "Unable to resolve executable path for: $ExePath"
  }

  return [pscustomobject]@{
    Path = $resolvedPath
    Source = "$($selected.CommandType):$resolvedPath"
  }
}

function Format-ArgPreview {
  [CmdletBinding()]
  param(
    [string[]]$ArgList
  )

  if ($null -eq $ArgList -or $ArgList.Count -eq 0) {
    return "<none>"
  }

  $quoted = foreach ($item in $ArgList) {
    $value = [string]$item
    if ($value -match '[\s"]') {
      '"' + ($value -replace '"', '\"') + '"'
    }
    else {
      $value
    }
  }

  return ($quoted -join " ")
}

function Invoke-ExternalCommand {
  <#
  .SYNOPSIS
  Run an external command with deterministic argument handling.

  .PARAMETER ExePath
  Executable name or full executable path.

  .PARAMETER ArgList
  External argument array.

  .PARAMETER WorkDir
  Working directory for command execution.

  .PARAMETER NoThrow
  If set, do not throw when exit code is non-zero.

  .NOTES
  Debug behavior uses the built-in CommonParameters (`-Debug`), so there is no
  custom parameter named Debug that could conflict with PowerShell semantics.
  #>
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath,

    [string[]]$ArgList = @(),

    [Parameter(Mandatory = $true)]
    [string]$WorkDir,

    [switch]$NoThrow
  )

  if (-not (Test-Path -LiteralPath $WorkDir -PathType Container)) {
    throw "Invoke-ExternalCommand: WorkDir does not exist: $WorkDir"
  }

  $resolvedCommand = Resolve-ExternalExecutable -ExePath $ExePath
  $resolvedWorkDir = (Resolve-Path -LiteralPath $WorkDir).Path
  $argPreview = Format-ArgPreview -ArgList $ArgList
  $commandLine = "$($resolvedCommand.Path) $argPreview".TrimEnd()

  Write-Debug "[Invoke-ExternalCommand] Source: $($resolvedCommand.Source)"
  Write-Debug "[Invoke-ExternalCommand] ExePath: $($resolvedCommand.Path)"
  Write-Debug "[Invoke-ExternalCommand] ArgList: $argPreview"
  Write-Debug "[Invoke-ExternalCommand] WorkDir: $resolvedWorkDir"

  $start = [DateTimeOffset]::UtcNow
  $process = $null

  try {
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $resolvedCommand.Path
    $startInfo.WorkingDirectory = $resolvedWorkDir
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true

    foreach ($arg in $ArgList) {
      [void]$startInfo.ArgumentList.Add([string]$arg)
    }

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo

    if (-not $process.Start()) {
      throw "Failed to start external command: $($resolvedCommand.Path)"
    }

    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    [System.Threading.Tasks.Task]::WaitAll($stdoutTask, $stderrTask)

    $stdout = $stdoutTask.Result
    $stderr = $stderrTask.Result

    $outputParts = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($stdout)) {
      $outputParts.Add($stdout.TrimEnd("`r", "`n"))
    }
    if (-not [string]::IsNullOrWhiteSpace($stderr)) {
      $outputParts.Add($stderr.TrimEnd("`r", "`n"))
    }
    $combinedOutput = [string]::Join([Environment]::NewLine, $outputParts.ToArray())
    $durationMs = [int][Math]::Round(([DateTimeOffset]::UtcNow - $start).TotalMilliseconds)
    $exitCode = [int]$process.ExitCode

    $result = [pscustomobject]@{
      Ok = ($exitCode -eq 0)
      ExitCode = $exitCode
      Stdout = $stdout
      Stderr = $stderr
      CommandLine = $commandLine
      DurationMs = $durationMs
      ExePath = $resolvedCommand.Path
      CommandSource = $resolvedCommand.Source
      ArgList = @($ArgList)
      WorkDir = $resolvedWorkDir
      Output = $combinedOutput
    }

    $global:LASTEXITCODE = $result.ExitCode

    if (-not $result.Ok -and -not $NoThrow) {
      $outputPreview = if ([string]::IsNullOrWhiteSpace($result.Output)) { "(no output)" } else { $result.Output }
      throw "External command failed. ExitCode=$($result.ExitCode); CommandLine=$($result.CommandLine); Source=$($result.CommandSource)`n$outputPreview"
    }

    return $result
  }
  finally {
    if ($process) {
      $process.Dispose()
    }
  }
}
