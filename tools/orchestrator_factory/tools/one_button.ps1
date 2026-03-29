[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$ErrorActionPreference = 'Stop'

function Resolve-FrameworkRoot {
    param([string]$ScriptPath)

    $toolsDir = Split-Path -Parent $ScriptPath
    return Split-Path -Parent $toolsDir
}

function Resolve-PythonExecutable {
    $candidates = @('python', 'py')
    foreach ($candidate in $candidates) {
        try {
            $command = Get-Command $candidate -ErrorAction Stop
            if ($null -ne $command) {
                return $candidate
            }
        }
        catch {
            continue
        }
    }
    throw 'No Python executable was found on PATH. Install Python or add it to PATH before running one_button.ps1.'
}

$scriptPath = $MyInvocation.MyCommand.Path
$frameworkRoot = Resolve-FrameworkRoot -ScriptPath $scriptPath
$entrypoint = Join-Path $frameworkRoot 'tools\execution_framework\one_button_session.py'

if (-not (Test-Path -LiteralPath $entrypoint)) {
    throw "Entrypoint not found: $entrypoint"
}

$pythonExe = Resolve-PythonExecutable
$resolvedArgs = @($entrypoint)
if ($Arguments) {
    $resolvedArgs += $Arguments
}

Write-Host 'Launching one-button runtime core...' -ForegroundColor Cyan
Write-Progress -Activity 'one-button runtime core' -Status 'Invoking Python entrypoint' -PercentComplete 25
& $pythonExe @resolvedArgs
Write-Progress -Activity 'one-button runtime core' -Completed
exit $LASTEXITCODE
