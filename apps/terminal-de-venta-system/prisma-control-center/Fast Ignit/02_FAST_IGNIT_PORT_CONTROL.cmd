@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
set "ENGINE=%SCRIPT_DIR%internal\fast_port_control.py"
if not exist "%ENGINE%" (
  echo No encontre motor Port Control: %ENGINE%
  pause
  exit /b 1
)
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 "%ENGINE%" --mode menu --output-dir "F:\descargasf"
  exit /b %ERRORLEVEL%
)
where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python "%ENGINE%" --mode menu --output-dir "F:\descargasf"
  exit /b %ERRORLEVEL%
)
echo No encontre Python para Port Control.
pause
exit /b 1
