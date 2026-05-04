@echo off
setlocal
set REPO=F:\repos\hitech-os
set SYSTEM=%REPO%\apps\terminal-de-venta-system
set DOCTOR=%SYSTEM%\tools\prisma-visual-os\ai_doctor_prisma_show_pos_00y.py
py "%DOCTOR%" --target-root "%REPO%" --out-dir F:\descargasf %*
endlocal
