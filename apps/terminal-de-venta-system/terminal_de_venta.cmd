@echo off
setlocal

set "SELF_DIR=%~dp0"
for %%I in ("%SELF_DIR%.") do set "TV_SYSTEM_ROOT=%%~fI"

set "PC_APP=%TV_SYSTEM_ROOT%\products\pc\app"
set "TABLET_APP=%TV_SYSTEM_ROOT%\products\tablet\app"

if not exist "%PC_APP%\package.json" (
  echo [ERROR] PC app not found:
  echo         %PC_APP%
  exit /b 1
)

if not exist "%TABLET_APP%\package.json" (
  echo [ERROR] Tablet app not found:
  echo         %TABLET_APP%
  exit /b 1
)

where pnpm >nul 2>&1
if errorlevel 1 (
  echo [ERROR] pnpm is not available in PATH.
  echo         Install pnpm and try again.
  exit /b 1
)

if "%~1"=="" goto help

if /I "%~1"=="help" goto help
if /I "%~1"=="pc-dev" goto pcdev
if /I "%~1"=="pc-build" goto pcbuild
if /I "%~1"=="pc-typecheck" goto pctypecheck
if /I "%~1"=="tablet-dev" goto tabletdev
if /I "%~1"=="tablet-build" goto tabletbuild
if /I "%~1"=="tablet-typecheck" goto tablettypecheck
if /I "%~1"=="validate-all" goto validateall
if /I "%~1"=="open" goto openapps
goto unknown

:help
echo Terminal de Venta Launcher
echo.
echo Usage:
echo   terminal_de_venta.cmd pc-dev
echo   terminal_de_venta.cmd pc-typecheck
echo   terminal_de_venta.cmd pc-build
echo   terminal_de_venta.cmd tablet-dev [targetRoot]
echo   terminal_de_venta.cmd tablet-typecheck [targetRoot]
echo   terminal_de_venta.cmd tablet-build [targetRoot]
echo   terminal_de_venta.cmd validate-all
echo   terminal_de_venta.cmd open
exit /b 0

:unknown
echo [ERROR] Unknown command: %~1
echo.
echo Use:
echo   terminal_de_venta.cmd help
exit /b 1

:pcdev
pnpm --dir "%PC_APP%" run dev
exit /b %ERRORLEVEL%

:tabletdev
set "TARGET=%~2"
if "%TARGET%"=="" set "TARGET=%TABLET_APP%"
if not exist "%TARGET%\package.json" (
  echo [ERROR] targetRoot does not look like an app root:
  echo         %TARGET%
  exit /b 1
)
pnpm --dir "%TARGET%" run dev
exit /b %ERRORLEVEL%

:pctypecheck
pnpm --dir "%PC_APP%" run typecheck
exit /b %ERRORLEVEL%

:pcbuild
pnpm --dir "%PC_APP%" run build
exit /b %ERRORLEVEL%

:tablettypecheck
set "TARGET=%~2"
if "%TARGET%"=="" set "TARGET=%TABLET_APP%"
if not exist "%TARGET%\package.json" (
  echo [ERROR] targetRoot does not look like an app root:
  echo         %TARGET%
  exit /b 1
)
pnpm --dir "%TARGET%" run typecheck
exit /b %ERRORLEVEL%

:tabletbuild
set "TARGET=%~2"
if "%TARGET%"=="" set "TARGET=%TABLET_APP%"
if not exist "%TARGET%\package.json" (
  echo [ERROR] targetRoot does not look like an app root:
  echo         %TARGET%
  exit /b 1
)
pnpm --dir "%TARGET%" run build
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [WARN] First tablet build attempt failed. Retrying once...
  pnpm --dir "%TARGET%" run build
  set "RC=%ERRORLEVEL%"
)
exit /b %RC%

:validateall
call "%~f0" pc-typecheck || exit /b 1
call "%~f0" pc-build || exit /b 1
call "%~f0" tablet-typecheck || exit /b 1
call "%~f0" tablet-build || exit /b 1
exit /b 0

:openapps
start "" "http://localhost:3130"
start "" "http://localhost:3120"
exit /b 0
