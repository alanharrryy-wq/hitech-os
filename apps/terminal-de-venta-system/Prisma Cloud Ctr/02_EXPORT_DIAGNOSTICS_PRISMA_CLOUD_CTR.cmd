@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PRISMA_CLOUD_CTR_ROOT=%CD%"
set "PRISMA_PROTECTED_CURRENT=F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center"
set "PRISMA_OUT_DIR=F:\descargasf"

echo ============================================================
echo PRISMA Cloud Ctr - diagnostics
echo Ruta: %PRISMA_CLOUD_CTR_ROOT%
echo Exporta diagnostico sanitizado. No incluye secretos.
echo ============================================================
echo.

py -3 "%PRISMA_CLOUD_CTR_ROOT%\internal\py\prisma_unified_lab_v3.py" --lab-root "%PRISMA_CLOUD_CTR_ROOT%" --protected-current "%PRISMA_PROTECTED_CURRENT%" --out-dir "%PRISMA_OUT_DIR%" --export-diagnostics

if errorlevel 1 (
  echo.
  echo [ERROR] Export diagnostics fallo.
  pause
  exit /b 1
)

echo.
echo [OK] Diagnostics exportados en F:\descargasf.
pause
