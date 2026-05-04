@echo off
setlocal
set REPO=F:\repos\hitech-os
set DOCTOR=%REPO%\apps\terminal-de-venta-system\tools\prisma-visual-os\doctor_prisma_show_pos_scan_00u.py
py "%DOCTOR%" --target-root "%REPO%" --out-dir "F:\descargasf" --scan --start-missing %*
endlocal
