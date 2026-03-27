@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0_common.ps1" -Action start_keystone
exit /b %errorlevel%
