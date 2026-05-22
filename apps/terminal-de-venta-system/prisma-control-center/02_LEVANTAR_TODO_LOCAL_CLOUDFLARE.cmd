@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - LEVANTAR TODO LOCAL + CLOUDFLARE
echo Libera puertos PRISMA, levanta stack local, reinicia tunnel y valida publico.
echo Sin preguntas si algo ocupa puerto: se mata y se monta limpio.
echo Root: %PCC_ROOT%
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\all_up.ps1" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA LOCAL + CLOUDFLARE fallo con exit code %RC%.
  echo Revisa F:\descargasf\latest_ALL_LOCAL_CLOUDFLARE.zip
  pause
)

exit /b %RC%
