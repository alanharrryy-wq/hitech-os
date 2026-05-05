@echo off

rem PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D_START

set "PRISMA_11D_PY=%PYTHON_EXE%"

if not defined PRISMA_11D_PY set "PRISMA_11D_PY=%PYTHON%"

rem PRISMA_MAIN_README_CONTRACT_12E_START
if /I "%~1"=="readme-contract" (
  if defined PYTHON_EXE (
    "%PYTHON_EXE%" "%~dp0tools\prisma\verify_prisma_main_readme_contract_12e.py" --root "%~dp0." --text
    exit /b
  )
  if defined PYTHON (
    "%PYTHON%" "%~dp0tools\prisma\verify_prisma_main_readme_contract_12e.py" --root "%~dp0." --text
    exit /b
  )
  python "%~dp0tools\prisma\verify_prisma_main_readme_contract_12e.py" --root "%~dp0." --text
  exit /b
)
rem PRISMA_MAIN_README_CONTRACT_12E_END
if not defined PRISMA_11D_PY set "PRISMA_11D_PY=python"

if "%~1"=="license-server-signing-smoke" (

  shift

  if "%~1"=="--http" (

    shift

    "%PRISMA_11D_PY%" "%~dp0tooling\licensing\server11d\server_signing_scan_policy_11d.py" --root "%~dp0." --out "F:\descargasf" smoke --http %*

  ) else (

    "%PRISMA_11D_PY%" "%~dp0tooling\licensing\server11d\server_signing_scan_policy_11d.py" --root "%~dp0." --out "F:\descargasf" smoke %*

  )

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-scan" (

  "%PRISMA_11D_PY%" "%~dp0tooling\licensing\server11d\server_signing_scan_policy_11d.py" --root "%~dp0." --out "F:\descargasf" scan

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-fixture-audit" (

  "%PRISMA_11D_PY%" "%~dp0tooling\licensing\server11d\server_signing_scan_policy_11d.py" --root "%~dp0." --out "F:\descargasf" fixture-audit

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-material-smoke" (

  "%PRISMA_11D_PY%" "%~dp0tooling\licensing\server11d\server_signing_scan_policy_11d.py" --root "%~dp0." --out "F:\descargasf" material-smoke

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-sanitize" (

  "%PRISMA_11D_PY%" "%~dp0tooling\licensing\server11d\server_signing_scan_policy_11d.py" --root "%~dp0." --out "F:\descargasf" sanitize

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-sign-license" (

  "%PRISMA_11D_PY%" "%~dp0tooling\licensing\server11d\server_signing_scan_policy_11d.py" --root "%~dp0." --out "F:\descargasf" sign-license

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-hardening-contract" (

  "%PRISMA_11D_PY%" "%~dp0tooling\licensing\server11d\server_signing_scan_policy_11d.py" --root "%~dp0." --out "F:\descargasf" contract

  exit /b %ERRORLEVEL%

)

rem PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D_END

rem PRISMA_LICENSE_SERVER_SIGNING_HARDENING_11C_START

if "%~1"=="license-server-signing-smoke" (

  shift

  if "%~1"=="--http" (

    shift

    "%PYTHON_EXE%" "%~dp0tooling\licensing\server11c\server_signing_hardening_11c.py" --root "%~dp0." --out "F:\descargasf" smoke --http %*

  ) else (

    "%PYTHON_EXE%" "%~dp0tooling\licensing\server11c\server_signing_hardening_11c.py" --root "%~dp0." --out "F:\descargasf" smoke %*

  )

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-scan" (

  "%PYTHON_EXE%" "%~dp0tooling\licensing\server11c\server_signing_hardening_11c.py" --root "%~dp0." --out "F:\descargasf" scan

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-material-smoke" (

  "%PYTHON_EXE%" "%~dp0tooling\licensing\server11c\server_signing_hardening_11c.py" --root "%~dp0." --out "F:\descargasf" material-smoke

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-sanitize" (

  "%PYTHON_EXE%" "%~dp0tooling\licensing\server11c\server_signing_hardening_11c.py" --root "%~dp0." --out "F:\descargasf" sanitize

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-sign-license" (

  "%PYTHON_EXE%" "%~dp0tooling\licensing\server11c\server_signing_hardening_11c.py" --root "%~dp0." --out "F:\descargasf" sign-license

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-hardening-contract" (

  "%PYTHON_EXE%" "%~dp0tooling\licensing\server11c\server_signing_hardening_11c.py" --root "%~dp0." --out "F:\descargasf" contract

  exit /b %ERRORLEVEL%

)

rem PRISMA_LICENSE_SERVER_SIGNING_HARDENING_11C_END

rem PRISMA_LICENSE_SERVER_SIGNING_MATERIAL_COMPAT_11B_START

if "%~1"=="license-server-signing-material-migrate" (

  set "PRISMA_11B_PY=%PYTHON%"

  if not defined PRISMA_11B_PY set "PRISMA_11B_PY=python"

  "%PRISMA_11B_PY%" "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" material-migrate

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-material-smoke" (

  set "PRISMA_11B_PY=%PYTHON%"

  if not defined PRISMA_11B_PY set "PRISMA_11B_PY=python"

  "%PRISMA_11B_PY%" "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" material-smoke

  exit /b %ERRORLEVEL%

)

if "%~1"=="license-server-signing-compat-smoke" (

  set "PRISMA_11B_PY=%PYTHON%"

  if not defined PRISMA_11B_PY set "PRISMA_11B_PY=python"

  "%PRISMA_11B_PY%" "%~dp0tooling\licensing\server11b\material_compat_11b.py" --root "%~dp0." --out "F:\descargasf" smoke

  exit /b %ERRORLEVEL%

)

rem PRISMA_LICENSE_SERVER_SIGNING_MATERIAL_COMPAT_11B_END



REM >>> PRISMA_LICENSE_SERVER_SIGNING_11 COMMANDS >>>

if /I "%~1"=="license-server-signing-config" (

  python "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" config %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-signing-audit" (

  python "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" audit %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-signing-smoke" (

  python "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" smoke %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-sign-license" (

  python "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" sign-payload %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-signing-verify" (

  python "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" verify %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-signing-activate" (

  python "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" activate-and-sign %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-signing-refresh" (

  python "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" refresh-and-sign %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-signing-contract" (

  python "%~dp0tooling\licensing\server11\license_server_signing_11.py" --root "%~dp0." --out "F:\descargasf" contract %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

REM <<< PRISMA_LICENSE_SERVER_SIGNING_11 COMMANDS <<<





REM >>> PRISMA_LICENSE_PRIVATE_KEY_SMOKE_FIX_10F COMMANDS >>>

if /I "%~1"=="license-private-key-smoke" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" smoke

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-scan" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" scan

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-audit" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" audit

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-contract" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" contract

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-generate-dev" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" generate-dev-key %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

REM <<< PRISMA_LICENSE_PRIVATE_KEY_SMOKE_FIX_10F COMMANDS <<<





rem PRISMA_LICENSE_CMD_DISPATCH_REPAIR_10E_START

rem 10E early security dispatcher. Must stay before legacy goto unknown and before pnpm checks.

if /I "%~1"=="license-signature-policy" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" policy --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-registry" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" registry --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-audit" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" audit --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-verify-fixture" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" verify-fixture --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-env-smoke" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" env-smoke --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-smoke" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" smoke --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-contract" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" contract --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-scan" (

  python "%~dp0tooling\licensing\signature10c\license_signature_scanner_10c.py" scan --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-scan-smoke" (

  python "%~dp0tooling\licensing\signature10c\license_signature_scanner_10c.py" self-test --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-scan-rules" (

  python "%~dp0tooling\licensing\signature10c\license_signature_scanner_10c.py" rules --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-scan" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" scan

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-audit" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" audit

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-quarantine" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" quarantine

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-generate-dev" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" generate-dev-key

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-smoke" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" smoke

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-contract" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0." --out "F:\descargasf" contract

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-dispatch-analyze" (

  python "%~dp0tooling\licensing\dispatch10e\cmd_dispatch_repair_10e.py" analyze --root "%~dp0." --out "F:\descargasf"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-dispatch-smoke" (

  python "%~dp0tooling\licensing\dispatch10e\cmd_dispatch_repair_10e.py" smoke --runtime --root "%~dp0." --out "F:\descargasf"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-dispatch-contract" (

  python "%~dp0tooling\licensing\dispatch10e\cmd_dispatch_repair_10e.py" contract --root "%~dp0." --out "F:\descargasf"

  exit /b %ERRORLEVEL%

)

rem PRISMA_LICENSE_CMD_DISPATCH_REPAIR_10E_END



rem PRISMA_LICENSE_CANONICAL_OPERATIONS_04_START

if /I "%~1"=="license-full-check" (

  python "%~dp0tooling\licensing\prisma_license_canon_ops.py" --root "%~dp0." --full-check --ensure-running

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-diagnose" (

  python "%~dp0tooling\licensing\prisma_license_canon_ops.py" --root "%~dp0." --diagnose --ensure-running

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-plan-matrix" (

  python "%~dp0tooling\licensing\prisma_license_canon_ops.py" --root "%~dp0." --plan-matrix --ensure-running

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-set-demo" (

  python "%~dp0tooling\licensing\prisma_license_canon_ops.py" --root "%~dp0." --set-demo-license "%~2"

  exit /b %ERRORLEVEL%

)

rem PRISMA_LICENSE_CANONICAL_OPERATIONS_04_END

rem PRISMA_LICENSE_SYSTEM_PRO_ROADMAP_05_START

if /I "%~1"=="license-pro-readiness" (

  python "%~dp0tooling\licensing\pro05\license_pro_readiness.py" --root "%~dp0."

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-pro-contract" (

  type "%~dp0docs\productization\PRISMA_LICENSE_SYSTEM_PRO_ROADMAP_05.md"

  exit /b 0

)

rem PRISMA_LICENSE_SYSTEM_PRO_ROADMAP_05_END



rem PRISMA_LICENSE_SERVER_MVP_06_START

if /I "%~1"=="license-server-dev" (

  python "%~dp0tooling\licensing\server06\license_server_mvp.py" --root "%~dp0." serve %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-smoke" (

  python "%~dp0tooling\licensing\server06\license_server_mvp.py" --root "%~dp0." smoke %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-seed" (

  python "%~dp0tooling\licensing\server06\license_server_mvp.py" --root "%~dp0." seed %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-server-contract" (

  type "%~dp0docs\productization\PRISMA_LICENSE_SERVER_MVP_06.md"

  exit /b 0

)

rem PRISMA_LICENSE_SERVER_MVP_06_END

rem PRISMA_LICENSE_DEVICE_ACTIVATION_HARDENING_08_START

if /I "%~1"=="license-device-policy" (

  python "%~dp0tooling\licensing\device08\license_device_activation_08.py" --root "%~dp0." policy %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-device-matrix" (

  python "%~dp0tooling\licensing\device08\license_device_activation_08.py" --root "%~dp0." matrix %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-device-audit" (

  python "%~dp0tooling\licensing\device08\license_device_activation_08.py" --root "%~dp0." audit %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-device-reset" (

  python "%~dp0tooling\licensing\device08\license_device_activation_08.py" --root "%~dp0." reset %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-device-smoke" (

  python "%~dp0tooling\licensing\device08\license_device_activation_08.py" --root "%~dp0." smoke-offline %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-device-contract" (

  type "%~dp0docs\productization\PRISMA_LICENSE_DEVICE_ACTIVATION_HARDENING_08.md"

  exit /b 0

)

rem PRISMA_LICENSE_DEVICE_ACTIVATION_HARDENING_08_END

rem PRISMA_LICENSE_PRODUCTION_KEY_MANAGEMENT_09_START

if /I "%~1"=="license-key-policy" (

  python "%~dp0tooling\licensing\keys09\license_key_management_09.py" --root "%~dp0." policy %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-key-env-template" (

  python "%~dp0tooling\licensing\keys09\license_key_management_09.py" --root "%~dp0." env-template %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-key-registry" (

  python "%~dp0tooling\licensing\keys09\license_key_management_09.py" --root "%~dp0." registry %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-key-audit" (

  python "%~dp0tooling\licensing\keys09\license_key_management_09.py" --root "%~dp0." audit %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-key-rotation-plan" (

  python "%~dp0tooling\licensing\keys09\license_key_management_09.py" --root "%~dp0." rotation-plan %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-key-smoke" (

  python "%~dp0tooling\licensing\keys09\license_key_management_09.py" --root "%~dp0." smoke %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-key-contract" (

  type "%~dp0docs\productization\PRISMA_LICENSE_PRODUCTION_KEY_MANAGEMENT_09.md"

  exit /b 0

)

rem PRISMA_LICENSE_PRODUCTION_KEY_MANAGEMENT_09_END

setlocal



set "SELF_DIR=%~dp0"

for %%I in ("%SELF_DIR%.") do set "TV_SYSTEM_ROOT=%%~fI"



set "PC_APP=%TV_SYSTEM_ROOT%\products\pc\app"

set "TABLET_APP=%TV_SYSTEM_ROOT%\products\tablet\app"

set "MOBILE_APP=%TV_SYSTEM_ROOT%\products\mobile\app"

set "OUT_DIR=F:\descargasf"

set "TABLET_DB_FILE=%TABLET_APP%\data\tablet-pos.db"
set "TABLET_DB_URL=file:%TABLET_DB_FILE:\=/%"

set "PC_DB_FILE=%TV_SYSTEM_ROOT%\tools\_local\data\terminal-de-venta-system\canonical.db"
set "PC_DB_URL=file:%PC_DB_FILE:\=/%"

set "PRISMA_HIDE_UPDATE_MESSAGE=1"



where pnpm >nul 2>&1

if errorlevel 1 (

  echo [ERROR] pnpm is not available in PATH.

  echo         Install pnpm and try again.

  exit /b 1

)



if "%~1"=="" goto startall



if /I "%~1"=="help" goto help

if /I "%~1"=="dev" goto startall

if /I "%~1"=="start-all" goto startall

if /I "%~1"=="both-dev" goto startall

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

if /I "%~1"=="mobile-dev" goto mobiledev

if /I "%~1"=="mobile-typecheck" goto mobiletypecheck

if /I "%~1"=="mobile-build" goto mobilebuild

if /I "%~1"=="doctor" goto doctor

if /I "%~1"=="run-all-doctor" goto doctor

if /I "%~1"=="health" goto health

if /I "%~1"=="validate-all" goto validateall

if /I "%~1"=="validate-tablet" goto validatetablet

if /I "%~1"=="open" goto openapps

rem PRISMA_LICENSE_SIGNATURE_10B_DISPATCH_FIX_START

rem Must appear before REM >>> PRISMA_LICENSE_PRIVATE_KEY_QUARANTINE_10D COMMANDS >>>

if /I "%~1"=="license-private-key-scan" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0" scan

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-audit" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0" audit

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-quarantine" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0" quarantine %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-generate-dev" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0" generate-dev-key %2 %3 %4 %5 %6 %7 %8 %9

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-smoke" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0" smoke

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-private-key-contract" (

  python "%~dp0tooling\licensing\signature10d\private_key_quarantine_10d.py" --root "%~dp0" contract

  exit /b %ERRORLEVEL%

)

REM <<< PRISMA_LICENSE_PRIVATE_KEY_QUARANTINE_10D COMMANDS <<<





goto unknown

if /I "%~1"=="license-signature-policy" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10\license_signature_10.py" policy --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-registry" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10\license_signature_10.py" registry --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-audit" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10\license_signature_10.py" audit --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-verify-fixture" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10\license_signature_10.py" verify-fixture --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-env-smoke" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10\license_signature_10.py" env-smoke --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-smoke" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10\license_signature_10.py" smoke --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-contract" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10\license_signature_10.py" contract --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-dispatch-analyze" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\dispatch10b\license_dispatch_guard_10b.py" analyze --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-dispatch-smoke" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\dispatch10b\license_dispatch_guard_10b.py" smoke --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

rem PRISMA_LICENSE_SIGNATURE_10B_DISPATCH_FIX_END

rem PRISMA_LICENSE_SIGNATURE_10C_SCAN_COMMANDS_START

rem Robust private-key scanner 10C commands. Must appear before goto unknown.

if /I "%~1"=="license-signature-scan" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10c\license_signature_scanner_10c.py" scan --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-scan-smoke" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10c\license_signature_scanner_10c.py" self-test --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-scan-rules" (

  python "%TV_SYSTEM_ROOT%\tooling\licensing\signature10c\license_signature_scanner_10c.py" rules --root "%TV_SYSTEM_ROOT%"

  exit /b %ERRORLEVEL%

)

rem PRISMA_LICENSE_SIGNATURE_10C_SCAN_COMMANDS_END

goto unknown



:help

echo Terminal de Venta Launcher

echo.

echo Usage:

echo   terminal_de_venta.cmd

echo   terminal_de_venta.cmd dev

echo   terminal_de_venta.cmd start-all

echo   terminal_de_venta.cmd pc-dev

echo   terminal_de_venta.cmd tablet-dev [targetRoot]

echo   terminal_de_venta.cmd mobile-dev

echo   terminal_de_venta.cmd pc-typecheck

echo   terminal_de_venta.cmd tablet-typecheck [targetRoot]

echo   terminal_de_venta.cmd mobile-typecheck

echo   terminal_de_venta.cmd pc-build

echo   terminal_de_venta.cmd tablet-build [targetRoot]

echo   terminal_de_venta.cmd mobile-build

echo   terminal_de_venta.cmd tablet-db-init [targetRoot]

echo   terminal_de_venta.cmd tablet-db-generate [targetRoot]

echo   terminal_de_venta.cmd tablet-db-push [targetRoot]

echo   terminal_de_venta.cmd tablet-db-seed [targetRoot]

echo   terminal_de_venta.cmd validate-tablet [targetRoot]

echo   terminal_de_venta.cmd validate-all

echo   terminal_de_venta.cmd doctor

echo   terminal_de_venta.cmd health

echo   terminal_de_venta.cmd open

echo.

echo Dev URLs:

echo   Tablet:     http://127.0.0.1:3120/

echo   Tablet ref: http://127.0.0.1:3120/prisma-dark-pos-reference

echo   PC:         http://127.0.0.1:3130/

echo   Mobile:     http://127.0.0.1:3140/prisma-app

echo.

echo Prisma dev preflight:

echo   pc-dev and tablet-dev run Prisma generate/bridge before Next dev.

echo   Tablet DATABASE_URL: %TABLET_DB_URL%

echo   PC DATABASE_URL:     %PC_DB_URL%

echo   Logs: F:\descargasf\prisma_*_dev_preflight_last.log

echo.

echo Doctor:

echo   doctor runs F:\descargasf\prisma_run_all_apps_doctor_00D.py when available.

echo   It repairs, tests, starts all three apps, writes one TXT, and copies it to clipboard.

echo.

echo Notes:

echo   No arguments, dev, and start-all launch Tablet, PC, and Mobile dev apps.

echo   Tablet remains standalone and uses its local SQLite DB.

echo   PC is backoffice. Mobile is supervisor/PWA and does not use Prisma directly.

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



:requiremobile

if not exist "%MOBILE_APP%\package.json" (

  echo [ERROR] Mobile app not found:

  echo         %MOBILE_APP%

  exit /b 1

)

exit /b 0



:prismadevpreflight

set "PRISMA_PREFLIGHT_PRODUCT=%~1"

set "PRISMA_PREFLIGHT_SCRIPT=%TV_SYSTEM_ROOT%\tools\_local\repair_prisma_client_pnpm_bridge.ps1"

if /I "%PRISMA_PREFLIGHT_PRODUCT%"=="tablet" (

  set "DATABASE_URL=%TABLET_DB_URL%"

  set "TABLET_DATABASE_URL=%TABLET_DB_URL%"

  set "TABLET_RUNTIME_MODE=standalone"

)

if /I "%PRISMA_PREFLIGHT_PRODUCT%"=="pc" (

  set "DATABASE_URL=%PC_DB_URL%"

  set "PC_DATABASE_URL=%PC_DB_URL%"

)

set "PRISMA_HIDE_UPDATE_MESSAGE=1"

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%" >nul 2>&1

if not exist "%PRISMA_PREFLIGHT_SCRIPT%" (

  echo [ERROR] Prisma preflight script not found:

  echo         %PRISMA_PREFLIGHT_SCRIPT%

  echo [INFO] Run doctor once or restore tools\_local\repair_prisma_client_pnpm_bridge.ps1.

  pause

  exit /b 1

)

powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PRISMA_PREFLIGHT_SCRIPT%" -Root "%TV_SYSTEM_ROOT%" -Product "%PRISMA_PREFLIGHT_PRODUCT%"

set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (

  echo [ERROR] Prisma preflight failed for %PRISMA_PREFLIGHT_PRODUCT%.

  echo [INFO] Review log under F:\descargasf\prisma_%PRISMA_PREFLIGHT_PRODUCT%_dev_preflight_last.log

  pause

)

exit /b %RC%

:pcdev

call :requirepc || exit /b 1

set "TARGET=%PC_APP%"
set "DATABASE_URL=%PC_DB_URL%"
set "PC_DATABASE_URL=%PC_DB_URL%"
set "PRISMA_HIDE_UPDATE_MESSAGE=1"

call :prismadevpreflight pc || exit /b %ERRORLEVEL%

pnpm --dir "%PC_APP%" run dev

set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (

  echo [ERROR] PC dev server exited with code %RC%.

  echo [INFO] Log: F:\descargasf\prisma_pc_dev_preflight_last.log

  pause

)

exit /b %RC%



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

set "DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_RUNTIME_MODE=standalone"
set "PRISMA_HIDE_UPDATE_MESSAGE=1"

call :prismadevpreflight tablet || exit /b %ERRORLEVEL%

pnpm --dir "%TARGET%" run dev

set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (

  echo [ERROR] Tablet dev server exited with code %RC%.

  echo [INFO] Log: F:\descargasf\prisma_tablet_dev_preflight_last.log

  pause

)

exit /b %RC%



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

set "DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_RUNTIME_MODE=standalone"
set "PRISMA_HIDE_UPDATE_MESSAGE=1"

pnpm --dir "%TARGET%" run db:tablet:init

exit /b %ERRORLEVEL%



:tabletdbgenerate

call :requiretablet %1 %2 || exit /b 1

set "DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_RUNTIME_MODE=standalone"
set "PRISMA_HIDE_UPDATE_MESSAGE=1"

pnpm --dir "%TARGET%" run db:tablet:generate

exit /b %ERRORLEVEL%



:tabletdbpush

call :requiretablet %1 %2 || exit /b 1

set "DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_RUNTIME_MODE=standalone"
set "PRISMA_HIDE_UPDATE_MESSAGE=1"

pnpm --dir "%TARGET%" run db:tablet:push

exit /b %ERRORLEVEL%



:tabletdbseed

call :requiretablet %1 %2 || exit /b 1

set "DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_DATABASE_URL=%TABLET_DB_URL%"
set "TABLET_RUNTIME_MODE=standalone"
set "PRISMA_HIDE_UPDATE_MESSAGE=1"

pnpm --dir "%TARGET%" run db:tablet:seed

exit /b %ERRORLEVEL%



:validatetablet

call :requiretablet %1 %2 || exit /b 1

pnpm --dir "%TARGET%" run check:all

exit /b %ERRORLEVEL%



:mobiledev

call :requiremobile || exit /b 1

pnpm --dir "%MOBILE_APP%" run dev

set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (

  echo [ERROR] Mobile dev server exited with code %RC%.

  pause

)

exit /b %RC%



:mobiletypecheck

call :requiremobile || exit /b 1

pnpm --dir "%MOBILE_APP%" run typecheck

exit /b %ERRORLEVEL%



:mobilebuild

call :requiremobile || exit /b 1

pnpm --dir "%MOBILE_APP%" run build

exit /b %ERRORLEVEL%



:doctor

set "PRISMA_DOCTOR=F:\descargasf\prisma_run_all_apps_doctor_00D.py"

if not exist "%PRISMA_DOCTOR%" (

  echo [ERROR] Doctor script not found:

  echo         %PRISMA_DOCTOR%

  echo [INFO] Download prisma_run_all_apps_doctor_00D.py into F:\descargasf or run app commands manually.

  pause

  exit /b 1

)

python "%PRISMA_DOCTOR%" --root "%TV_SYSTEM_ROOT%" --out "%OUT_DIR%" --timeout 120

exit /b %ERRORLEVEL%



:health

powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "function T($n,$u){try{$r=Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 8; Write-Host ('OK '+$n+' '+$r.StatusCode+' '+$u) -ForegroundColor Green}catch{Write-Host ('FAIL '+$n+' '+$u+' :: '+$_.Exception.Message) -ForegroundColor Red}}; T 'Tablet' 'http://127.0.0.1:3120/'; T 'TabletRef' 'http://127.0.0.1:3120/prisma-dark-pos-reference'; T 'PC' 'http://127.0.0.1:3130/'; T 'Mobile' 'http://127.0.0.1:3140/prisma-app'"

exit /b %ERRORLEVEL%



:validateall

call "%~f0" pc-typecheck || exit /b 1

call "%~f0" tablet-typecheck || exit /b 1

call "%~f0" validate-tablet || exit /b 1

call "%~f0" mobile-typecheck || exit /b 1

exit /b 0



:openapps

start "" "http://127.0.0.1:3120/"

start "" "http://127.0.0.1:3130/"

start "" "http://127.0.0.1:3140/prisma-app"

exit /b 0



:startall

call :requirepc || exit /b 1

call :requiretablet tablet-dev "%TABLET_APP%" || exit /b 1

call :requiremobile || exit /b 1

echo [INFO] Starting Tablet app: http://127.0.0.1:3120/

echo [INFO] Starting PC app:     http://127.0.0.1:3130/

echo [INFO] Starting Mobile app: http://127.0.0.1:3140/prisma-app

echo [INFO] Three terminal windows will stay open for the dev servers.

start "PRISMA Tablet (3120)" cmd /k ""%~f0" tablet-dev"

start "PRISMA PC (3130)" cmd /k ""%~f0" pc-dev"

start "PRISMA Mobile (3140)" cmd /k ""%~f0" mobile-dev"

exit /b 0



:: BEGIN PRISMA_LICENSE_PRODUCTION_SIGNATURE_10

if /I "%~1"=="license-signature-policy" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" policy --root "%~dp0"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-registry" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" registry --root "%~dp0"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-audit" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" audit --root "%~dp0"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-verify-fixture" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" verify-fixture --root "%~dp0"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-env-smoke" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" env-smoke --root "%~dp0"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-smoke" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" smoke --root "%~dp0"

  exit /b %ERRORLEVEL%

)

if /I "%~1"=="license-signature-contract" (

  python "%~dp0tooling\licensing\signature10\license_signature_10.py" contract --root "%~dp0"

  exit /b %ERRORLEVEL%

)

:: END PRISMA_LICENSE_PRODUCTION_SIGNATURE_10

