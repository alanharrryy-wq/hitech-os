@echo off
setlocal EnableExtensions

REM PRISMA Mamastrophic Menu Launcher
REM Put this .bat next to MENU.ps1:
REM F:\repos\hitech-os\tools\Plawright Mamastrophic\mamenu.bat

set "HERE=%~dp0"
set "MENU=%HERE%MENU.ps1"

if not exist "%MENU%" (
  set "MENU=F:\repos\hitech-os\tools\Plawright Mamastrophic\MENU.ps1"
)

if not exist "%MENU%" (
  echo.
  echo ============================================================
  echo  ERROR: No encuentro MENU.ps1
  echo ============================================================
  echo.
  echo Busque aqui:
  echo   %HERE%MENU.ps1
  echo.
  echo Y tambien aqui:
  echo   F:\repos\hitech-os\tools\Plawright Mamastrophic\MENU.ps1
  echo.
  echo Coloca este .bat dentro de:
  echo   F:\repos\hitech-os\tools\Plawright Mamastrophic
  echo.
  pause
  exit /b 1
)

echo.
echo ============================================================
echo  PRISMA Mamastrophic Menu
echo ============================================================
echo Default GPU: off. No start, no kill, no DB, no deploy.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%MENU%" %*

set "CODE=%ERRORLEVEL%"

echo.
if "%CODE%"=="0" (
  echo ============================================================
  echo  MENU cerrado correctamente.
  echo ============================================================
) else (
  echo ============================================================
  echo  MENU termino con error. ExitCode=%CODE%
  echo ============================================================
)

echo.
pause
exit /b %CODE%
