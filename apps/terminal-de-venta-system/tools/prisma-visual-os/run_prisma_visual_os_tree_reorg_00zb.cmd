@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
py -3 "%SCRIPT_DIR%tree\prisma_visual_os_tree_reorg_00zb.py" %*
exit /b %ERRORLEVEL%
