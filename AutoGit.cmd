@echo off
setlocal EnableExtensions
set "REPO_ROOT=%~dp0"
set "TOOL_ROOT=%REPO_ROOT%autogit\"

if not exist "%TOOL_ROOT%bin\autogit.ps1" (
  echo.
  echo [AutoGit] ERROR: no encontre "%TOOL_ROOT%bin\autogit.ps1".
  echo Revisa que exista F:\repos\hitech-os\autogit\bin\autogit.ps1
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
