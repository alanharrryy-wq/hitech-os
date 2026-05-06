# PRISMA POS · Terminal de Venta System

**Proyecto:** PRISMA POS / Terminal de Venta  
**Raíz operativa:** `F:\repos\hitech-os\apps\terminal-de-venta-system`  
**Idioma visible:** `es-MX`  
**Estado:** arquitectura viva, modular y gobernada  
**Regla madre:** **Tablet vende sola. PC y App móvil son assets complementarios.**

---

## 1. Qué es PRISMA

PRISMA es una plataforma POS modular para negocios que necesitan vender, controlar inventario y crecer sin convertir el sistema en un plato de espagueti con credencial corporativa.

El sistema no es un POS simple. Está pensado como una arquitectura por productos, contratos compartidos y entregas instalables:

- **Tablet POS:** venta, caja, ticket, stock local, operación offline y eventos.
- **PC Backoffice:** administración, inventario avanzado, auditoría, compras, recepción, reabasto, dashboard y control multi-operación.
- **App móvil / Pulso:** consulta, alertas, resumen operativo y seguimiento ligero.
- **Shared Kernel / Shared UI:** contratos, tokens visuales, glosario, eventos y compatibilidad.
- **Licenciamiento:** planes, activación de dispositivos, entitlements, firma de licencias, gracia offline y auditoría de uso.
- **Verticales:** paquetes por giro de negocio sobre un core común.

---

## 2. Decisión canónica de producto

La decisión más importante del proyecto es esta:

```text
Tablet es el POS autónomo.
PC es un asset de backoffice y control avanzado.
App móvil es un asset de pulso, consulta y alertas.
Shared contracts son el contrato común.
Ningún asset debe convertirse en requisito para que Tablet venda.
```

Esto evita el error clásico de tratar a Tablet como terminal tonta subordinada a PC. No. Tablet cobra aunque PC no exista. PC entra cuando el negocio ya necesita gobierno operativo, no cuando alguien quiere vender su primer refresco.

| Superficie | Rol | Puede vivir sola | No debe hacer |
|---|---|---:|---|
| Tablet POS | Venta local, caja, ticket, stock operativo, corte, outbox | Sí | Depender de PC para vender |
| PC Backoffice | Gobierno, inventario avanzado, auditoría, compras, recepción, dashboard | Sí, como panel admin | Bloquear venta local básica |
| App móvil / Pulso | Consulta, alertas, resumen y seguimiento ligero | Sí, como companion | Volverse requisito de venta |
| Shared Kernel/UI | Contratos y lenguaje común | No aplica | Convertirse en basurero de utilidades |

---

## 3. Principios no negociables

1. **Tablet debe vender sola.**
   - Carga catálogo local.
   - Crea tickets.
   - Cierra ventas.
   - Descuenta stock local.
   - Genera eventos/outbox.
   - Exporta datos.
   - Opera offline cuando aplique.

2. **PC no es permiso para vender.**
   - PC administra, audita, consolida y gobierna cuando existe.
   - Si un flujo de venta básica exige PC, ese flujo está mal diseñado.

3. **App móvil no es PC chiquita.**
   - Aunque viva técnicamente dentro de `products/pc/app`, se valida como superficie visual independiente.
   - Su papel es pulso, alertas, consulta y acompañamiento.

4. **Todo cambio visual debe cubrir las tres superficies.**
   - Tablet.
   - PC.
   - App móvil.
   - Si una no se toca, debe declararse y justificarse.

5. **Toda entrega relevante debe ser reversible.**
   - ZIP con payload exacto.
   - Instalador `.py`.
   - `--dry-run`, `--apply`, `--verify`, `--rollback`.
   - Backup previo.
   - Log único en `F:\descargasf`.

---

## 4. Estructura operativa esperada

```text
apps/terminal-de-venta-system/
  README.md
  terminal_de_venta.cmd
  docs/
    architecture/
    design/
    productization/      # licencias, activación, runtime, soporte y release
    qa/
  local-runtime/         # material local de desarrollo: licencias firmadas, config local y llaves dev
  manifests/
  products/
    tablet/
      app/
        app/
        components/
        src/
        prisma/
        data/
    pc/
      app/
        app/
          prisma-app/        # App móvil / Pulso, aunque viva bajo PC
          pulso/             # Legacy Pulso cuando exista
        src/
        prisma/
        docs/
    shared-ui/
      prisma/
        tokens/
        components/
  packages/
    shared-kernel/
  shared/
    contracts/
      ui/
  tools/
    prisma/
  tooling/
    licensing/           # motores, políticas, scanners, contratos y regresiones de licenciamiento
```

> Nota importante: `products/mobile/app` es la raíz canónica de **PRISMA App / Mobile**. Las rutas históricas bajo `products/pc/app` son legacy y no convierten Mobile en una pantalla hija de PC.

---

## 5. Superficies visuales oficiales

| ID lógico | Nombre | Rutas principales |
|---|---|---|
| `prisma.tablet.pos` | Tablet POS | `products/tablet/app/**` |
| `prisma.pc.backoffice` | PC Backoffice | `products/pc/app/**` |
| `prisma.mobile.app` | App móvil / Pulso | `products/mobile/app/**` |
| `prisma.shared.visual` | Shared visual layer | `products/shared-ui/prisma/**`, `shared/contracts/ui/**`, `docs/design/**`, `docs/qa/**`, `tools/prisma/**`, `manifests/**` |

Cuando se toque `prisma.shared.visual`, el cambio debe declarar cobertura de Tablet, PC y App móvil.

---

## 6. Gobierno visual actual

El proyecto ya cuenta con capas de gobierno para evitar que el CSS se convierta en sopa de neón:

| Paquete | Propósito |
|---|---|
| `PRISMA_BLACK_VISUAL_GOVERNANCE_BASELINE_01E` | Baseline de gobierno visual Black: documentación, contrato, manifest y checker. |
| `PRISMA_BLACK_VISUAL_GOVERNANCE_01E_CHECKER_HOTFIX_00A` | Corrige el checker 01E para ejecución compatible. |
| `PRISMA_BLACK_CSS_LAYER_NORMALIZATION_01F` | Normaliza capas CSS con markers y contratos sin rediseñar visualmente. |
| `PRISMA_TRI_SURFACE_VISUAL_GUARDIAN_00B` | Obliga a declarar cobertura visual para Tablet, PC y App móvil. |

Regla práctica:

```text
Antes de cualquier cambio visual premium, correr/verificar guardianes.
Si falta matriz tri-superficie, el cambio no entra.
```

---

## 7. Capas visuales Black

La experiencia visual Black se rige por esta jerarquía:

```text
Capa 1: Fondo vive.
Capa 2: Panel grande interpreta.
Capa 3: Card enmarca.
Capa 4: Contenido informa.
Capa 5: Glow sólo jerarquiza.
```

Regla anti-caos:

```text
Si todo brilla, nada brilla.
Si cada card tiene su propia niebla, volvemos al caldo premium de fantasma.
```

Los pases visuales deben ordenar primero y embellecer después. El proyecto no debe resolver deuda visual echándole más glow encima, que es básicamente pintar humedad con dorado.

---

## 8. Contrato de entregas

Toda entrega que modifique repo debe seguir este contrato:

```text
ZIP + instalador .py
```

El instalador debe soportar:

```text
--dry-run
--apply
--verify
--rollback
```

También debe incluir:

- backup previo de archivos afectados;
- rollback automático si falla `apply` o `verify`;
- rollback manual;
- log único directamente en `F:\descargasf`;
- validación posterior;
- independencia del directorio actual;
- rutas absolutas o `--target-root` explícito.

Formato recomendado de log:

```text
F:\descargasf\<paquete>_int_YYMMDD_HHMM.log
```

---

## 9. Comandos de desarrollo usados en local

Raíz del monorepo:

```powershell
$Repo = "F:\repos\hitech-os"
```

Raíz del proyecto:

```powershell
$TargetRoot = "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

Rutas de app:

```powershell
$TabletRoot = "F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app"
$PcRoot = "F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app"
```

Puertos usados para desarrollo local:

| Producto | Puerto | Health / ruta esperada |
|---|---:|---|
| Tablet | `3120` | `http://127.0.0.1:3120/prisma-dark-pos-reference` |
| PC | `3130` | `http://127.0.0.1:3130/` |

Cuando se use `pnpm`, preferir ejecución con raíz explícita, no depender del directorio actual:

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app" dev
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app" dev
```

---

## 10. Checkers importantes

Checkers de gobierno visual:

```powershell
node "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma\verify_prisma_black_visual_governance_01e.mjs" --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --text

node "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma\verify_prisma_black_css_layer_normalization_01f.mjs" --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --text

python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma\prisma_tri_surface_visual_guardian_00b.py" --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --manifest "F:\repos\hitech-os\apps\terminal-de-venta-system\manifests\PRISMA_TRI_SURFACE_VISUAL_GUARDIAN_00B.manifest.json" --text
```

Los warnings visuales no siempre son fallo automático. Sirven como guía para no crear una UI donde cada botón quiere ser antro, faro y santo patrono al mismo tiempo.

---

## 11. Arquitectura Tablet POS

Tablet debe operar como POS standalone:

```text
UI Touch
  -> API Routes / Server Actions
    -> pos-api
      -> pos-engine
        -> Prisma Client
          -> SQLite local tablet-pos.db
            -> Outbox/Event Log
```

DB local canónica:

```text
products/tablet/app/data/tablet-pos.db
```

Errores canónicos mínimos:

```text
EMPTY_CART
INVALID_QUANTITY
PRODUCT_NOT_FOUND
PRODUCT_INACTIVE
INSUFFICIENT_STOCK
TERMINAL_NOT_FOUND
NETWORK_UNAVAILABLE
SYNC_PENDING
```

Eventos mínimos:

```text
sale.created
sale.completed
ticket.closed
stock.decremented
inventory.low_stock_detected
```

---

## 12. Arquitectura PC Backoffice

PC es backoffice y control avanzado. Debe cubrir:

- catálogo;
- SKUs y códigos de barras;
- stock y movimientos;
- conteos físicos;
- compras;
- recepción;
- reabasto;
- auditoría;
- sincronización;
- dashboard ejecutivo;
- conflictos y consolidación.

PC puede administrar y reconciliar, pero no debe bloquear la venta local básica de Tablet.

---

## 13. App móvil / Pulso

La App móvil es un asset companion. Su rol principal:

- ver pulso operativo;
- consultar métricas ligeras;
- recibir alertas;
- revisar estado de operación;
- acompañar decisiones rápidas.

Rutas actuales relevantes:

```text
products/pc/app/app/prisma-app/**
products/pc/app/app/pulso/**
products/pc/app/src/lib/prisma-app/**
products/pc/app/src/lib/pulso/**
products/pc/app/docs/prisma-app/**
```

Aunque técnicamente viva en `products/pc/app`, no se debe mezclar su cobertura visual con PC Backoffice.

---

## 14. Licenciamiento, activación y entitlements

El licenciamiento de PRISMA no debe ser un candado atravesado en la caja. Debe ser el gafete operativo del sistema: identifica el plan, activa capacidades, registra estados y protege el negocio sin impedir que Tablet haga su trabajo básico cuando la red se pone de payasa.

Regla madre aplicada al licenciamiento:

```text
La licencia gobierna capacidades.
La licencia no convierte a PC ni a internet en permiso para vender.
Tablet debe poder vender localmente si tiene una licencia local válida o una gracia offline vigente.
```

### 14.1 Modelo mental correcto
El flujo correcto es:

```text
Servidor/Admin de licencias
  -> define cliente, plan, terminales y entitlements
  -> genera licencia
  -> firma licencia
  -> entrega licencia firmada

Tablet / PC
  -> guarda licencia local
  -> verifica firma con llave pública o registro permitido
  -> resuelve estado de licencia
  -> activa o bloquea features según plan y política
  -> registra auditoría de eventos sensibles
```

Dicho sin incienso corporativo: el servidor pone el sello, la app verifica el sello y luego decide qué puede hacer. No se aceptan licencias “porque sí”, ni features activadas por ocurrencia, ni llaves privadas tiradas en el repo como volante de taquería.

### 14.2 Planes comerciales esperados
| Plan | Rol | Debe permitir | No debe asumir |
|---|---|---|---|
| `TABLET_SOLO` | POS autónomo básico | venta local, tickets, stock local, corte, exportación y operación offline controlada | PC disponible |
| `TABLET_PRO` | POS autónomo con más control | permisos, devoluciones, turnos, ajustes locales autorizados, reportes mejores y respaldo/export avanzado | internet permanente |
| `TABLET_PC_REQUIRED` | operación administrada | sync con PC, políticas, inventario avanzado, auditoría fuerte, multi-sucursal y resolución de conflictos | que Tablet deje de vender si cae PC |

Si un cliente complejo compra sólo Tablet sin auditoría/backoffice, el problema es comercial. Si una tiendita chica necesita PC para vender un refresco, el problema es técnico. Ambos son formas caras de patear una cubeta.

### 14.3 Modos técnicos de licencia
| Modo | Qué significa | PC requerido | Internet requerido | Comportamiento esperado |
|---|---|---:|---:|---|
| `standalone` | Tablet opera con licencia local y datos locales | No | No | Venta básica sigue; exportación local disponible |
| `managed` | Tablet opera con PC/backoffice disponible para administración avanzada | Sí para gobierno | Intermitente o estable | Venta sigue localmente; sync reconcilia después |
| `degraded_managed` | Operación administrada con PC/red caída | Sí para gobierno futuro | No para venta básica | Venta permitida si política/gracia lo permite; eventos quedan marcados |

### 14.4 Rutas canónicas
Docs de licenciamiento:

```text
docs/productization/PRISMA_LICENSES_README.md
docs/productization/PRISMA_LICENSE_SERVER_CONTRACT_05.md
docs/productization/PRISMA_DEVICE_ACTIVATION_CONTRACT_05.md
docs/productization/PRISMA_LICENSE_ADMIN_PORTAL_CONTRACT_05.md
docs/productization/PRISMA_LICENSE_STATE_MACHINE.md
docs/productization/PRISMA_LOCAL_LICENSE_STORE_CONTRACT.md
docs/productization/PRISMA_OFFLINE_GRACE_POLICY.md
docs/productization/PRISMA_LICENSE_OPERATIONS_RUNBOOK.md
docs/productization/PRISMA_LICENSE_OPERATION_MATRIX.md
docs/productization/PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D.md
docs/productization/PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D_ACCEPTANCE.md
```

Runtime local de desarrollo:

```text
local-runtime/license/
local-runtime/license-keys/dev/
local-runtime/license-server/
```

Tooling técnico:

```text
tooling/licensing/
tooling/licensing/server11d/
```

La raíz del proyecto no debe llenarse de `.cmd`, `.json`, backups ni estados temporales de licencias. Eso va en `tools/`, `tooling/`, `manifests/`, `local-runtime/` o `F:\Trash-old`, según corresponda. La raíz no es cajón de calcetines.

### 14.5 Qué debe contener una licencia firmada
La forma exacta puede evolucionar, pero el mínimo conceptual debe cubrir:

```json
{
  "licenseId": "lic_...",
  "businessId": "biz_...",
  "deviceId": "dev_...",
  "terminalId": "term_...",
  "plan": "TABLET_PRO",
  "mode": "standalone",
  "features": {
    "pos.sale.complete": true,
    "report.today.view": true,
    "export.local.create": true,
    "pos.return.create": false,
    "sync.pc.enabled": false
  },
  "issuedAt": "2026-04-30T00:00:00.000Z",
  "validFrom": "2026-04-30T00:00:00.000Z",
  "expiresAt": "2027-04-30T00:00:00.000Z",
  "offlineGraceUntil": "2027-05-07T00:00:00.000Z",
  "keyId": "dev-local",
  "signature": "..."
}
```

Campos mínimos:

| Campo | Para qué sirve |
|---|---|
| `licenseId` | identidad única de licencia |
| `businessId` | negocio dueño |
| `deviceId` / `terminalId` | dispositivo o caja autorizada |
| `plan` | paquete comercial |
| `mode` | modo técnico de operación |
| `features` | entitlements concretos |
| `issuedAt`, `validFrom`, `expiresAt` | vigencia |
| `offlineGraceUntil` | tolerancia offline |
| `keyId` | llave pública/registro que verifica la firma |
| `signature` | prueba de integridad |

### 14.6 Estados de licencia
La app debe resolver un estado, no inventar booleanos sueltos por todo el código.

| Estado | Significado | Venta básica | Acciones sensibles |
|---|---|---:|---:|
| `valid` | firma válida y vigencia correcta | Permitida | Según features |
| `grace` | expiró validación online, pero hay gracia offline | Permitida con marca | Limitadas |
| `expired` | vencida y sin gracia | Bloqueada o modo lectura, según política | Bloqueadas |
| `invalid_signature` | firma no válida | Bloqueada | Bloqueadas |
| `device_mismatch` | licencia no corresponde al dispositivo | Bloqueada | Bloqueadas |
| `missing` | no hay licencia local | onboarding/activación | Bloqueadas |
| `revoked` | marcada como revocada por servidor/backoffice | Bloqueada tras confirmación | Bloqueadas |

Regla anti-desmadre:

```text
Nunca decidir features con checks dispersos tipo if plan == "PRO" en pantallas.
Primero resolver estado y entitlements; luego UI/API consumen esa decisión.
```

### 14.7 Entitlements mínimos
Permisos base de Tablet Solo:

```text
pos.sale.create
pos.sale.complete
pos.ticket.view
inventory.local.view
report.today.view
export.local.create
```

Permisos de Tablet Pro:

```text
pos.sale.cancel
pos.return.create
inventory.local.adjust
shift.open
shift.close
event.outbox.view
```

Permisos administrados Tablet + PC:

```text
catalog.write
price.write
inventory.adjust.approve
purchase.write
receiving.write
audit.view
sync.conflict.resolve
user.permission.manage
sync.pc.enabled
```

Las pantallas deben esconder, deshabilitar o explicar acciones según entitlement. No se vale que el botón aparezca feliz y luego explote con error críptico. Eso es UX de puesto que dice “sí hay sistema” y luego cobra en libreta.

<!-- PRISMA_MAIN_README_FEATURE_KEYS_12F_START -->
### 14.8 Feature keys canonicas
Los **feature keys** son los nombres canonicos de capacidades que una licencia puede encender, apagar o limitar. Son el puente entre el plan comercial, la licencia firmada y la decision tecnica en runtime.

Regla sencilla: el plan dice el paquete vendido; los entitlements dicen que capacidades incluye; los **feature keys** son los identificadores exactos que consume codigo, UI, API, QA y auditoria.

Nunca se deben inventar feature keys dentro de componentes, pantallas o scripts sueltos. Eso termina en el clasico changarro donde una pantalla cree que el cliente es PRO, otra cree que es SOLO y la caja queda como tiendita con dos libretas diferentes.

#### 14.8.1 Catalogo minimo de feature keys

| Feature key | Proposito | Plan minimo esperado | Superficie |
|---|---|---|---|
| `pos.sale.create` | Permite iniciar una venta local | `TABLET_SOLO` | Tablet |
| `pos.sale.complete` | Permite cerrar/cobrar una venta local permitida | `TABLET_SOLO` | Tablet |
| `pos.ticket.view` | Permite consultar ticket local | `TABLET_SOLO` | Tablet |
| `inventory.local.view` | Permite ver inventario local operativo | `TABLET_SOLO` | Tablet |
| `report.today.view` | Permite ver resumen operativo del dia | `TABLET_SOLO` | Tablet |
| `export.local.create` | Permite exportar ventas/eventos locales | `TABLET_SOLO` | Tablet |
| `pos.sale.cancel` | Permite cancelar ventas bajo politica | `TABLET_PRO` | Tablet |
| `pos.return.create` | Permite registrar devoluciones | `TABLET_PRO` | Tablet |
| `inventory.local.adjust` | Permite ajustes locales controlados | `TABLET_PRO` | Tablet |
| `shift.open` | Permite abrir turno | `TABLET_PRO` | Tablet |
| `shift.close` | Permite cerrar turno | `TABLET_PRO` | Tablet |
| `event.outbox.view` | Permite revisar outbox/eventos pendientes | `TABLET_PRO` | Tablet |
| `sync.managed.enable` | Habilita operacion administrada con PC/backoffice | `TABLET_PC_REQUIRED` | Tablet + PC |
| `pc.backoffice.dashboard.view` | Permite ver dashboard ejecutivo | `TABLET_PC_REQUIRED` | PC |
| `catalog.write` | Permite modificar catalogo maestro | `TABLET_PC_REQUIRED` | PC |
| `price.write` | Permite modificar precios maestros | `TABLET_PC_REQUIRED` | PC |
| `inventory.adjust.approve` | Permite aprobar ajustes sensibles | `TABLET_PC_REQUIRED` | PC |
| `purchase.write` | Permite crear/editar compras | `TABLET_PC_REQUIRED` | PC |
| `receiving.write` | Permite registrar recepcion | `TABLET_PC_REQUIRED` | PC |
| `audit.view` | Permite consultar auditoria | `TABLET_PC_REQUIRED` | PC |
| `sync.conflict.resolve` | Permite resolver conflictos de sincronizacion | `TABLET_PC_REQUIRED` | PC |
| `user.permission.manage` | Permite administrar permisos | `TABLET_PC_REQUIRED` | PC |
| `license.verify` | Permite validar firma, vigencia y estado de licencia | Sistema | Runtime |
| `license.activate.device` | Permite activar dispositivo/terminal | Sistema | Server + Runtime |
| `license.offline.grace.use` | Permite operar dentro de gracia offline | Sistema | Runtime |
| `license.feature.denied.audit` | Registra intento de usar feature no incluida | Sistema | Auditoria |

#### 14.8.2 Reglas de nombrado

- Los feature keys usan minusculas, puntos y nombres de dominio: `dominio.recurso.accion`.
- No usar textos visibles como key. `Cobrar venta` es etiqueta de UI; `pos.sale.complete` es contrato tecnico.
- No usar keys por pantalla. La pantalla consume capacidades; no define contratos.
- No duplicar synonyms. Elegir uno: `pos.sale.complete`, no tambien `sales.checkout.finish`.
- No cambiar un feature key sin migracion, alias temporal y nota de compatibilidad.

#### 14.8.3 Donde viven y quien manda

La fuente canonica debe vivir en contrato/documentacion y despues reflejarse en codigo:

```text
docs/productization/PRISMA_LICENSES_README.md
README.md
shared/contracts/licensing/   # cuando exista contrato formal de licensing
packages/shared-kernel/       # solo si se vuelve contrato compartido real
```

La UI no decide licenciamiento. La UI pregunta por capacidades ya resueltas.
La API no inventa planes. La API valida contra licencia resuelta.
El servidor no firma ocurrencias. Firma un documento con plan, entitlements, feature keys y vigencia.

#### 14.8.4 Forma recomendada en licencia firmada

```json
{
  "plan": "TABLET_PRO",
  "features": {
    "pos.sale.create": true,
    "pos.sale.complete": true,
    "report.today.view": true,
    "pos.return.create": true,
    "sync.managed.enable": false
  }
}
```

#### 14.8.5 Regla anti-regresion

Si alguien agrega una funcionalidad vendible o restringible, debe declarar:

```text
featureKey:
plan minimo:
superficie:
comportamiento offline:
evento de auditoria si se deniega:
prueba de acceptance:
```

Si no puede llenar eso, todavia no es feature vendible; es una ocurrencia con zapatos nuevos.
<!-- PRISMA_MAIN_README_FEATURE_KEYS_12F_END -->

### 14.9 Offline grace
Offline no significa barra libre.

Permitido offline cuando la licencia local lo permite:

- venta con catálogo local activo;
- tickets locales;
- corte local;
- consulta de reporte del día;
- exportación local;
- generación de eventos/outbox;
- sincronización posterior.

Bloqueable offline:

- cambios masivos de precio;
- alta avanzada de productos;
- ajustes grandes de inventario;
- devolución sensible;
- cambios de permisos;
- operaciones multi-sucursal;
- revocación o transferencia de licencia.

Regla:

```text
Si afecta dinero, inventario, permisos, caja, cliente, fiscal o producción, debe generar evento auditable.
```

### 14.10 Firma y seguridad
La licencia debe verificarse por firma. La app cliente no debe confiar en JSON plano sólo porque “se ve bonito”.

Reglas:

- servidor firma;
- cliente verifica;
- cliente no necesita llave privada;
- llaves privadas no se guardan en repo;
- fixtures con PEM sólo se permiten si están explícitamente aprobados como regresión;
- producción no debe firmar con material `dev-local`;
- toda validación sensible debe registrar resultado.

La política activa relacionada es:

```text
PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D
```

Esa política existe para evitar el pecado mortal de dejar material criptográfico vivo regado en el repositorio. Básicamente, para que el repo no parezca mochila de estudiante con contraseñas en post-its.

### 14.11 Comandos útiles de licencia
Smokes actuales esperados desde la raíz del proyecto:

```powershell
F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd license-server-signing-smoke
F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd license-server-signing-scan
F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd license-server-signing-fixture-audit
```

Validación directa del scanner 11D:

```powershell
python F:\repos\hitech-os\apps\terminal-de-venta-system\tooling\licensing\server11d\server_signing_scan_policy_11d.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --out F:\descargasf smoke
```

### 14.12 Qué debe hacer la UI con licencias
La UI no debe hablar como abogado fiscal ni como error de compilador.

Debe mostrar:

| Caso | Mensaje esperado |
|---|---|
| licencia válida | estado discreto, sin estorbar |
| gracia offline | aviso visible: “Operando offline con licencia en gracia” |
| feature no incluida | explicación clara: “Tu plan no incluye esta función” |
| licencia vencida | ruta de renovación/activación |
| firma inválida | bloqueo seguro y mensaje de soporte |
| device mismatch | “Esta licencia no corresponde a esta terminal” |

La UI debe evitar:

- mensajes tipo `invalid_signature`;
- botones habilitados que fallan tarde;
- ventas bloqueadas por no tener PC si el modo permite standalone;
- ocultar estados críticos de licencia/sync.

### 14.13 Auditoría obligatoria
Eventos mínimos:

```text
license.loaded
license.validated
license.validation_failed
license.grace_started
license.grace_expired
license.feature_denied
license.device_mismatch
license.revoked
license.renewed
```

Todo evento debe llevar, cuando aplique:

```text
eventId
businessId
terminalId
deviceId
actorId
licenseId
plan
featureKey
result
reason
occurredAt
schemaVersion
```

### 14.14 Regla de frontera con pagos
PRISMA puede registrar método de pago y cierre de venta, pero el licenciamiento no debe confundirse con procesamiento financiero real.

Regla:

```text
Licencia de PRISMA habilita capacidades del software.
No procesa pagos bancarios por sí misma.
No sustituye PSP, adquirente, tokenización bancaria ni cumplimiento financiero externo.
```

Si un módulo futuro toca pagos reales, debe tener contrato separado. No mezclar licencia de software con cobro bancario, porque así empiezan los incendios con corbata.

### 14.15 Checklist antes de tocar licencias
Antes de modificar licenciamiento, confirmar:

- qué plan o feature se toca;
- si afecta Tablet, PC, App móvil o shared;
- si cambia contrato de licencia;
- si cambia firma o llaves;
- si cambia comportamiento offline;
- si cambia activación de dispositivo;
- si requiere migración de licencia local;
- si requiere evento de auditoría;
- si requiere actualizar docs en `docs/productization`;
- si pasa smoke 11D y fixture audit.

### 14.16 No romper jamás
Prohibido:

- hacer que Tablet dependa de PC para vender básico;
- hacer que internet sea requisito duro para venta standalone;
- guardar llaves privadas productivas en repo;
- validar licencias con JSON sin firma;
- dispersar `if plan == ...` por pantallas;
- bloquear export local permitido por plan;
- activar features sin entitlement;
- esconder estado de gracia offline;
- meter comandos/licencias temporales en raíz;
- prometer planes/features en README que no tengan contrato o implementación.
## 15. Verticales de negocio

PRISMA contempla modularización por giros de negocio mediante contratos de capacidades core y verticales.

El entregable histórico `PRISMA_VERTICALS_ARCHITECTURE_00A_CORE_CONTRACTS` instaló:

- arquitectura vertical base;
- contrato de capacidades core y verticales;
- schema de manifiesto vertical;
- seeds para verticales iniciales;
- matriz QA;
- validador local de contratos.

Este README ya no representa sólo ese entregable. Ahora describe el proyecto completo.

---

## 16. KPIs base

KPIs prioritarios para primeras fases:

- ventas netas;
- número de tickets;
- ticket promedio;
- top SKUs;
- quiebres de stock;
- exactitud de inventario;
- merma;
- cancelaciones/devoluciones;
- fill rate;
- tiempo promedio de venta;
- latencia de sincronización.

Tablet alimenta operación y eventos. PC consolida, audita y convierte esos datos en tablero. App móvil muestra pulso y alertas.

---

## 17. Cómo pedir o integrar cambios

Toda solicitud debe declarar:

```text
objetivo:
alcance:
tipo de entrega: .py o ZIP + .py
restricciones:
validación esperada:
```

Ejemplo:

```text
objetivo: refinamiento visual Black 01G
alcance: shared-ui, PC, Tablet y App móvil
entrega: ZIP + instalador .py
restricciones: no tocar datos, layout ni TS/TSX salvo necesidad explícita
validación: checkers 01E, 01F y guardian 00B pasan con matriz tri-superficie
```

---

## 18. Definition of Done

Una entrega se considera aceptable sólo si:

- tiene objetivo claro;
- define alcance;
- respeta Tablet standalone;
- declara impacto PC / Tablet / App móvil cuando es visual;
- incluye backup;
- incluye log único;
- puede aplicarse con `--dry-run`;
- puede verificarse con `--verify`;
- puede revertirse con `--rollback`;
- no depende del directorio actual;
- no introduce cambios silenciosos;
- no promete más de lo que instala.

---

## 19. Estado mental correcto del proyecto

```text
Tablet vende sola.
Tablet deja eventos.
PC administra cuando existe.
App móvil observa y alerta.
Sync reconcilia.
Shared contracts mantienen compatibilidad.
Los paquetes entran gobernados, verificables y reversibles.
```

Ese es el norte. Todo lo demás es decoración, y la decoración sin contrato termina siendo foquito navideño pegado con cinta en tablero eléctrico.
