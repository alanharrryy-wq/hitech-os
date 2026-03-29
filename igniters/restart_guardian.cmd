@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0_common.ps1" -Action restart_guardian
exit /b %errorlevel%
