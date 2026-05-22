@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - CONTROL CENTER SEGURO v3
echo Levanta Control Center 3150 y Web/EIT 3110 sin bloquear por todo el stack.
echo Corrige: HOME readonly, health JSON mezclado y ZIP con logs bloqueados.
echo Siempre genera evidencia en F:\descargasf.
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\control_center_safe.ps1" -StartWeb %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] Control Center seguro termino con exit code %RC%.
  echo Revisa F:\descargasf\latest_CONTROL_SAFE.zip
  pause
)

exit /b %RC%
