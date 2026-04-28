@echo off
setlocal

set "SELF_DIR=%~dp0"
for %%I in ("%SELF_DIR%.") do set "TV_SYSTEM_ROOT=%%~fI"

set "PC_APP=%TV_SYSTEM_ROOT%\products\pc\app"
set "TABLET_APP=%TV_SYSTEM_ROOT%\products\tablet\app"

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
if /I "%~1"=="tablet-db-init" goto tabletdbinit
if /I "%~1"=="tablet-db-generate" goto tabletdbgenerate
if /I "%~1"=="tablet-db-push" goto tabletdbpush
if /I "%~1"=="tablet-db-seed" goto tabletdbseed
if /I "%~1"=="validate-all" goto validateall
if /I "%~1"=="validate-tablet" goto validatetablet
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
echo   terminal_de_venta.cmd tablet-db-init [targetRoot]
echo   terminal_de_venta.cmd tablet-db-generate [targetRoot]
echo   terminal_de_venta.cmd tablet-db-push [targetRoot]
echo   terminal_de_venta.cmd tablet-db-seed [targetRoot]
echo   terminal_de_venta.cmd validate-tablet [targetRoot]
echo   terminal_de_venta.cmd validate-all
echo   terminal_de_venta.cmd open
echo.
echo Notes:
echo   Tablet commands validate only the Tablet app root.
echo   PC is not required for tablet-dev, tablet-build, tablet-typecheck, or tablet-db-*.
exit /b 0

:unknown
echo [ERROR] Unknown command: %~1
echo.
echo Use:
echo   terminal_de_venta.cmd help
exit /b 1

:requirepc
if not exist "%PC_APP%\package.json" (
  echo [ERROR] PC app not found:
  echo         %PC_APP%
  exit /b 1
)
exit /b 0

:requiretablet
set "TARGET=%~2"
if "%TARGET%"=="" set "TARGET=%TABLET_APP%"
if not exist "%TARGET%\package.json" (
  echo [ERROR] targetRoot does not look like a Tablet app root:
  echo         %TARGET%
  exit /b 1
)
exit /b 0

:pcdev
call :requirepc || exit /b 1
pnpm --dir "%PC_APP%" run dev
exit /b %ERRORLEVEL%

:pctypecheck
call :requirepc || exit /b 1
pnpm --dir "%PC_APP%" run typecheck
exit /b %ERRORLEVEL%

:pcbuild
call :requirepc || exit /b 1
pnpm --dir "%PC_APP%" run build
exit /b %ERRORLEVEL%

:tabletdev
call :requiretablet %1 %2 || exit /b 1
pnpm --dir "%TARGET%" run dev
exit /b %ERRORLEVEL%

:tablettypecheck
call :requiretablet %1 %2 || exit /b 1
pnpm --dir "%TARGET%" run typecheck
exit /b %ERRORLEVEL%

:tabletbuild
call :requiretablet %1 %2 || exit /b 1
pnpm --dir "%TARGET%" run build
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [WARN] First tablet build attempt failed. Retrying once...
  pnpm --dir "%TARGET%" run build
  set "RC=%ERRORLEVEL%"
)
exit /b %RC%

:tabletdbinit
call :requiretablet %1 %2 || exit /b 1
pnpm --dir "%TARGET%" run db:tablet:init
exit /b %ERRORLEVEL%

:tabletdbgenerate
call :requiretablet %1 %2 || exit /b 1
pnpm --dir "%TARGET%" run db:tablet:generate
exit /b %ERRORLEVEL%

:tabletdbpush
call :requiretablet %1 %2 || exit /b 1
pnpm --dir "%TARGET%" run db:tablet:push
exit /b %ERRORLEVEL%

:tabletdbseed
call :requiretablet %1 %2 || exit /b 1
pnpm --dir "%TARGET%" run db:tablet:seed
exit /b %ERRORLEVEL%

:validatetablet
call :requiretablet %1 %2 || exit /b 1
pnpm --dir "%TARGET%" run check:all
exit /b %ERRORLEVEL%

:validateall
call "%~f0" pc-typecheck || exit /b 1
call "%~f0" pc-build || exit /b 1
call "%~f0" validate-tablet || exit /b 1
call "%~f0" tablet-build || exit /b 1
exit /b 0

:openapps
start "" "http://localhost:3130"
start "" "http://localhost:3120"
exit /b 0
