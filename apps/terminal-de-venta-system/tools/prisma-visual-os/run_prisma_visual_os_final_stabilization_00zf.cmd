@echo off
setlocal
set "REPO=F:epos\hitech-os"
set "SYSTEM=%REPO%pps	erminal-de-venta-system"
set "OUT=F:\descargasf"
py "%SYSTEM%	ools\prisma-visual-os	ree\prisma_visual_os_final_stabilization_00zf.py" --target-root "%SYSTEM%" --out-dir "%OUT%" --verify
