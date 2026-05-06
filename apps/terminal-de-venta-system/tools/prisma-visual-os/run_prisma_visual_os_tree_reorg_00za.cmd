@echo off
setlocal
set REPO=F:\repos\hitech-os
set OUT=F:\descargasf
py -3 "%REPO%\apps\terminal-de-venta-system\tools\prisma-visual-os\tree\prisma_visual_os_tree_reorg_00za.py" --target-root "%REPO%" --out-dir "%OUT%" %*
exit /b %ERRORLEVEL%
