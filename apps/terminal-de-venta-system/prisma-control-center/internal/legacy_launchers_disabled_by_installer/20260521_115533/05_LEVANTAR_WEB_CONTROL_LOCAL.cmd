@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - levantar Web + Control local
echo Levanta Web/EIT 3110 y Control Center 3150; siempre genera health y ZIP.
echo Puertos: 3000 Chart Lab, 3110 Web/EIT, 3120 Tablet, 3130 PC, 3140 Mobile, 3150 Control
echo ZIP: F:\descargasf
echo Root: %PCC_ROOT%
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\control_center_safe.ps1" -StartWeb %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA - levantar Web + Control local fallo con exit code %RC%.
  echo Revisa el ZIP mas reciente en F:\descargasf
  pause
)

exit /b %RC%
