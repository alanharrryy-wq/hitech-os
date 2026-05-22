@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PRISMA_LAB_ROOT=%CD%"
set "PRISMA_PROTECTED_CURRENT=F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center"
set "PRISMA_OUT_DIR=F:\descargasf"
set "PRISMA_LAB_PORT=3160"

echo ============================================================
echo PRISMA - UNIFIED SHELL LAB V3.1 RESURRECTED
echo Puerto LAB fijo: 3160
echo No toca Control Center bueno en 3150.
echo Root: %PRISMA_LAB_ROOT%
echo ============================================================
echo.

py -3 "%PRISMA_LAB_ROOT%\internal\py\prisma_unified_lab_v3.py" --lab-root "%PRISMA_LAB_ROOT%" --protected-current "%PRISMA_PROTECTED_CURRENT%" --out-dir "%PRISMA_OUT_DIR%" --port 3160

if errorlevel 1 (
  echo.
  echo [ERROR] No pude abrir Unified Shell Lab v3.1.
  pause
  exit /b 1
)

echo.
echo [OK] Unified Shell Lab abierto en http://127.0.0.1:3160/unified-shell.html
pause
