@echo off
setlocal EnableExtensions

rem ================================================================
rem PRISMA Chart Lab - levantar local y abrir Cloudflare Pages
rem Estado actualizado:
rem   Produccion Cloudflare: https://prisma-chart-lab.pages.dev
rem   Cloudflare Pages root: HTTP 200 OK
rem   Project: prisma-chart-lab
rem   Account ID: f9fafe5309089fc108bd94e292a8202f
rem
rem Uso normal:
rem   doble click o ejecutar este .cmd
rem
rem Opciones:
rem   04_LEVANTAR_LOCAL_LUEGO_CLOUDFLARE.cmd deploy   -> build + deploy produccion sin --branch
rem   04_LEVANTAR_LOCAL_LUEGO_CLOUDFLARE.cmd check    -> solo verifica local/cloudflare
rem ================================================================

set "REPO_ROOT=F:\repos\hitech-os"
set "TERMINAL_ROOT=F:\repos\hitech-os\apps\terminal-de-venta-system"
set "CHART_LAB_ROOT=F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app"
set "LOCAL_URL=http://127.0.0.1:3000"
set "CLOUDFLARE_URL=https://prisma-chart-lab.pages.dev"
set "CLOUDFLARE_ACCOUNT_ID=f9fafe5309089fc108bd94e292a8202f"
set "PAGES_PROJECT=prisma-chart-lab"

if /I "%~1"=="deploy" goto DEPLOY
if /I "%~1"=="check" goto CHECK
if /I "%~1"=="cloudflare" goto OPEN_CLOUDFLARE
if /I "%~1"=="local" goto START_LOCAL

echo.
echo === PRISMA Chart Lab: local + Cloudflare ===
echo Local:      %LOCAL_URL%
echo Cloudflare: %CLOUDFLARE_URL%
echo.

if not exist "%TERMINAL_ROOT%\package.json" (
  echo [ERROR] No existe %TERMINAL_ROOT%\package.json
  pause
  exit /b 1
)

if not exist "%CHART_LAB_ROOT%\package.json" (
  echo [ERROR] No existe %CHART_LAB_ROOT%\package.json
  pause
  exit /b 1
)

goto START_LOCAL

:START_LOCAL
echo.
echo === Levantando Chart Lab local en una ventana nueva ===
start "PRISMA Chart Lab Local 3000" powershell.exe -NoLogo -NoExit -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Set-Location -LiteralPath '%TERMINAL_ROOT%'; pnpm chart-lab:dev"

echo Esperando que arranque http://127.0.0.1:3000 ...
timeout /t 8 /nobreak >nul

goto CHECK

:CHECK
echo.
echo === Smoke local y Cloudflare ===
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "^$ErrorActionPreference='Continue'; function Test-Head([string]^$url){ try { ^$r=Invoke-WebRequest -Uri ^$url -Method Head -UseBasicParsing -TimeoutSec 8; Write-Host ('OK ' + ^$r.StatusCode + ' ' + ^$url) -ForegroundColor Green; return ^$true } catch { Write-Host ('WARN ' + ^$url + ' -> ' + ^$_.Exception.Message) -ForegroundColor Yellow; return ^$false } }; ^$local=Test-Head '%LOCAL_URL%'; ^$cf=Test-Head '%CLOUDFLARE_URL%'; if (-not ^$cf) { exit 2 }"
set "RC=%ERRORLEVEL%"

if "%RC%"=="2" (
  echo [WARN] Cloudflare no respondio 200. Revisa red/cache o ejecuta deploy.
) else (
  echo [OK] Cloudflare production esta vivo.
)

echo.
echo Abriendo URLs...
start "" "%LOCAL_URL%"
start "" "%CLOUDFLARE_URL%"
exit /b 0

:OPEN_CLOUDFLARE
echo Abriendo Cloudflare production: %CLOUDFLARE_URL%
start "" "%CLOUDFLARE_URL%"
exit /b 0

:DEPLOY
echo.
echo === Build + deploy Cloudflare Pages PRODUCCION ===
echo OJO: deploy de produccion va SIN --branch.
echo Project: %PAGES_PROJECT%
echo URL final: %CLOUDFLARE_URL%
echo.

if not exist "%CHART_LAB_ROOT%\out" (
  echo [INFO] No existe out. Se ejecutara build.
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $env:CLOUDFLARE_ACCOUNT_ID='%CLOUDFLARE_ACCOUNT_ID%'; Push-Location '%TERMINAL_ROOT%'; pnpm chart-lab:verify; pnpm chart-lab:typecheck; pnpm chart-lab:build; Pop-Location; Push-Location '%CHART_LAB_ROOT%'; pnpm exec wrangler pages deploy '.\out' --project-name '%PAGES_PROJECT%' --commit-dirty=true; Pop-Location; Start-Sleep -Seconds 8; $r=Invoke-WebRequest -Uri '%CLOUDFLARE_URL%' -Method Head -UseBasicParsing -TimeoutSec 15; Write-Host ('Cloudflare production: ' + $r.StatusCode + ' %CLOUDFLARE_URL%') -ForegroundColor Green"
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo [ERROR] Deploy fallo. Si Wrangler pide login, ejecuta: pnpm exec wrangler login
  pause
  exit /b %RC%
)

echo.
echo [OK] Deploy production completo.
start "" "%CLOUDFLARE_URL%"
exit /b 0
