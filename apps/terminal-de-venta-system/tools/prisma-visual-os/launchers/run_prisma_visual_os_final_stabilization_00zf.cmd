@echo off
setlocal
py "%~dp0..\tree\prisma_visual_os_final_stabilization_00zf.py" --target-root "%~dp0..\..\.." --out-dir "F:\descargasf" --verify
exit /b %ERRORLEVEL%
