$ErrorActionPreference = "Stop"
# PRISMO_PANEL_WRAPPER_SERVER_AWARE: wrapper PRISMO-aware, loads Gemini process env before launching panel.

# PRISMO_LAUNCHER_GEMINI_ENV_GUARD_BEGIN
function Set-PrismoAiProcessEnv {
  $userGemini = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY", "User")
  if ([string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY) -and -not [string]::IsNullOrWhiteSpace($userGemini)) {
    $env:GEMINI_API_KEY = $userGemini
  }

  if (-not [string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY)) {
    $env:PRISMO_AI_ENABLED = "true"
    $env:PRISMO_AI_DEMO_MODE = "false"
  } else {
    if ([string]::IsNullOrWhiteSpace($env:PRISMO_AI_ENABLED)) { $env:PRISMO_AI_ENABLED = "false" }
    if ([string]::IsNullOrWhiteSpace($env:PRISMO_AI_DEMO_MODE)) { $env:PRISMO_AI_DEMO_MODE = "true" }
  }
}
Set-PrismoAiProcessEnv
# PRISMO_LAUNCHER_GEMINI_ENV_GUARD_END
& (Join-Path $PSScriptRoot "_launcher_common.ps1") -Profile "panel" @args
exit $LASTEXITCODE
