@echo off
setlocal
set "ROOT=%~dp0"
if /I "%~1"=="legacy" (
  start "" "%ROOT%sistema-ui\identidad\index.html"
  endlocal
  exit /b 0
)
call "%ROOT%ABRIR-VISUAL.cmd"
endlocal
