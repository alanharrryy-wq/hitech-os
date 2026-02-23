<#
.SYNOPSIS
Generate a deterministic plaintext unified diff artifact.

.DESCRIPTION
Writes `git diff --no-color --patch` output to disk and returns a summary object.
Supports staged-only mode via `--cached`.
#>

param(
  [Alias("RepoPath")]
  [string]$WriteDiffRepoPath,
  [Alias("OutPath")]
  [string]$WriteDiffOutPath,
  [Alias("BaseRef")]
  [string]$WriteDiffBaseRef = "HEAD",
  [Alias("StagedOnly")]
  [switch]$WriteDiffStagedOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$externalHelperPath = Join-Path $PSScriptRoot "Invoke-External.ps1"
$externalHelperPath = (Resolve-Path -LiteralPath $externalHelperPath).Path
. $externalHelperPath

function Resolve-OutputPath {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$BasePath,
    [Parameter(Mandatory = $true)]
    [string]$RawOutPath
  )

  if ([System.IO.Path]::IsPathRooted($RawOutPath)) {
    return $RawOutPath
  }

  return (Join-Path $BasePath $RawOutPath)
}

function Parse-NumStatLine {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$Line
  )

  $parts = $Line -split "`t", 3
  if ($parts.Count -lt 3) {
    return $null
  }

  return [pscustomobject]@{
    Insertions = $parts[0]
    Deletions = $parts[1]
    Path = $parts[2]
  }
}

function Write-UnifiedDiffArtifact {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory = $true)]
    [string]$RepoPath,

    [Parameter(Mandatory = $true)]
    [string]$OutPath,

    [string]$BaseRef = "HEAD",

    [switch]$StagedOnly
  )

  if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) {
    throw "Write-UnifiedDiffArtifact: RepoPath does not exist: $RepoPath"
  }

  $resolvedRepoPath = (Resolve-Path -LiteralPath $RepoPath).Path
  $resolvedOutPath = Resolve-OutputPath -BasePath $resolvedRepoPath -RawOutPath $OutPath

  $outDir = Split-Path -Parent $resolvedOutPath
  if (-not [string]::IsNullOrWhiteSpace($outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force -WhatIf:$false -Confirm:$false | Out-Null
  }

  $diffArgs = @("diff", "--no-color", "--patch")
  $numstatArgs = @("diff", "--no-color", "--numstat")

  if ($StagedOnly) {
    $diffArgs += "--cached"
    $numstatArgs += "--cached"
  }
  else {
    $diffArgs += $BaseRef
    $numstatArgs += $BaseRef
  }

  $diffArgs += "--"
  $numstatArgs += "--"

  $patchResult = Invoke-ExternalCommand -ExePath "git" -ArgList $diffArgs -WorkDir $resolvedRepoPath -NoThrow
  if (-not $patchResult.Ok -and $patchResult.ExitCode -ne 0) {
    throw "Write-UnifiedDiffArtifact: git diff failed (exit $($patchResult.ExitCode)): $($patchResult.Output)"
  }

  $patchText = if ($null -eq $patchResult.Stdout) { "" } else { [string]$patchResult.Stdout }
  if (-not [string]::IsNullOrEmpty($patchText) -and -not $patchText.EndsWith("`n")) {
    $patchText += "`n"
  }

  $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
  [System.IO.File]::WriteAllText($resolvedOutPath, $patchText, $utf8NoBom)

  $numstatResult = Invoke-ExternalCommand -ExePath "git" -ArgList $numstatArgs -WorkDir $resolvedRepoPath -NoThrow
  if (-not $numstatResult.Ok -and $numstatResult.ExitCode -ne 0) {
    throw "Write-UnifiedDiffArtifact: git diff --numstat failed (exit $($numstatResult.ExitCode)): $($numstatResult.Output)"
  }

  $changedFiles = New-Object System.Collections.Generic.List[string]
  $insertions = 0
  $deletions = 0

  if (-not [string]::IsNullOrWhiteSpace($numstatResult.Stdout)) {
    $numstatLines = $numstatResult.Stdout -split "`r?`n"
    foreach ($line in $numstatLines) {
      if ([string]::IsNullOrWhiteSpace($line)) {
        continue
      }

      $parsed = Parse-NumStatLine -Line $line
      if ($null -eq $parsed) {
        continue
      }

      $changedFiles.Add($parsed.Path)
      if ($parsed.Insertions -match '^\d+$') {
        $insertions += [int]$parsed.Insertions
      }
      if ($parsed.Deletions -match '^\d+$') {
        $deletions += [int]$parsed.Deletions
      }
    }
  }

  return [pscustomobject]@{
    RepoPath = $resolvedRepoPath
    OutPath = $resolvedOutPath
    BaseRef = $BaseRef
    StagedOnly = [bool]$StagedOnly
    FilesChanged = $changedFiles.Count
    Insertions = $insertions
    Deletions = $deletions
    ChangedFiles = @($changedFiles)
    PatchBytes = $utf8NoBom.GetByteCount($patchText)
  }
}

if ($PSBoundParameters.ContainsKey("WriteDiffRepoPath") -and $PSBoundParameters.ContainsKey("WriteDiffOutPath")) {
  Write-UnifiedDiffArtifact `
    -RepoPath $WriteDiffRepoPath `
    -OutPath $WriteDiffOutPath `
    -BaseRef $WriteDiffBaseRef `
    -StagedOnly:$WriteDiffStagedOnly
}
