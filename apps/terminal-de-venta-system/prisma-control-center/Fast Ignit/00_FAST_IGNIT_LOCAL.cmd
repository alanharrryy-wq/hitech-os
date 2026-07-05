@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
where pwsh.exe >nul 2>nul
if %ERRORLEVEL%==0 (
  pwsh.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%FastIgnit.ps1" --mode start --ports "3000,3110,3120,3130,3140,3150,3160" --concurrency 4 --timeout 180 --reset-ports "3160" --stream --hold
  exit /b %ERRORLEVEL%
)
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%FastIgnit.ps1" --mode start --ports "3000,3110,3120,3130,3140,3150,3160" --concurrency 4 --timeout 180 --reset-ports "3160" --stream --hold
exit /b %ERRORLEVEL%
