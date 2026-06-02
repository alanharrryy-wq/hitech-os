@echo off
setlocal EnableExtensions
set "TOOL_ROOT=%~dp0"

if not exist "%TOOL_ROOT%bin\autogit.ps1" (
  echo.
  echo [AutoGit] ERROR: no encontre "%TOOL_ROOT%bin\autogit.ps1".
  echo Este AutoGit.cmd debe vivir dentro de F:\repos\hitech-os\autogit
  echo.
  exit /b 9009
)

if not defined AUTOGIT_OUT set "AUTOGIT_OUT=F:\descargasf"
if not defined AUTOGIT_MODE set "AUTOGIT_MODE=full"

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

if exist "%PS%" (
  "%PS%" -NoProfile -ExecutionPolicy Bypass -File "%TOOL_ROOT%bin\autogit.ps1" %*
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%TOOL_ROOT%bin\autogit.ps1" %*
)

set "CODE=%ERRORLEVEL%"

if not "%CODE%"=="0" (
  echo.
  echo [AutoGit] FALLO con codigo %CODE%.
  echo Revisa o sube el ZIP mas reciente en F:\descargasf
  echo.
)

exit /b %CODE%
