@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"
set "PRISMA_WRAPPER=%PCC_ROOT%internal\wrappers\cloud_command_center_3160.ps1"

echo.
echo ============================================================
echo PRISMA - CLOUD COMMAND CENTER 3160
echo Abre el cockpit privado PRISMA Cloud Command Center.
echo No toca Control Center 3150 ni levanta el stack completo.
echo Root: %PCC_ROOT%
echo ============================================================
echo.

if not exist "%PRISMA_WRAPPER%" (
  echo Falta wrapper oficial: %PRISMA_WRAPPER%
  exit /b 2
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PRISMA_WRAPPER%" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA Cloud Command Center 3160 fallo con exit code %RC%.
  echo Revisa F:\descargasf\latest_CLOUD_COMMAND_CENTER_3160.zip
  pause
)

exit /b %RC%
