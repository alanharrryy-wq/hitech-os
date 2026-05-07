@echo off
setlocal EnableExtensions

REM PRISMA Terminal de Venta - Cloudflare Industrial Launcher
REM Wrapper corto para evitar el limite de longitud de cmd.exe.
REM Coloca este .cmd junto al .ps1 y ejecutalo desde cualquier carpeta.

set "SCRIPT_DIR=%~dp0"
set "PS1=%SCRIPT_DIR%terminal_de_venta_cloudflare_industrial.ps1"

if not exist "%PS1%" (
  echo [ERROR] No encuentro el PowerShell companion:
  echo         %PS1%
  exit /b 10
)

pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
set "EXITCODE=%ERRORLEVEL%"
echo.
echo Exit code: %EXITCODE%
exit /b %EXITCODE%

