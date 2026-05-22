# PRISMA License Runtime Operator Flow

Flujo simple para dejar Tablet con runtime, identidad, licencia local y sync a PC funcionando.

Regla base: Tablet vende sola aunque PC no exista. Cuando PC existe, Tablet le manda eventos por red local y PC conserva ledger, conflictos y evidencia.

## Resultado esperado

Al terminar, `GET http://127.0.0.1:3120/api/license/status` debe reportar:

- `state`: `active`
- `plan`: `TABLET_PRO` o el plan real comprado
- `assignmentState`: `assigned`
- `denialReason`: `null`
- `warnings`: vacio
- `operationalDecision`: `allow`
- `canUseLocalPos`: `true`
- `deniedFeatures`: `0` cuando la licencia cubre las funciones esperadas

## 1. Respaldar config actual

```powershell
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$dest = "F:\descargasf\PRISMA_ProgramData_Config_backup_$stamp.zip"
Compress-Archive -LiteralPath 'C:\ProgramData\PRISMA\Commerce\Config' -DestinationPath $dest -Force
$dest
```

Si la carpeta no existe, sigue al paso 2.

## 2. Tener lista la licencia firmada

Para cliente real usa el `license.json` firmado del cliente.

Para prueba local controlada en este repo se puede usar:

```powershell
F:\repos\hitech-os\apps\terminal-de-venta-system\tooling\licensing\fixtures\tablet-pro.active.signed.license.json
```

No uses licencia de prueba como licencia productiva final. Sirve para validar runtime, UI, verifiers y continuidad local.

## 3. Provisionar Tablet local

Desde el repo:

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system

node tools/provision-prisma-runtime.mjs `
  --apply `
  --runtime-mode customer `
  --vertical commerce `
  --role tablet `
  --client-id cust_demo `
  --business-id biz_demo `
  --store-id matriz-001 `
  --terminal-id tablet-terminal-001 `
  --device-id tablet-001 `
  --package-type TABLET_PC_MANAGED `
  --pc-origin http://127.0.0.1:3130 `
  --license-file tooling/licensing/fixtures/tablet-pro.active.signed.license.json
```

Para otro cliente cambia `client-id`, `business-id`, `store-id`, `terminal-id`, `device-id` y `--license-file`.

Si de verdad sera Tablet sin PC, cambia `--package-type TABLET_SOLO` y no pongas `--pc-origin`.

## 4. Validar

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system verify:runtime-config
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system verify:tablet-provisioning
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system verify:tablet-solo-smoke
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system verify:no-direct-db-in-ui
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system verify:tablet-license-page-layout
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system verify:license-ops-console
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system verify:code-atlas-boundaries
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app typecheck
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app build
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\quality quality:self-test
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\quality quality:customer-smoke
```

Todos deben salir `PASS` o `OK`.

## 5. Confirmar estado vivo

Levanta primero PC y luego Tablet:

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system
.\terminal_de_venta.cmd pc-dev
.\terminal_de_venta.cmd tablet-dev
```

Si ya estan levantados por Codex o por otra terminal, no abras otros dos. Solo valida.

Con Tablet corriendo en `127.0.0.1:3120` y PC en `127.0.0.1:3130`:

```powershell
$r = Invoke-WebRequest -Uri 'http://127.0.0.1:3120/api/license/status' -UseBasicParsing -TimeoutSec 10
$json = $r.Content | ConvertFrom-Json
[pscustomobject]@{
  ok = $json.ok
  state = $json.data.status.state
  plan = $json.data.status.plan
  source = $json.data.status.source
  path = $json.data.status.path
  assignment = $json.data.status.assignmentState
  denialReason = $json.data.status.denialReason
  warnings = ($json.data.status.warnings | ConvertTo-Json -Compress)
  operationalDecision = $json.data.operationalDecision
  canUseLocalPos = $json.data.canUseLocalPos
  deniedFeatures = (@($json.data.decisions | Where-Object { -not $_.allowed }).Count)
} | ConvertTo-Json -Depth 5
```

Salida buena:

```json
{
  "ok": true,
  "state": "active",
  "plan": "TABLET_PRO",
  "source": "local_file",
  "path": "C:\\ProgramData\\PRISMA\\Commerce\\Config\\license.json",
  "assignment": "assigned",
  "denialReason": null,
  "warnings": null,
  "operationalDecision": "allow",
  "canUseLocalPos": true,
  "deniedFeatures": 0
}
```

Sync bueno:

```powershell
Invoke-WebRequest -Uri 'http://127.0.0.1:3120/api/pos/sync/health/pc' -UseBasicParsing
Invoke-WebRequest -Uri 'http://127.0.0.1:3120/api/pos/sync/dispatch' -Method POST -Body '{"force":true}' -ContentType 'application/json' -UseBasicParsing
```

Salida buena de health:

```json
{
  "ok": true,
  "enabled": true,
  "status": "online",
  "url": "http://127.0.0.1:3130/api/sync/ingest"
}
```

Salida buena de dispatch cuando ya no hay pendientes:

```json
{
  "ok": true,
  "reason": "empty",
  "dispatched": 0
}
```

Salida buena de dispatch cuando habia pendientes:

```json
{
  "ok": true,
  "reason": "dispatched",
  "dispatched": 25
}
```

## 6. Si algo falla

- `license_missing`: falta `C:\ProgramData\PRISMA\Commerce\Config\license.json`.
- `wrong_business`: la licencia no coincide con `businessId`.
- `wrong_store`: la licencia no coincide con `storeId`.
- `wrong_device`: la licencia no coincide con `deviceId`.
- `wrong_terminal`: la licencia no coincide con `terminalId`.
- `LICENSE_SIGNATURE_INVALID`: el archivo fue alterado o no fue firmado por una llave reconocida.
- `customer mode apunta al repo`: provisiona otra vez con `runtimeRoot` en `C:\ProgramData\PRISMA\Commerce`.
- `pc_sync_disabled`: runtime no esta en `TABLET_PC_MANAGED` o `sync.enabled` esta en `false`.
- `pc_unavailable`: PC no esta levantada en `127.0.0.1:3130` o `pcOrigin` apunta a otro lugar.
- `conflict/product_discontinued`: PC recibio el evento, pero su catalogo no tiene ese producto.
- `conflict/sale_outside_shift`: PC recibio el evento, pero su caja/turno canonico no coincide.
- `recognized_not_projected`: PC recibio y guardo ledger, pero ese topic todavia no proyecta tabla final. No es red apagada.

No edites la UI para esconder estos estados. Se corrige runtime, identidad o licencia.

## 7. Compilar sin pelear Windows

Estos comandos ya usan un HOME temporal local para que Next no escanee carpetas protegidas de `C:\Users`:

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app build
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app build
```

## 8. Regla de oro

Tablet debe poder vender localmente aunque PC, Mobile, internet o cloud no existan. PC gobierna si esta presente. Mobile supervisa. Shared/Core registra, valida contratos y conserva evidencia. Control audita.
