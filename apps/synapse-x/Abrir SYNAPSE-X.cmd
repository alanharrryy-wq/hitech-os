@echo off
setlocal

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "PYEXE=C:\Users\alanh\AppData\Local\Programs\Python\Python312\python.exe"
set "STARTER=%ROOT%\synapse-x_starter.py"

if not exist "%STARTER%" (
  echo [ERROR] No encontre el launcher:
  echo         %STARTER%
  echo.
  pause
  exit /b 1
)

if not exist "%PYEXE%" (
  echo [ERROR] No encontre python.exe:
  echo         %PYEXE%
  echo.
  pause
  exit /b 1
)

set "SYNAPSE_X_ROOT=%ROOT%"
set "SYNAPSE_X_FORCE_CONSOLE=1"

"%PYEXE%" "%STARTER%" --root "%ROOT%"
set "CODE=%ERRORLEVEL%"

if not "%CODE%"=="0" (
  echo.
  echo [ERROR] SYNAPSE-X termino con exit code %CODE%.
  echo.
  pause
)

exit /b %CODE%