@echo off
setlocal
py "%~dp0tree\prisma_visual_os_tree_reorg_close_00ze.py" --target-root "%~dp0..\..\..\.." --out-dir "F:\descargasf" --verify
exit /b %ERRORLEVEL%
