@echo off
REM Synapse-X GUI Launcher
REM Ejecutar desde línea de comandos o con doble clic
cd /d "%~dp0"
echo Iniciando Synapse-X GUI...
py -3 synapse-x_starter.py --root "%~dp0"
pause