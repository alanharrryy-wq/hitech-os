@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"

set "PYTHON_EXE=python"
set "PYTHON_ARGS="
where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Python not found on PATH. Install Python 3.11+.
    exit /b 1
  )
  set "PYTHON_EXE=py"
  set "PYTHON_ARGS=-3"
)

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "RUN_TAG=%%I"
set "LOG_DIR=%REPO_ROOT%\tools\ui_map\_logs\%RUN_TAG%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set "SUMMARY_LOG=%LOG_DIR%\runner-summary.log"
echo RUN_TAG=%RUN_TAG%>"%SUMMARY_LOG%"
echo REPO=%REPO_ROOT%>>"%SUMMARY_LOG%"
echo CLI_MODULE=tools.ui_map._all_py_onebutton.cli>>"%SUMMARY_LOG%"

echo [INFO] Repo root: %REPO_ROOT%
echo [INFO] Run tag: %RUN_TAG%
echo [INFO] Running one-button UI map pipeline...
pushd "%REPO_ROOT%"

set /a IDX=0
for %%S in (doctor generate validate queries) do (
  set /a IDX+=1
  if !IDX! LSS 10 (set "STEP_NO=0!IDX!") else set "STEP_NO=!IDX!"
  set "STEP_NAME=%%S"
  set "STEP_LOG=%LOG_DIR%\!STEP_NO!_!STEP_NAME!.log"

  echo STEP=!STEP_NAME!>>"%SUMMARY_LOG%"
  echo CMD=%PYTHON_EXE% %PYTHON_ARGS% -m tools.ui_map._all_py_onebutton.cli !STEP_NAME! --repo %REPO_ROOT% --out docs/ui-map --run-tag %RUN_TAG%>>"%SUMMARY_LOG%"

  %PYTHON_EXE% %PYTHON_ARGS% -m tools.ui_map._all_py_onebutton.cli !STEP_NAME! --repo "%REPO_ROOT%" --out "docs/ui-map" --run-tag "%RUN_TAG%" > "!STEP_LOG!" 2>&1
  set "EXIT_CODE=!ERRORLEVEL!"
  echo EXIT_CODE=!EXIT_CODE!>>"%SUMMARY_LOG%"
  echo EXIT_CODE=!EXIT_CODE!>>"!STEP_LOG!"

  if not "!EXIT_CODE!"=="0" (
    popd
    echo [ERROR] Step !STEP_NAME! failed with exit code !EXIT_CODE!.
    echo [ERROR] See log: !STEP_LOG!
    exit /b !EXIT_CODE!
  )
)
popd

echo [OK] UI map one-button completed.
echo [OK] Logs: %LOG_DIR%
exit /b 0
