@echo off
setlocal

set REPO_ROOT=%1
if "%REPO_ROOT%"=="" set REPO_ROOT=.

set OUTPUT_DIR=%2
if "%OUTPUT_DIR%"=="" set OUTPUT_DIR=docs\live-scene-composer\architecture-artifacts

python "%REPO_ROOT%\tools\live-scene-composer\generate_architecture_artifacts.py" --repo-root "%REPO_ROOT%" --output-dir "%OUTPUT_DIR%"

endlocal
