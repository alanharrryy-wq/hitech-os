@echo off
setlocal
set "ROOT=%~dp0"
set "PS1=%ROOT%internal\wrappers\warm_dev_routes.ps1"

if not exist "%PS1%" (
  echo No encontre el calentador de rutas:
  echo %PS1%
  exit /b 1
)

where pwsh.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  pwsh.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
) else (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
)
endlocal
