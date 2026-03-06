@echo off
setlocal EnableExtensions

set "REPO_ROOT=%~dp0"
set "LAUNCHER=%REPO_ROOT%tools\scripts\Invoke-HitechLoopbackLauncher.ps1"

if not exist "%LAUNCHER%" (
  echo [ERROR] Launcher script not found:
  echo         %LAUNCHER%
  exit /b 1
)

where pwsh >nul 2>&1
if errorlevel 1 (
  echo [ERROR] pwsh is not installed or not in PATH.
  echo Install PowerShell 7+ and try again.
  exit /b 1
)

echo.
echo [HITECH-OS] Starting loopback launcher...
echo Script: %LAUNCHER%
echo.

pwsh -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%" %*
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo.
  echo [ERROR] Launcher failed with exit code %EXIT_CODE%.
)

exit /b %EXIT_CODE%
