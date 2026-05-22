@echo off
setlocal EnableExtensions
set "PCC_ROOT=%~dp0"

echo.
echo ============================================================
echo PRISMA - ABRIR ATLAS DE DEPENDENCIAS
echo Abre el Black Glass Atlas local de prisma-control-center.
echo Root: %PCC_ROOT%
echo ============================================================
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PCC_ROOT%internal\wrappers\open_dependency_atlas.ps1" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] PRISMA ATLAS DEPENDENCIAS fallo con exit code %RC%.
  echo Revisa F:\descargasf\latest_DEPENDENCY_ATLAS_OPEN.zip
  pause
)

exit /b %RC%
