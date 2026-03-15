@echo off
setlocal
set REPO_ROOT=%~1
if "%REPO_ROOT%"=="" set REPO_ROOT=F:\repos\hitech-os
python "%REPO_ROOT%\tools\live-scene-composer\control_tower.py" --repo-root "%REPO_ROOT%" full
