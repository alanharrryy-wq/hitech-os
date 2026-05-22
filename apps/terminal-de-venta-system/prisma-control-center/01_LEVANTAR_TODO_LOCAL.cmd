@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - LEVANTAR TODO LOCAL
echo Libera puertos PRISMA, levanta stack local y abre Control Center.
echo Sin preguntas si algo ocupa puerto: se mata y se monta limpio.
echo Root: %PCC_ROOT%
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\local_up.ps1" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA TODO LOCAL fallo con exit code %RC%.
  echo Revisa F:\descargasf\latest_ALL_LOCAL.zip
  pause
)

exit /b %RC%
