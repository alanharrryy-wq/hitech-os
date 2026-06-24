@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"
set "LAB_ROOT=F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center-unified-shell-lab-v3"
set "PRISMA_PROTECTED_CURRENT=%PCC_ROOT:~0,-1%"
set "PRISMA_OUT_DIR=F:\descargasf"

echo.
echo ============================================================
echo PRISMA - CLOUD COMMAND CENTER 3160
echo Abre el cockpit privado PRISMA Cloud Command Center.
echo No toca Control Center 3150 ni levanta el stack completo.
echo Lab: %LAB_ROOT%
echo ============================================================
echo.

py -3 "%LAB_ROOT%\internal\py\prisma_unified_lab_v3.py" --lab-root "%LAB_ROOT%" --protected-current "%PRISMA_PROTECTED_CURRENT%" --out-dir "%PRISMA_OUT_DIR%" --port 3160
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA Cloud Command Center 3160 fallo con exit code %RC%.
  pause
)

exit /b %RC%
