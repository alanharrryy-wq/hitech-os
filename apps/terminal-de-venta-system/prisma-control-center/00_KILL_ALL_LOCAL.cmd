@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - KILL ALL LOCAL
echo Mata puertos/procesos locales PRISMA y tunnel Cloudflare local.
echo Sin preguntas. Sin tocar codigo, DBs ni archivos de trabajo.
echo Root: %PCC_ROOT%
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\kill_everything.ps1" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA KILL ALL LOCAL fallo con exit code %RC%.
  echo Revisa F:\descargasf\latest_KILL_EVERYTHING.zip
  pause
)

exit /b %RC%
