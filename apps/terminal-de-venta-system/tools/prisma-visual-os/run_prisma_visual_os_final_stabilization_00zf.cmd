@echo off
setlocal
py "%~dp0tree\prisma_visual_os_final_stabilization_00zf.py" --target-root "%~dp0..\.." --out-dir "F:\descargasf" --verify
exit /b %ERRORLEVEL%
