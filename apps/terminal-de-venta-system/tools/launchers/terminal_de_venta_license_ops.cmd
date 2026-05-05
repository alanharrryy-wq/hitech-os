@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%.") do set "ROOT=%%~fI"

python "%ROOT%\tooling\licensing\prisma_license_ops.py" --root "%ROOT%" %*
exit /b %ERRORLEVEL%
