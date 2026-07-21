
@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo No se encontro Python en PATH.
  echo Ejecuta manualmente: py -3 tools\servidor_local.py
  pause
  exit /b 1
)
python tools\servidor_local.py
