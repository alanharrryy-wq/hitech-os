@echo off
setlocal
cd /d "%~dp0"
where code >nul 2>nul
if errorlevel 1 (
  echo No se encontro el comando code en PATH.
  echo Abre manualmente PRISMA-HTML.code-workspace con Visual Studio Code.
  pause
  exit /b 1
)
code "%~dp0PRISMA-HTML.code-workspace"
