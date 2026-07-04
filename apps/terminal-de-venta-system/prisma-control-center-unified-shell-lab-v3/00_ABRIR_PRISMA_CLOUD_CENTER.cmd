@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PRISMA_CLOUD_CENTER_ROOT=%CD%"
set "PRISMA_PROTECTED_CURRENT=F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center"
set "PRISMA_OUT_DIR=F:\descargasf"
set "PRISMA_CLOUD_CENTER_PORT=3160"

echo ============================================================
echo PRISMA Cloud Center
echo Puerto local: 3160
echo Ruta: %PRISMA_CLOUD_CENTER_ROOT%
echo No mata procesos. No despliega Cloudflare. No lee secretos.
echo ============================================================
echo.

py -3 "%PRISMA_CLOUD_CENTER_ROOT%\internal\py\prisma_unified_lab_v3.py" --lab-root "%PRISMA_CLOUD_CENTER_ROOT%" --protected-current "%PRISMA_PROTECTED_CURRENT%" --out-dir "%PRISMA_OUT_DIR%" --port 3160

if errorlevel 1 (
  echo.
  echo [ERROR] No pude abrir Prisma Cloud Center.
  pause
  exit /b 1
)

echo.
echo [OK] Prisma Cloud Center abierto en http://127.0.0.1:3160/unified-shell.html
pause
