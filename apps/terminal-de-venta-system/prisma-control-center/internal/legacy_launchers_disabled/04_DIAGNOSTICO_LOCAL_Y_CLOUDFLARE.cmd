@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - diagnostico local y Cloudflare
echo Solo lectura. No mata, no levanta, no modifica.
echo Puertos: 3000 Chart Lab, 3110 Web/EIT, 3120 Tablet, 3130 PC, 3140 Mobile, 3150 Control
echo ZIP: F:\descargasf
echo Root: %PCC_ROOT%
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\health.ps1" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA - diagnostico local y Cloudflare fallo con exit code %RC%.
  echo Revisa el ZIP mas reciente en F:\descargasf
  pause
)

exit /b %RC%
