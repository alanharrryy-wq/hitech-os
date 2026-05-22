@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - LEVANTAR SOLO UN MODULO + CLOUDFLARE
echo Menu quirurgico: libera el puerto elegido, levanta ese modulo y tunnel.
echo Sin preguntas si algo ocupa puerto: se mata y se monta limpio.
echo Root: %PCC_ROOT%
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\module_cloudflare.ps1" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA MODULO + CLOUDFLARE fallo con exit code %RC%.
  echo Revisa F:\descargasf\latest_MODULE_CLOUDFLARE.zip
  pause
)

exit /b %RC%
