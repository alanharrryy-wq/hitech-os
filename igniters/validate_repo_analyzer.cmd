@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0_common.ps1" -Action validate_repo_analyzer
exit /b %errorlevel%
