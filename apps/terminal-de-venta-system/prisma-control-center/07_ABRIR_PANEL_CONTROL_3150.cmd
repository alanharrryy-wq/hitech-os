@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - abrir panel Control Center 3150
echo Abre el panel; si 3150 no esta vivo, lo levanta primero.
echo Puertos: 3000 Chart Lab, 3110 Web/EIT, 3120 Tablet, 3130 PC, 3140 Mobile, 3150 Control
echo ZIP: F:\descargasf
echo Root: %PCC_ROOT%
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\control_center_safe.ps1" -PanelOnly %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA - abrir panel Control Center 3150 fallo con exit code %RC%.
  echo Revisa el ZIP mas reciente en F:\descargasf
  pause
)

exit /b %RC%
