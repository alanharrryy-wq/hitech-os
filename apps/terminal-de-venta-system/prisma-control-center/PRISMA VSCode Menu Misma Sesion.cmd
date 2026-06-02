@echo off
setlocal
set "PS1=F:\descargasf\PRISMA VSCode Menu Misma Sesion.ps1"

if not exist "%PS1%" (
  echo No encontre el launcher PowerShell:
  echo %PS1%
  echo.
  echo Primero ejecuta o extrae el parche vssfix para crear ese archivo.
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
