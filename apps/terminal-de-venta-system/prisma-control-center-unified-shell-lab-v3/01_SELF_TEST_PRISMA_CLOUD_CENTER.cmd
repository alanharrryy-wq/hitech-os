@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PRISMA_CLOUD_CENTER_ROOT=%CD%"
set "PRISMA_PROTECTED_CURRENT=F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center"
set "PRISMA_OUT_DIR=F:\descargasf"

echo ============================================================
echo PRISMA Cloud Center - self-test
echo Ruta: %PRISMA_CLOUD_CENTER_ROOT%
echo No ejecuta acciones admin ni mutaciones cloud.
echo ============================================================
echo.

py -3 "%PRISMA_CLOUD_CENTER_ROOT%\internal\py\prisma_unified_lab_v3.py" --lab-root "%PRISMA_CLOUD_CENTER_ROOT%" --protected-current "%PRISMA_PROTECTED_CURRENT%" --out-dir "%PRISMA_OUT_DIR%" --self-test

if errorlevel 1 (
  echo.
  echo [ERROR] Self-test fallo.
  pause
  exit /b 1
)

echo.
echo [OK] Self-test PASS.
pause
