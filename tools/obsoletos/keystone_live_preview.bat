@echo off
setlocal EnableExtensions DisableDelayedExpansion

rem ============================================================
rem Keystone Live Preview Launcher
rem ============================================================

set "STUDIO_URL=http://localhost:3000"

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"

set "LOG_DIR=%REPO_ROOT%\tools\logs\keystone_live_preview"

for /f %%I in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyyMMdd_HHmmss\")"') do set "TIMESTAMP=%%I"
if not defined TIMESTAMP set "TIMESTAMP=00000000_000000"
set "LOG_FILE=%LOG_DIR%\%TIMESTAMP%_keystone_live_preview.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

call :Header
call :Progress 0 "Starting Keystone live preview bootstrap."
call :Log "Script path: %~f0"
call :Log "Script dir: %SCRIPT_DIR%"
call :Log "Repo root: %REPO_ROOT%"
call :Log "Studio URL: %STUDIO_URL%"

call :Progress 20 "Running preflight checks."
call :CheckNode
if errorlevel 1 exit /b 1
call :CheckPnpm
if errorlevel 1 exit /b 1
call :Progress 40 "Preflight checks passed."

set "INSTALL_NEEDED=1"
if exist "%REPO_ROOT%\node_modules\.pnpm\lock.yaml" set "INSTALL_NEEDED=0"
if exist "%REPO_ROOT%\node_modules" set "INSTALL_NEEDED=0"

if "%INSTALL_NEEDED%"=="1" (
  call :Log "Dependency heuristic: node_modules/.pnpm/lock.yaml and node_modules are missing."
  call :Progress 60 "Installing dependencies with pnpm."
  call :RunAndLog pnpm -C "%REPO_ROOT%" install
  if errorlevel 1 (
    call :Error "Dependency install failed. See log: %LOG_FILE%"
    exit /b 2
  )
) else (
  call :Log "Dependency heuristic: existing node_modules detected; install skipped."
  call :Progress 60 "Dependencies already present. Skipping install."
)

set "STUDIO_WINDOW_TITLE=keystone:scene:studio"

call :Progress 80 "Launching Keystone Scene Studio in a new terminal (or reusing existing one)."
echo [WARN] Duplicate detection is disabled for reliability on this machine.
echo [WARN] If Studio is already running, close extra Studio terminals manually.
call :Log "Duplicate detection skipped to avoid tasklist hangs."
call :Log "Executing: start %STUDIO_WINDOW_TITLE% cmd /k call pnpm -C %REPO_ROOT% keystone:scene:studio"
start "%STUDIO_WINDOW_TITLE%" cmd /k "call pnpm -C ""%REPO_ROOT%"" keystone:scene:studio"
if errorlevel 1 (
  call :Error "Failed to launch Keystone Scene Studio."
  exit /b 3
)

echo Waiting 3 seconds before opening browser...
call :Log "Waiting 3 seconds before browser open."
timeout /t 3 /nobreak >nul

call :ResolveStudioUrl
call :Log "Opening browser URL: %OPEN_URL%"
start "" "%OPEN_URL%"

echo If the page didn't load, check the studio terminal output.
call :Log "Browser open requested for %OPEN_URL%."
call :Progress 100 "Done. Live preview should now be running."
call :Log "Launcher completed successfully."
echo Log file: %LOG_FILE%
exit /b 0

:Header
echo ============================================================
echo Keystone Scene Studio Live Preview Launcher
echo Date: %DATE%  Time: %TIME%
echo ============================================================
exit /b 0

:Progress
echo [%~1%%] %~2
call :Log "[%~1%%] %~2"
exit /b 0

:CheckNode
node -v >nul 2>&1
if errorlevel 1 (
  call :Error "Node.js is not installed or not on PATH. Install Node.js and retry."
  exit /b 1
)
set "NODE_VERSION="
for /f "usebackq delims=" %%V in (`node -v 2^>^&1`) do if not defined NODE_VERSION set "NODE_VERSION=%%V"
if not defined NODE_VERSION set "NODE_VERSION=(unknown)"
call :Log "Node detected: %NODE_VERSION%"
echo Node: %NODE_VERSION%
exit /b 0

:CheckPnpm
pushd "%REPO_ROOT%" >nul 2>&1
if errorlevel 1 (
  call :Error "Could not access repo root for pnpm check: %REPO_ROOT%"
  exit /b 1
)
call pnpm -v >nul 2>&1
if errorlevel 1 (
  popd >nul 2>&1
  call :Error "pnpm is not installed or not on PATH. Install pnpm and retry."
  exit /b 1
)
set "PNPM_VERSION="
for /f "usebackq delims=" %%V in (`call pnpm -v 2^>^&1`) do if not defined PNPM_VERSION set "PNPM_VERSION=%%V"
popd >nul 2>&1
if not defined PNPM_VERSION set "PNPM_VERSION=(unknown)"
call :Log "pnpm detected: %PNPM_VERSION%"
echo pnpm: %PNPM_VERSION%
exit /b 0

:ResolveStudioUrl
set "OPEN_URL="
for /f "usebackq delims=" %%U in (`powershell -NoProfile -Command "$default=$env:STUDIO_URL; $c=@($default,'http://127.0.0.1:3101/dev/scene-studio?debug=1','http://localhost:3101/dev/scene-studio?debug=1','http://127.0.0.1:3100/dev/scene-studio?debug=1','http://localhost:3100/dev/scene-studio?debug=1','http://127.0.0.1:3000/dev/scene-studio?debug=1','http://localhost:3000/dev/scene-studio?debug=1'); $list=New-Object System.Collections.Generic.List[string]; foreach($u in $c){ if([string]::IsNullOrWhiteSpace($u)){ continue }; if(-not $list.Contains($u)){ [void]$list.Add($u) } }; for($i=0;$i -lt 8;$i++){ foreach($u in $list){ try { $r=Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -ge 200 -and $r.StatusCode -lt 400){ Write-Output $u; exit 0 } } catch { $code=$null; try { $code=[int]$_.Exception.Response.StatusCode.value__ } catch { }; if($code -ge 200 -and $code -lt 400){ Write-Output $u; exit 0 } } }; Start-Sleep -Milliseconds 600 }; foreach($p in @(3101,3100,3000)){ try { $client=New-Object System.Net.Sockets.TcpClient; $iar=$client.BeginConnect('127.0.0.1',$p,$null,$null); if($iar.AsyncWaitHandle.WaitOne(300) -and $client.Connected){ $client.EndConnect($iar); $client.Close(); Write-Output ('http://127.0.0.1:' + $p + '/dev/scene-studio?debug=1'); exit 0 }; $client.Close() } catch { } }; Write-Output $default"` ) do if not defined OPEN_URL set "OPEN_URL=%%U"
if not defined OPEN_URL set "OPEN_URL=%STUDIO_URL%"
call :Log "Resolved studio URL: %OPEN_URL%"
exit /b 0

:RunAndLog
set "RUN_CMD=%*"
echo [CMD] %RUN_CMD%
call :Log "CMD: %RUN_CMD%"
cmd /d /c "%RUN_CMD%" >>"%LOG_FILE%" 2>&1
set "RUN_RC=%ERRORLEVEL%"
if not "%RUN_RC%"=="0" (
  call :Log "Command failed with exit code %RUN_RC%."
  exit /b %RUN_RC%
)
call :Log "Command finished successfully."
exit /b 0

:Log
>>"%LOG_FILE%" echo [%DATE% %TIME%] %~1
exit /b 0

:Error
echo [ERROR] %~1
call :Log "ERROR: %~1"
exit /b 1
