@echo off
setlocal

set REPO_ROOT=%1
if "%REPO_ROOT%"=="" set REPO_ROOT=.

set DOCS_ROOT=%2
if "%DOCS_ROOT%"=="" set DOCS_ROOT=docs\live-scene-composer

python "%REPO_ROOT%\tools\live-scene-composer\validate_docs_architecture_guard.py" --repo-root "%REPO_ROOT%" --docs-root "%DOCS_ROOT%" --write-report

endlocal
