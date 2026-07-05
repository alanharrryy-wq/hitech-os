---
title: PRISMA Field Manual de Aprendizaje Operativo
path: docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md
status: LIVING
owner: PRISMA Ops / Engineering
created: 2026-06-10
last_updated: 2026-06-10
version: 00A
scope:
  - hot-injection
  - rollback
  - test-gates
  - scripts
  - visual-patches
  - packaging
  - Windows/Prisma gotchas
  - evidence-ledger
principle: "Aprender una vez; no volver a pagar la misma multa operacional."
---

# PRISMA Field Manual de Aprendizaje Operativo

Este archivo es la libreta de campo viva para registrar lo que ya aprendimos operando PRISMA: qué comandos funcionan, cuáles explotan, cómo inyectar cambios sin apagar procesos, cómo hacer rollback, qué pruebas sí validan lo que creemos y qué trampas vuelven con bigote falso.

No reemplaza contratos, runbooks oficiales ni governance docs. Los complementa con memoria práctica, reproducible y accionable. Es el cuaderno de taquería del sistema: si algo ya nos quemó la mano, aquí queda escrito para no volver a agarrar el comal con fe ciega.

## 0. Ubicación propuesta

```text
apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md
```

Si `docs/ops` no existe, se crea. Este manual debe vivir dentro del repo para que viaje con el código, no en una carpeta de descargas como náufrago con USB.

## 1. Autoridades que este manual respeta

Este manual nace debajo de estas reglas de gobierno ya existentes:

| Autoridad | Regla práctica que aporta |
|---|---|
| `docs/PRISMA_OPERATIONAL_SAFETY_RULES.md` | Cambios riesgosos requieren backup, evidencia, rollback y cuidado con secretos. |
| `docs/design/PRISMA_TRI_SURFACE_VISUAL_CHANGE_CONTRACT_00A.md` | Cambio visual debe declarar PC, Tablet y Mobile: tocar, validar o excluir con razón. |
| `docs/design/PRISMA_TRI_SURFACE_VISUAL_GUARDIAN_00B.md` | Tablet vende sola; PC y Mobile no son padres de Tablet. No inventar jerarquías. |
| `docs/design/PRISMA_VISUAL_CHANGE_MANIFEST_TEMPLATE_00C.json` | Todo cambio visual oficial debe tener manifest de cobertura y evidencia. |
| `quality/contracts/no-fake-green.contract.json` | No cantar verde sin evidencia. Verde de palabra no vale, carajo. |
| `quality/contracts/traceable-operation.contract.json` | Cada resultado debe rastrearse de acción a evidencia. |
| `quality/contracts/release-evidence-required.contract.json` | Nada listo para release sin evidencia empaquetable. |
| `prisma-control-center/internal/py/prismo_learning/**` | Ya existe memoria/aprendizaje en tooling; este manual es la capa humana, operativa y legible. |

## 2. Reglas de oro

1. Todo cambio aplicado por script debe tener backup detectable antes de correr pruebas.
2. Todo comando debe registrar: contexto, precondiciones, comando exacto, resultado, evidencia y rollback.
3. No mezclar hot-injection con comandos que regeneren Prisma si hay servidores vivos.
4. Un smoke funcional `PASS` no significa que el cambio visual sea perceptible.
5. Si el cambio visual toca varias superficies, debe tener manifest visual o quedarse como experimento/hotfix.
6. Ningún aprendizaje se considera cerrado sin síntoma, causa real y comando corregido.
7. No tocar `shared-ui`, `globals`, PC, Tablet y Mobile juntos sin matriz de impacto. Eso ya no es parche, es operativo federal.
8. No subir `.env`, DBs vivas, tokens, zips con secretos o evidencia sensible a canales externos.
9. Tablet POS se protege como superficie autónoma de venta. No introducir dependencia de PC o Mobile para vender.
10. Todo rollback debe restaurar el repo y dejar log de qué backup usó.

## 3. Taxonomía de entradas

| Tipo | Cuándo usarlo |
|---|---|
| `COMMAND_WORKS` | Comando confirmado como útil en cierto contexto. |
| `COMMAND_FAILS` | Comando que falló y debe evitarse o condicionarse. |
| `HOT_INJECTION_RECIPE` | Procedimiento para parchear sin apagar dev server. |
| `ROLLBACK_RECIPE` | Procedimiento de reversa probado. |
| `GOTCHA` | Trampa técnica no obvia. |
| `VISUAL_LEARNING` | Hallazgo de UI/CSS/Visual OS. |
| `PACKAGING_LEARNING` | Hallazgo sobre TodoALV, ZIPs, tamaños, scripts. |
| `GOVERNANCE_LEARNING` | Qué exige gobierno para que un parche sea oficial. |
| `EVIDENCE_LEARNING` | Qué prueba qué cosa y qué no prueba. |
| `WINDOWS_PRISMA_LOCK` | Casos de archivos bloqueados por Windows/Prisma/Next. |

## 4. Plantilla para registrar aprendizaje

```md
### YYYY-MM-DD HH:mm - <titulo corto>

**Tipo:** COMMAND_WORKS | COMMAND_FAILS | HOT_INJECTION_RECIPE | ROLLBACK_RECIPE | GOTCHA | VISUAL_LEARNING | PACKAGING_LEARNING | GOVERNANCE_LEARNING | EVIDENCE_LEARNING | WINDOWS_PRISMA_LOCK
**Superficie:** Tablet | PC | Mobile | Chart Lab | Shared UI | Tooling | Packaging
**Contexto:** <qué estaba vivo, qué se quería lograr, qué ruta/pantalla>
**Precondiciones:** <servidor vivo, zip en ruta, repo path, rama, etc.>
**Comando exacto:**

```powershell
# pegar comando exacto aquí
```

**Resultado observado:** PASS | FAIL | PARTIAL
**Evidencia:** <ruta de reporte, diff, smoke, captura, log>
**Causa real:** <qué aprendimos>
**Rollback probado:** Sí | No | N/A
**Regla nueva:** <frase imperativa para futuro>
**Notas:** <detalles, límites, deuda pendiente>
```

## 5. Primeras entradas confirmadas

### 2026-06-10 03:28 - `pc:typecheck` no es seguro en hot-injection con dev servers vivos

**Tipo:** COMMAND_FAILS / GOTCHA / WINDOWS_PRISMA_LOCK
**Superficie:** PC / Tablet / Tooling
**Contexto:** Se aplicó payload visual con Tablet `next dev` vivo. Luego se intentó correr `pc:typecheck`.
**Síntoma:** Prisma falló al intentar borrar DLL generado.

```text
EPERM: operation not permitted, unlink 'F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\.generated\prisma-client\query_engine-windows.dll.node'
```

**Causa real:** Windows mantenía bloqueado `query_engine-windows.dll.node` porque algún proceso `node`, `next dev`, watcher, VS Code/TS Server o Prisma runtime seguía vivo.
**Rollback probado:** Sí. El script restauró desde `_prisma_delayer_02_backups\20260610_035112`.
**Regla nueva:** En hot-injection no correr gates que ejecuten `prisma generate`. Usar pruebas focalizadas que no regeneren cliente Prisma.

**Comando a evitar en caliente:**

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" pc:typecheck
```

**Comando permitido en caliente si no toca Prisma:**

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" verify:tablet-solo-smoke
```

---

### 2026-06-10 10:00 - Hot-injection con rollback automático sí funciona para parches focalizados

**Tipo:** HOT_INJECTION_RECIPE / ROLLBACK_RECIPE / COMMAND_WORKS
**Superficie:** Tablet / Tooling
**Contexto:** Usuario no quería apagar `next dev`; se aplicó payload desde ZIP en `F:\descargasf`.
**Resultado observado:** PASS. `verify:tablet-solo-smoke` pasó con 7 checks verdes.
**Evidencia:** `F:\descargasf\PRISMA_TABLET_SOLO_SMOKE_20260610_100037.md` y `.json`.
**Rollback probado:** Sí, en pruebas anteriores el rollback restauró el repo al fallar smoke o Prisma lock.
**Regla nueva:** Hot-injection debe ser focalizada, con backup, prueba compatible y rollback automático.

**Receta base reutilizable:**

```powershell
$ErrorActionPreference = "Stop"

$Zip  = "F:\descargasf\PRISMA_DELAYER_XX_payload.zip"
$Repo = "F:\repos\hitech-os\apps\terminal-de-venta-system"
$Work = Join-Path $env:TEMP ("PRISMA_DELAYER_XX_HOT_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
$BackupRoot = Join-Path $Repo "_prisma_delayer_XX_backups"
$Backup = $null

function Restore-Backup {
    param([string]$BackupPath)

    if (-not $BackupPath -or -not (Test-Path $BackupPath)) {
        Write-Host "NO HAY BACKUP PARA ROLLBACK." -ForegroundColor Red
        exit 2
    }

    Write-Host "ROLLBACK EN CALIENTE desde: $BackupPath" -ForegroundColor Yellow
    robocopy $BackupPath $Repo /E /NFL /NDL /NJH /NJS /NC /NS | Out-Host

    if ($LASTEXITCODE -ge 8) {
        Write-Host "ROLLBACK FALLÓ." -ForegroundColor Red
        exit 3
    }

    Write-Host "ROLLBACK OK." -ForegroundColor Green
    exit 1
}

try {
    if (-not (Test-Path $Zip)) { throw "No encontré ZIP: $Zip" }
    if (-not (Test-Path $Repo)) { throw "No encontré repo: $Repo" }

    New-Item -ItemType Directory -Force -Path $Work | Out-Null
    Expand-Archive -LiteralPath $Zip -DestinationPath $Work -Force

    $Apply = Get-ChildItem -Path $Work -Filter "APLICAR_PRISMA_DELAYER_XX.ps1" -Recurse | Select-Object -First 1
    if (-not $Apply) { throw "No encontré aplicador dentro del ZIP." }

    powershell -NoProfile -ExecutionPolicy Bypass -File $Apply.FullName -RepoRoot $Repo

    $Backup = Get-ChildItem $BackupRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $Backup) { throw "No encontré backup para rollback." }

    Start-Sleep -Seconds 8

    pnpm -C $Repo verify:tablet-solo-smoke
    if ($LASTEXITCODE -ne 0) { throw "Falló verify:tablet-solo-smoke" }

    Write-Host "HOT INJECTION OK." -ForegroundColor Green
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($Backup) { Restore-Backup -BackupPath $Backup.FullName }
    $LatestBackup = $null
    if (Test-Path $BackupRoot) {
        $LatestBackup = Get-ChildItem $BackupRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    }
    if ($LatestBackup) { Restore-Backup -BackupPath $LatestBackup.FullName }
    exit 2
}
finally {
    if (Test-Path $Work) { Remove-Item $Work -Recurse -Force -ErrorAction SilentlyContinue }
}
```

---

### 2026-06-10 09:28 - Smoke funcional FAIL encontró copy faltante de licencia y provenance

**Tipo:** EVIDENCE_LEARNING / COMMAND_FAILS
**Superficie:** Tablet / License UI
**Contexto:** DELAYER 01 aplicó CSS, pero `verify:tablet-solo-smoke` falló.
**Resultado observado:** FAIL.
**Checks fallidos:**

```text
missing license customer mode has pending install copy
UI shows runtime provenance
```

**Causa real:** El smoke no estaba reclamando CSS. Estaba reclamando textos/estado visible de licencia: instalación pendiente y provenance runtime.
**Regla nueva:** Leer el reporte antes de culpar al parche visual. Un smoke puede fallar por copy/UI funcional aunque el cambio CSS sea inocente.

---

### 2026-06-10 10:00 - Smoke funcional PASS no prueba percepción visual

**Tipo:** VISUAL_LEARNING / GOTCHA / EVIDENCE_LEARNING
**Superficie:** Tablet
**Contexto:** `verify:tablet-solo-smoke` pasó después de corregir licencia/provenance, pero el usuario no vio cambio visual.
**Resultado observado:** PASS funcional, PARTIAL visual.
**Causa real:** El smoke valida contrato funcional/licencia, no densidad visual, cantidad de capas, blur, halos ni percepción de saturación.
**Regla nueva:** Para cambios visuales, además de smoke funcional, exigir evidencia visual:

- captura antes/después;
- diff del CSS correcto;
- ruta exacta afectada;
- selector real de la pantalla;
- `Ctrl+Shift+R` o incógnito si Next/Turbopack dejó cache vieja;
- opcional: checker que cuente `backdrop-filter`, `box-shadow`, `radial-gradient`, `::before`, `::after`.

---

### 2026-06-10 10:16 - `/catalog` no era `pos.module.css`

**Tipo:** VISUAL_LEARNING / GOTCHA
**Superficie:** Tablet `/catalog`
**Contexto:** Se redujeron capas en POS, pero la pantalla observada era “Catálogo que sí vende”.
**Resultado observado:** No hubo cambio perceptible en la captura de `/catalog`.
**Causa real:** La pantalla visible usaba `catalog-stock-selling-assist.module.css`, no el módulo principal de POS.
**Regla nueva:** Antes de tocar CSS, identificar ruta, componente real y módulo CSS que renderiza la pantalla. No asumir por nombre parecido.

**Archivos relevantes para esa pantalla:**

```text
products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css
products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css
```

**Comando de diff recomendado:**

```powershell
$Repo = "F:\repos\hitech-os\apps\terminal-de-venta-system"
git -C $Repo diff -- products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css
git -C $Repo diff -- products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css
```

---

### 2026-06-10 10:28 - DELAYER 01/02 sirvieron como experimento, no como parche gobernado final

**Tipo:** GOVERNANCE_LEARNING / VISUAL_LEARNING
**Superficie:** Tablet / PC / Mobile / Chart Lab / Shared UI
**Contexto:** El diff mostró demasiadas superficies tocadas para un objetivo visual específico.
**Resultado observado:** 28 archivos cambiados, 823 inserciones, 76 eliminaciones.
**Causa real:** El cambio fue amplio, con CSS overrides y `CSS priority override`; útil para probar dirección, pero no suficiente para gobernanza final.
**Regla nueva:** Si se toca más de una superficie, el cambio debe traer manifest visual y matriz de cobertura.

**Matriz mínima exigida:**

```text
Tablet: TOUCHED + evidencia
PC: TOUCHED o EXCLUDED con razón
Mobile: TOUCHED o EXCLUDED con razón
Shared UI: TOUCHED solo con validación tri-superficie
Chart Lab: TOUCHED o EXCLUDED con razón
```

**Estado recomendado:** Convertir experimento a parche gobernado focalizado, empezando por Tablet `/catalog` solamente.

---

### 2026-06-10 10:06 - TodoALV de 80 MB depende del BAT, no solo del default del motor

**Tipo:** PACKAGING_LEARNING / GOTCHA
**Superficie:** Packaging / Tooling
**Contexto:** El motor había sido modificado a 80 MB, pero seguían saliendo ZIPs de aproximadamente 500 MB.
**Resultado observado:** `TodoALV 001.zip` apareció con `511,968 KB`.
**Causa real:** El `.bat` pasaba `--max-part-kb 512000`, forzando el tamaño viejo.
**Regla nueva:** Cuando un default no se refleja, revisar wrappers `.bat`, `.ps1`, accesos directos y variables de entorno.

**Valor correcto:**

```bat
--max-part-kb 81920
```

**Comando para forzar 80 MB sin depender del default:**

```powershell
python F:\PRISMA_CTX\MOTORES\TodoALV.py --max-part-kb 81920
```

---

### 2026-06-10 10:06 - TodoALV usa 18 workers solo para inventario, no para escribir ZIPs

**Tipo:** PACKAGING_LEARNING / COMMAND_WORKS
**Superficie:** Packaging / Tooling
**Contexto:** Se preguntó si el motor opera con 18 workers en paralelo.
**Causa real:** `ProcessPoolExecutor(max_workers=workers)` paraleliza clasificación, secretos, hash y estimación de compresión. La escritura final de ZIPs queda secuencial.
**Regla nueva:** No asumir que `--workers 18` hace todo paralelo. Acelera inventario y estimación, no la fase final de escritura.

**Dónde conviene mejorar:**

```text
- reserva más conservadora para no pasarse de 80 MB;
- opción futura --zip-workers 2 para SSD/NVMe;
- modo rápido opcional para estimación sin doble compresión.
```

---

### 2026-06-10 10:16 - Next/Turbopack puede mostrar 404 que no son del parche visual

**Tipo:** GOTCHA / VISUAL_LEARNING
**Superficie:** Tablet dev server
**Contexto:** En `next dev` aparecieron 404 para packshots y una URL literal interpolada.
**Síntomas:**

```text
/products/packshots/light/cola_bottle_512.png 404
/products/packshots/dark/gomitas-enchiladas-pack-2.png 404
/$%7BgetPrismaRealtimeBaseUrl()%7D/state 404
```

**Causa probable:** Packshots faltantes y una interpolación que llegó literal como `${getPrismaRealtimeBaseUrl()}/state`, posiblemente por comillas incorrectas en lugar de template string.
**Regla nueva:** Separar ruido de dev server de fallos del parche. No resolver 404 de assets dentro de un delayer visual si no es el objetivo.

---

## 6. Comandos canonizados

### 6.1 Ver tablet solo smoke

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" verify:tablet-solo-smoke
```

### 6.2 Ver diff de archivos específicos

```powershell
$Repo = "F:\repos\hitech-os\apps\terminal-de-venta-system"
git -C $Repo diff --stat
git -C $Repo diff -- products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css
git -C $Repo diff -- products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css
```

### 6.3 Forzar TodoALV a 80 MB sin depender del default

```powershell
python F:\PRISMA_CTX\MOTORES\TodoALV.py --max-part-kb 81920
```

### 6.4 Validación fría completa, solo cuando no haya dev servers vivos

```powershell
$Repo = "F:\repos\hitech-os\apps\terminal-de-venta-system"
pnpm -C $Repo pc:typecheck
pnpm -C $Repo mobile:typecheck
pnpm -C $Repo verify:tablet-solo-smoke
pnpm -C $Repo chart-lab:verify
```

### 6.5 Buscar procesos que puedan bloquear Prisma, solo si se acepta cerrar procesos

```powershell
$Repo = "F:\repos\hitech-os\apps\terminal-de-venta-system"

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -and (
      $_.CommandLine -like "*terminal-de-venta-system*" -or
      $_.CommandLine -like "*products\pc\app*" -or
      $_.CommandLine -like "*products\tablet\app*" -or
      $_.CommandLine -like "*next dev*" -or
      $_.CommandLine -like "*prisma-client*" -or
      $_.CommandLine -like "*query_engine-windows.dll.node*"
    )
  } |
  Select-Object ProcessId, Name, CommandLine
```

No matar estos procesos si el objetivo es hot-injection sin apagar. Este comando primero es diagnóstico. Si se decide cerrar procesos, convertir a `Stop-Process` con aprobación explícita.

## 7. Known good / known bad

| Comando o acción | Estado | Condición |
|---|---:|---|
| `verify:tablet-solo-smoke` durante hot-injection | GOOD | Si no regenera Prisma. |
| `pc:typecheck` con `next dev` vivo | BAD | Puede ejecutar Prisma generate y fallar con EPERM. |
| Aplicar ZIP con script + backup + smoke | GOOD | Si el aplicador copia archivos focalizados y crea backup antes. |
| Cambiar `DEFAULT_MAX_PART_KB` sin revisar `.bat` | PARTIAL | El wrapper puede sobreescribir el default. |
| Smoke funcional como prueba visual | BAD | No mide percepción, layers ni saturación. |
| Tocar PC, Tablet, Mobile, Chart Lab y Shared UI en un delayer pequeño | BAD para repo final | Requiere manifest y validación tri-superficie. |
| CSS con `CSS priority override` masivo | TOLERABLE solo como experimento | No debe ser forma final si existen tokens/perillas Visual OS. |

## 8. Criterio para promover un aprendizaje a regla oficial

Un aprendizaje puede volverse regla si tiene:

- comando exacto;
- al menos un resultado PASS o FAIL reproducible;
- causa real identificada;
- evidencia local;
- rollback o mitigación;
- alcance declarado;
- fecha y contexto;
- dueño o superficie responsable.

## 9. Criterio para promover un hotfix visual a parche gobernado

Un hotfix visual puede entrar al repo final si trae:

1. objetivo visual específico;
2. superficie canónica declarada;
3. archivos tocados mínimos;
4. PC, Tablet y Mobile declarados como `TOUCHED`, `VALIDATED` o `EXCLUDED` con razón;
5. evidencia visual antes/después;
6. smoke funcional relevante;
7. diff limpio;
8. rollback probado;
9. manifest visual compatible con `PRISMA_VISUAL_CHANGE_MANIFEST_TEMPLATE_00C.json`;
10. explicación de por qué no rompe Tablet standalone.

## 10. Pendientes

- Crear checker visual que cuente `backdrop-filter`, `box-shadow`, `radial-gradient`, `linear-gradient`, `filter`, `::before`, `::after` por pantalla.
- Crear manifest estándar para parches visuales focalizados.
- Crear `apply-hot-payload.ps1` reusable para no pegar scripts gigantes cada vez.
- Separar smoke funcional de smoke visual.
- Documentar qué tests ejecutan `prisma generate` y cuáles son seguros en caliente.
- Crear mapa “ruta visible -> componente -> CSS module” para Tablet POS.
- Crear comando que agregue una entrada a este manual desde un JSON pequeño.

## 11. Formato ultra-rápido para añadir una línea nueva

```md
### YYYY-MM-DD HH:mm - <título>

**Tipo:** <tipo>
**Superficie:** <superficie>
**Contexto:** <situación>
**Comando exacto:** `<comando>`
**Resultado observado:** PASS | FAIL | PARTIAL
**Evidencia:** <ruta>
**Causa real:** <causa>
**Rollback probado:** Sí | No | N/A
**Regla nueva:** <regla>
```

## 12. Changelog

| Fecha | Cambio |
|---|---|
| 2026-07-03 | Aprendizaje LICFLOW4 Admin Bridge: token solo backend, confirmaciones obligatorias, dry-run primero y commit sin Mobile/PC/Tablet ni generated evidence. |
| 2026-06-18 | Cierre operativo POS /pos: governance limpio con govclean2, posctx limpio, AutoMesh PASS, Layer Map obligatorio y ruta app-root del manual corregida. |
| 2026-06-10 | Creación del manual vivo con primeras entradas de TodoALV, hot-injection, Prisma EPERM, smoke funcional, delayer visual y gobernanza tri-superficie. |

### 2026-06-18 00:45 - POS `/pos` preflight cerrado y AutoMesh path corregido

**Tipo:** GOVERNANCE_LEARNING / COMMAND_WORKS / GOTCHA / VISUAL_LEARNING
**Superficie:** Tablet POS `/pos` / Tooling / Governance
**Contexto:** Antes del primer patch visual premium de PRISMA Tablet POS `/pos`, se bloqueó correctamente el cambio porque `.governance/current` estaba sucio. Se diagnosticó y limpió governance, se volvió a correr contexto POS y se generó Authority Mesh task-scoped con Layers Map.
**Precondiciones:** Repo `F:\repos\hitech-os`, app `apps/terminal-de-venta-system`, sin matar procesos vivos, sin puertos, sin dev server start, sin Prisma generate caliente.
**Comando exacto:**

```powershell
& "F:\PRISMA_CTX\MOTORES\run_automesh.ps1" -Task "PRISMA Tablet POS /pos primer patch visual premium claro: mejorar layout, header busqueda, category rail, product grid, ticket side panel, action dock y quitar bloque legacy Reembolso Guardar Cancelar Venta si pertenece al owner canonical; no tocar PC Mobile Chart Lab Shared UI; no important; no overrides sucios" -Surface tablet -Repo "F:\repos\hitech-os" -Workers 18 -Shards 54 -MaxFiles 120 -MaxMB 40
```

**Resultado observado:** PASS para preflight. `govclean2 up1 1806 0013 result.zip` dejó governance limpio; `posctx 1806 0014 result.zip` confirmó contexto fresco limpio; `automesh mesh1 1806 0025 result.zip` generó Mesh con 18 workers, 54 sharders, scope Tablet, 120 selected files y 120 Layer entries.
**Evidencia:** `F:\descargasf\govclean2 up1 1806 0013 result.zip`; `F:\descargasf\posctx 1806 0014 result.zip`; `F:\descargasf\automesh mesh1 1806 0025 result.zip`; `F:\descargasf\opsclose1 1806 0037 fail.zip`.
**Causa real:** El bloqueo de governance no debía taparse con otro Mesh. Primero se corrigió el dirty state. Después, AutoMesh mostró un warning falso porque buscaba el manual operativo en `docs/ops/...` desde la raíz del repo, pero el manual vivo está en `apps/terminal-de-venta-system/docs/ops/...`. `opsclose1` falló por bug del empaquetador Python: `newline="\\n"` literal, no por contenido ni por Git; el rollback se ejecutó.
**Rollback probado:** Sí para `govclean2`; `opsclose1` reportó `rollback_executed: true`.
**Regla nueva:** Para visual/premium de `/pos`, el orden es: governance limpio, `posctx.py` fresco, Authority Mesh exacto con `LAYERS_MAP.md/json`, manual operativo consultado desde app-root, y sólo después patch. AutoMesh debe reconocer el manual tanto en raíz como en app-root. No usar smoke funcional como green visual.
**Notas:** No tocar PC, Mobile, Chart Lab ni Shared UI salvo que matrices Authority Mesh lo autoricen explícitamente. No usar `!important`, priority override tokens ni hacks globales.

### 2026-07-03 12:31 - LICFLOW3 POST 404 era worker vivo stale y config local desalineada

**Tipo:** GOTCHA / EVIDENCE_LEARNING / COMMAND_WORKS
**Superficie:** Cloudflare LICFLOW3 / Tooling / 3160
**Contexto:** `https://app.hitechrts.com` tenia `/health` y `/api/public/capabilities` en `200`, pero `POST /api/licenses/activate`, `/refresh` y `/revoke` devolvian `404`.
**Precondiciones:** Repo `F:\repos\hitech-os`, app `apps/terminal-de-venta-system`, sin deploy, sin DNS/Tunnel, sin secrets, sin D1 copy/export, sin levantar servidores.
**Comando exacto:**

```powershell
$ErrorActionPreference='Stop'
Set-Location 'F:\repos\hitech-os\apps\terminal-de-venta-system'
python tools/prisma-governance/authority_mesh.py --task "Corregir LICFLOW3 Cloudflare licensing routes para que POST /api/licenses/activate, /refresh y /revoke funcionen contra app.hitechrts.com sin downgrades, sin duplicar LICFLOW2, sin tocar secretos, sin copiar DB, sin deploy automatico no autorizado y preservando Worker real prisma-cloud-semilla y D1 real prisma_cloud_semilla." --output .governance/current
pnpm run verify:licflow3:route-activate
pnpm run verify:licflow3:route-refresh
pnpm run verify:licflow3:route-revoke
```

**Resultado observado:** PARTIAL. Local route contract PASS con `401 ADMIN_TOKEN_REQUIRED` para dummy sin token; live target seguia en `404` porque no hubo deploy autorizado.
**Evidencia:** `.governance/current/LICFLOW3_ROUTE_MAP.md`, `.governance/current/LICFLOW3_OWNERSHIP_MAP.md`, `F:\descargasf\licflow3-evidence\latest\verifier-output\verify_licflow3_route-*.json`.
**Causa real:** El worker vivo `prisma-cloud-semilla` estaba en version `prcloud5-2026-06-23` y no tenia las rutas POST de LICFLOW3; el `wrangler.jsonc` local todavia apuntaba al scaffold `prisma-licflow3-cloud-licensing` y D1 placeholder, no al worker/D1 reales.
**Rollback probado:** N/A. No hubo deploy ni mutacion cloud; rollback local es revertir el diff de `infra/cloudflare/licflow3-worker`, `tools/verify-licflow3.mts`, `package.json` y docs.
**Regla nueva:** En LICFLOW3, antes de diagnosticar handlers, confirmar tres cosas juntas: respuesta viva con version, worker/D1 reales en Wrangler, y `wrangler.jsonc` local apuntando a esos nombres reales. Si local pasa y live sigue 404, el cierre honesto es `LOCAL_READY_CLOUDFLARE_DEPLOY_AUTH_REQUIRED`.
**Notas:** No llamar PASS funcional hosted hasta tener deploy/smoke autorizado. Dummy route evidence puede aceptar `400/401/403/422`, nunca `404` ni `5xx`.

### 2026-07-03 21:34 - LICFLOW4 Admin Bridge pertenece al backend local 3160

**Tipo:** GOVERNANCE_LEARNING / EVIDENCE_LEARNING / COMMAND_WORKS
**Superficie:** Prisma Cloud Ctr / LICFLOW4 / 3160
**Contexto:** Prisma Cloud Ctr necesitaba operar `activate`, `refresh` y `revoke` contra LICFLOW3 sin entregar `ADMIN_TOKEN` al navegador ni crear otro cockpit o adapter.
**Precondiciones:** Repo `F:\repos\hitech-os`, app `apps/terminal-de-venta-system`, sin AutoGit, sin stash, sin deploy Cloudflare, sin D1 dump/export/copy, sin matar procesos, sin tocar Mobile/PC/Tablet.
**Comando exacto:**

```powershell
pnpm run verify:licflow4:admin-bridge
pnpm run verify:licflow4:no-token-frontend
pnpm run verify:licflow4:confirmations
pnpm run verify:licflow4:diagnostics-sanitized
pnpm run verify:licflow4:no-autorun-mutations
```

**Resultado observado:** PASS local. Python compile, JS check, JSON parse, self-test, LICFLOW3 verifiers seguros y LICFLOW4 verifiers nuevos pasaron sin deploy, sin D1 y sin mutacion real.
**Evidencia:** `F:\descargasf\licflow4-admin-bridge-inventory-*.zip`; `F:\descargasf\licflow4-admin-bridge-precommit-*.zip`; `F:\descargasf\licflow4-admin-bridge-result-*.zip`.
**Causa real:** El token admin debe vivir en el backend local y leerse solo dentro de la ruta confirmada. El frontend solo puede recibir booleanos, codigos sanitizados y resumen de audit redacted.
**Rollback probado:** N/A hasta cierre del PR; rollback local es revertir el rename de `Prisma Cloud Ctr`, `licflow4_admin_bridge.py`, scripts `verify:licflow4:*`, docs y verifiers tocados.
**Regla nueva:** Para LICFLOW4, el orden seguro es inventario ZIP, bridge backend local, UI sin token, dry-run primero, confirmacion `confirmAdminLicenseAction: true`, revoke con `REVOKE_LICENSE`, diagnostics sanitizado, verifiers sin mutacion real, evidence ZIP, staging explicito sin Mobile/PC/Tablet ni generated evidence.
**Notas:** Si una referencia historica vive en PC o generated evidence excluido, no arrastrarla al commit LICFLOW4; reportarla como scope conflict en lugar de ensuciar trabajo paralelo.

### 2026-07-04 - LICFLOW5 canonical naming y Customer Setup multi-device

**Tipo:** GOVERNANCE_LEARNING / EVIDENCE_LEARNING / COMMAND_WORKS
**Superficie:** Prisma Cloud Ctr / Prisma Cloud Center / License Operations / Customer Setup / 3160
**Contexto:** LICFLOW3/LICFLOW4 son nombres historicos utiles para rutas, verifiers y lineage tecnico, pero no deben ser lenguaje principal de operador. El mismo pase agrega Prisma Customer Setup para cliente Tablet + PC + Mobile sin crear otro Control Center.
**Precondiciones:** Repo `F:\repos\hitech-os`, app `apps/terminal-de-venta-system`, sin deploy Cloudflare, sin D1 live, sin secretos, sin matar procesos, sin levantar dev servers, sin Prisma regenerate.
**Comando exacto:**

```powershell
pnpm -C apps/terminal-de-venta-system run verify:license:canonical-naming
pnpm -C apps/terminal-de-venta-system run verify:customer-setup:multidevice
```

**Resultado observado:** Source-ready esperado. Los nombres con numeros quedan en lineage tecnico, rutas, verifiers, constantes y raw diagnostics; UI/docs operador usan `Prisma Cloud Center`, `Cloud License Gateway`, `License Admin Bridge`, `Simulation (Dry Run)`, `Confirmed License Operation`, `License Operation Audit`, `License Diagnostics` y `License Route Map`.
**Evidencia:** Verifiers source-only y diff de Cloud Ctr/shared licensing/Cloud Gateway source.
**Causa real:** Operador necesita lenguaje humano y flujo seguro; cliente necesita Setup Link, Setup Code, Setup QR y Device Slots sin admin token.
**Rollback probado:** N/A. Rollback local es revertir los archivos source/docs/verifiers tocados.
**Regla nueva:** No crear otro Control Center ni otro customer setup subsystem. Extender `Prisma Cloud Ctr`, `shared/licensing`, Cloud License Gateway source y las tres superficies con un contrato compartido. Source-ready no equivale a hosted PASS hasta deploy/D1 autorizados.
**Notas:** Pendiente futuro: migrar nombres de package scripts solo con plan de compatibilidad; live Customer Setup requiere autorizacion explicita de deploy y migracion D1.
