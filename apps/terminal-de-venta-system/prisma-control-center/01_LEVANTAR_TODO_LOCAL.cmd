@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - levantar TODO local
echo Resetea 3000,3110,3120,3130,3140,3150 y levanta stack local.
echo Puertos: 3000 Chart Lab, 3110 Web/EIT, 3120 Tablet, 3130 PC, 3140 Mobile, 3150 Control
echo ZIP: F:\descargasf
echo Root: %PCC_ROOT%
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\local_up.ps1" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA - levantar TODO local fallo con exit code %RC%.
  echo Revisa el ZIP mas reciente en F:\descargasf
  pause
)

exit /b %RC%
