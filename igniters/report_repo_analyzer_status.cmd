@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0_common.ps1" -Action report_repo_analyzer_status
exit /b %errorlevel%
