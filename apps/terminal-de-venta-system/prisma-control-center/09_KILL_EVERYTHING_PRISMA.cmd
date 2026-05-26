@echo off
setlocal
REM PRISMA_CONTEXTUAL_FIXPACK_20260525_01
REM Detiene procesos y puertos PRISMA
REM Puertos cubiertos: 3000 3100 3110 3120 3130 3140 3150 3200
set "PRISMA_CC_ROOT=%~dp0"
set "PRISMA_WRAPPER=%PRISMA_CC_ROOT%internal\wrappers\kill_everything.ps1"
if not exist "%PRISMA_WRAPPER%" (
  echo Falta wrapper oficial: %PRISMA_WRAPPER%
  exit /b 2
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%PRISMA_WRAPPER%" %*
exit /b %ERRORLEVEL%
