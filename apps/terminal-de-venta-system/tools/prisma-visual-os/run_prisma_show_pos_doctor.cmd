@echo off
setlocal
set "REPO=F:\repos\hitech-os"
set "DOCTOR=%REPO%\apps\terminal-de-venta-system\tools\prisma-visual-os\doctor_prisma_show_pos_scan_00x.py"
py "%DOCTOR%" --target-root "%REPO%" --out-dir "F:\descargasf" --scan --start-missing
exit /b %ERRORLEVEL%
