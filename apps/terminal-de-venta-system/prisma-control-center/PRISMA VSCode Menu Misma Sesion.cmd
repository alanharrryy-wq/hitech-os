@echo off
REM PRISMA_VSCODE_MENU_FAST_IGNIT_FOLDER_OPEN
setlocal
set "PS1=%~dp0PRISMA VSCode Menu Misma Sesion.ps1"

if not exist "%PS1%" (
  echo No encontre el launcher PowerShell:
  echo %PS1%
  pause
  exit /b 1
)

where pwsh.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  pwsh.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
) else (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
)
endlocal
