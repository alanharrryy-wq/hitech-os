@echo off
setlocal EnableExtensions

set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"

echo.
echo [HITECH-OS] One-click startup
echo Repo: %REPO_ROOT%
echo.

where pnpm >nul 2>&1
if errorlevel 1 (
  echo [ERROR] pnpm is not installed or not in PATH.
  echo Install pnpm 9.x and try again.
  exit /b 1
)

set "PYTHON_CMD=python"
where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Install Python 3.11+ and try again.
    exit /b 1
  )
  set "PYTHON_CMD=py -3.11"
)

if not exist "%REPO_ROOT%node_modules" (
  echo [1/6] Installing dependencies...
  call pnpm install --frozen-lockfile
  if errorlevel 1 (
    echo [ERROR] pnpm install failed.
    exit /b 1
  )
) else (
  echo [1/6] Dependencies already present (node_modules found).
)

echo [2/6] Starting @hitech/contracts (watch build)...
start "HITECH Contracts Watch" cmd /k "cd /d \"%REPO_ROOT%\" && pnpm --filter @hitech/contracts dev"

echo [3/6] Starting @hitech/ui-kit (watch build)...
start "HITECH UI-Kit Watch" cmd /k "cd /d \"%REPO_ROOT%\" && pnpm --filter @hitech/ui-kit dev"

echo [4/6] Starting core-api on http://127.0.0.1:3001 ...
start "HITECH Core API" cmd /k "cd /d \"%REPO_ROOT%\" && pnpm --filter @hitech/core-api dev"

echo [5/6] Starting ai-agent on http://127.0.0.1:8001 ...
start "HITECH AI Agent" cmd /k "cd /d \"%REPO_ROOT%\\services\\ai-agent\" && %PYTHON_CMD% -m app.main --host 127.0.0.1 --port 8001"

echo [6/6] Starting keystone on http://127.0.0.1:3100 ...
start "HITECH Keystone" cmd /k "cd /d \"%REPO_ROOT%\" && pnpm --filter @hitech/keystone dev"

echo.
echo Startup commands launched.
echo Keystone Pitch URL: http://127.0.0.1:3100/pitch
echo.
echo Optional check:
echo   pnpm --filter @hitech/keystone test -- tests/pitch-routes.test.tsx tests/layer-data-attributes.test.tsx
echo.

exit /b 0
