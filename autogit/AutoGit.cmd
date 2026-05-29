@echo off
setlocal EnableExtensions
set "TOOL_ROOT=%~dp0"
set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%PS%" (
  "%PS%" -NoProfile -ExecutionPolicy Bypass -File "%TOOL_ROOT%bin\autogit.ps1" %*
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%TOOL_ROOT%bin\autogit.ps1" %*
)
exit /b %ERRORLEVEL%
