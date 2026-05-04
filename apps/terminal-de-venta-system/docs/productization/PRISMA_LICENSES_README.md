# PRISMA Licencias - README operacional

**ID:** `PRISMA_LICENSES_README_12C`  
**Proyecto:** Terminal de Venta / PRISMA POS  
**Ruta esperada:** `docs/productization/PRISMA_LICENSES_README.md`  
**Estado:** guia canonica de lectura y operacion  
**Idioma visible:** es-MX  
**Objetivo:** explicar, sin humo ni magia negra de pasillo, como debe funcionar el sistema de licencias de PRISMA y que documento se debe consultar para cada decision.

---

## 0. Lectura rapida para no cagarla

PRISMA tiene licencias para **habilitar capacidades**, no para secuestrar la caja.

La regla madre es esta:

```text
Tablet debe poder vender localmente.
PC gobierna cuando el negocio necesita control fuerte.
La licencia decide que capacidades tiene el cliente.
La licencia no debe destruir datos, bloquear exportaciones de emergencia ni convertir la app en ladrillo por falta de internet.
```

Dicho en barrio: la licencia es como pulsera de acceso del baile. Te dice si puedes entrar a VIP, barra libre o zona general. Pero no debe quitarle las piernas al cajero cuando se cae el WiFi.

---

## 1. Donde empezar

Abre este README primero cuando tengas cualquier duda sobre licencias.

Luego usa este mapa:

| Pregunta | Documento |
|---|---|
| Como se modela el servidor de licencias | `docs/productization/PRISMA_LICENSE_SERVER_CONTRACT_05.md` |
| Como se activa una terminal/dispositivo | `docs/productization/PRISMA_DEVICE_ACTIVATION_CONTRACT_05.md` |
| Como se opera el portal administrativo | `docs/productization/PRISMA_LICENSE_ADMIN_PORTAL_CONTRACT_05.md` |
| Que estados puede tener una licencia | `docs/productization/PRISMA_LICENSE_STATE_MACHINE.md` |
| Donde vive la licencia local | `docs/productization/PRISMA_LOCAL_LICENSE_STORE_CONTRACT.md` |
| Que pasa sin internet | `docs/productization/PRISMA_OFFLINE_GRACE_POLICY.md` |
| Que features incluye cada plan | `docs/productization/PRISMA_PLAN_CATALOG_CONTRACT.md` |
| Como se nombran las feature keys | `docs/productization/PRISMA_FEATURE_KEYS_CATALOG.md` |
| Como se decide si algo esta permitido | `docs/productization/PRISMA_LICENSE_ENTITLEMENTS_CONTRACT.md` |
| Como se opera soporte/smoke/reportes | `docs/productization/PRISMA_LICENSE_OPERATIONS_RUNBOOK.md` |
| Matriz rapida por estado | `docs/productization/PRISMA_LICENSE_OPERATION_MATRIX.md` |
| Seguridad de firma y escaneo 11D | `docs/productization/PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D.md` |
| Acceptance de 11D | `docs/productization/PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D_ACCEPTANCE.md` |
| Frontera de no procesar pagos | `docs/productization/PRISMA_NO_PAYMENT_PROCESSING_BOUNDARY.md` |

---

## 2. Modelo mental correcto

### 2.1 Que es una licencia

Una licencia es un **documento firmado** que dice:

- quien es el cliente;
- que negocio/sucursal esta cubierto;
- que dispositivo o terminal puede operar;
- que plan tiene;
- que features estan habilitadas;
- que limites aplica;
- desde cuando y hasta cuando es valida;
- cuantos dias puede operar sin refresh remoto;
- con que llave fue firmada;
- que firma permite detectar tampering.

No es un archivo de configuracion cualquiera. No es un `.json` para editar a mano cuando da flojera hacer portal. No es un papelito pegado al monitor. Es un contrato operativo.

### 2.2 Que no es una licencia

Una licencia no debe ser:

- una dependencia dura de internet para cada venta;
- una excusa para borrar datos;
- una forma de bloquear exportaciones de emergencia;
- un permiso para procesar pagos bancarios dentro de PRISMA;
- una llave privada escondida en el repo;
- un `if (isPro)` regado en veinte componentes como cucarachas de cocina.

---

## 3. Productos, planes y modos

### 3.1 Productos

PRISMA tiene dos productos relacionados:

| Producto | Papel | Regla |
|---|---|---|
| Tablet POS | vende, opera caja, genera tickets, descuenta stock local | debe poder vender sola |
| PC Backoffice | gobierna catalogo, inventario, compras, recepcion, auditoria, dashboard y sync | no debe ser requisito para venta local basica |

### 3.2 Planes comerciales

| Plan | Cliente ideal | Debe permitir |
|---|---|---|
| `TABLET_SOLO` | tiendita, bazar, food truck, negocio chico | venta local, ticket, stock local, corte, export basico |
| `TABLET_PRO` | negocio chico con empleados o control mas serio | lo de Solo + devoluciones, turnos, ajustes locales, outbox visible, export avanzado |
| `PC_BACKOFFICE` | negocio que quiere administrar inventario y operacion | catalogo, inventario, compras, recepcion, auditoria, dashboard, sync ingest |
| `TABLET_PC_MANAGED` / `TABLET_PC_REQUIRED` | negocio con varias cajas/sucursales/control fuerte | Tablet + PC, sync gobernado, conflictos, dispositivos, refresh remoto |

> Nota de naming: el repositorio puede tener docs con `TABLET_PC_REQUIRED` y otros con `TABLET_PC_MANAGED`. La intencion de producto es la misma familia: Tablet operando bajo gobierno de PC/backoffice. Antes de implementar una nueva capa, conviene normalizar el nombre canonico en contratos.

### 3.3 Modos tecnicos

| Modo | PC requerido | Internet requerido | Lectura correcta |
|---|---:|---:|---|
| `standalone` | no | no | Tablet vende con DB local y licencia local valida |
| `managed` | si | intermitente/estable | Tablet sincroniza con backoffice cuando puede |
| `degraded_managed` | si para gobierno, no para vender | no para venta basica | aunque caiga PC/red, Tablet conserva operacion permitida |

---

## 4. Arquitectura de licenciamiento

### 4.1 Flujo principal

```text
Admin / soporte
  -> crea cliente, negocio, plan y licencia
  -> activa dispositivo o terminal
  -> servidor genera payload canonico
  -> servidor firma licencia
  -> Tablet/PC guarda licencia local
  -> runtime verifica firma y vigencia
  -> feature gates prenden/apagan capacidades
  -> eventos de auditoria registran cambios sensibles
```

### 4.2 Separacion de responsabilidades

| Capa | Responsabilidad | No debe hacer |
|---|---|---|
| Servidor de licencias | emitir, renovar, suspender, revocar y firmar licencias | meter llaves privadas al repo |
| Portal admin | operar clientes, negocios, dispositivos, planes y auditoria | editar JSON productivo a mano |
| Runtime local | leer licencia, validar firma, calcular estado y features | depender de `cwd` o de internet inmediato |
| Feature gates | decidir si una accion esta habilitada | tener reglas comerciales duplicadas en UI |
| Tablet | vender localmente segun licencia y politica | depender de PC para venta basica |
| PC | gobernar, auditar y consolidar | bloquear venta local permitida |
| Soporte | diagnosticar, exportar evidencia, refresh controlado | saltarse auditoria |

---

## 5. Archivos y carpetas importantes

### 5.1 Documentacion

```text
docs/productization/PRISMA_LICENSES_README.md
docs/productization/PRISMA_LICENSE_SERVER_CONTRACT_05.md
docs/productization/PRISMA_DEVICE_ACTIVATION_CONTRACT_05.md
docs/productization/PRISMA_LICENSE_ADMIN_PORTAL_CONTRACT_05.md
docs/productization/PRISMA_LICENSE_STATE_MACHINE.md
docs/productization/PRISMA_LOCAL_LICENSE_STORE_CONTRACT.md
docs/productization/PRISMA_OFFLINE_GRACE_POLICY.md
docs/productization/PRISMA_PLAN_CATALOG_CONTRACT.md
docs/productization/PRISMA_FEATURE_KEYS_CATALOG.md
docs/productization/PRISMA_LICENSE_ENTITLEMENTS_CONTRACT.md
docs/productization/PRISMA_LICENSE_OPERATIONS_RUNBOOK.md
docs/productization/PRISMA_LICENSE_OPERATION_MATRIX.md
docs/productization/PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D.md
docs/productization/PRISMA_LICENSE_SERVER_SIGNING_SCAN_POLICY_11D_ACCEPTANCE.md
docs/productization/PRISMA_NO_PAYMENT_PROCESSING_BOUNDARY.md
```

### 5.2 Runtime local de desarrollo

```text
local-runtime/license/
local-runtime/license-keys/dev/
local-runtime/license-server/
```

Uso esperado:

| Ruta | Uso |
|---|---|
| `local-runtime/license/` | licencias locales firmadas o fixtures dev |
| `local-runtime/license-keys/dev/` | material dev-local de firma/verificacion |
| `local-runtime/license-server/` | configuracion local del servidor de licencias |

### 5.3 Tooling de licencias

```text
tooling/licensing/
tooling/productization/examples/license-local/
tooling/productization/test-cases/
```

Uso esperado:

| Ruta | Uso |
|---|---|
| `tooling/licensing/` | motores, escaneos, smokes y fixtures de seguridad |
| `tooling/productization/examples/license-local/` | ejemplos de licencias locales por estado/plan |
| `tooling/productization/test-cases/` | casos de contrato para productizacion |

---

## 6. Modelo minimo de licencia

Este es el modelo recomendado para pensar el payload. No obliga a que todos los campos ya existan en codigo, pero evita que el sistema crezca como sopa recalentada.

```json
{
  "licenseId": "lic_001",
  "customerId": "cus_001",
  "businessId": "biz_001",
  "deviceId": "dev_tablet_001",
  "terminalId": "tablet_caja_01",
  "plan": "TABLET_PRO",
  "state": "active",
  "validFrom": "2026-04-29T00:00:00.000Z",
  "validUntil": "2026-05-29T00:00:00.000Z",
  "offlineGraceDays": 7,
  "limits": {
    "terminals": 2,
    "branches": 1
  },
  "features": {
    "pos.sales.complete": true,
    "pos.ticket.local": true,
    "inventory.local.decrement": true,
    "report.today.basic": true,
    "export.local.basic": true,
    "pos.returns.create": true,
    "shift.open": true,
    "shift.close": true,
    "event.outbox.view": true
  },
  "signature": "base64url:...",
  "keyId": "prod-2026-01",
  "signatureAlgorithm": "ed25519",
  "schemaVersion": "license.v1"
}
```

### 6.1 Campos que no deben faltar

| Campo | Por que importa |
|---|---|
| `licenseId` | identifica la licencia y permite auditoria |
| `customerId` | liga la licencia al cliente comercial |
| `businessId` | evita usar licencia de otro negocio |
| `deviceId` / `terminalId` | amarra activacion al dispositivo/terminal |
| `plan` | define paquete comercial |
| `state` | define comportamiento operativo |
| `validFrom` / `validUntil` | define vigencia |
| `offlineGraceDays` | evita bloqueo brutal por falta de red |
| `limits` | controla terminales, sucursales y crecimiento |
| `features` | prende/apaga capacidades reales |
| `signature` | evita alteracion del payload |
| `keyId` | permite rotacion de llaves |
| `signatureAlgorithm` | evita ambiguedad de verificacion |
| `schemaVersion` | permite migrar sin romper |

---

## 7. Estados de licencia

### 7.1 Estados canonicos

```text
dev
trial
active
offline_grace
past_due_external
suspended
expired
revoked
```

### 7.2 Comportamiento por estado

| Estado | Venta local basica | Premium/plugins | Exportacion | Soporte | UX esperada |
|---|---:|---:|---:|---:|---|
| `dev` | si | si | si | si | marca visible de dev |
| `trial` | si | si | si | si | aviso de trial/vencimiento |
| `active` | si | si | si | si | normal |
| `offline_grace` | si | no o limitado | si | si | banner discreto a admin |
| `past_due_external` | si | no o limitado | si | si | aviso administrativo |
| `suspended` | limitada | no | si | si | aviso persistente |
| `expired` | limitada tras grace | no | si | si | aviso de vencimiento |
| `revoked` | limitada o bloqueo gradual | no | si | si | aviso critico |

### 7.3 Regla de oro de suspensiones

```text
Suspender no es secuestrar.
```

Si el cliente tiene problema administrativo:

- no borrar datos;
- permitir exportar;
- permitir respaldo;
- permitir soporte;
- bloquear primero features premium;
- auditar el cambio;
- aplicar grace cuando corresponda.

---

## 8. Feature keys y entitlements

### 8.1 Convencion

```text
dominio.modulo.accion
```

Ejemplos:

```text
pos.sales.complete
pos.returns.create
inventory.local.adjust
dashboard.kpis
sync.managed
plugin.remote.activate
support.remote
ai.support.readonly.future
```

### 8.2 Reglas para no hacer un chilaquil

- No usar labels visibles como keys.
- No usar nombres de botones como contrato.
- No usar `isPro`, `isPremium`, `canDoMagic` ni inventos del compadre.
- No meter precios en keys.
- No usar keys por cliente.
- No duplicar reglas en cada componente.
- Las keys son contrato tecnico: cambian poco y se migran con cuidado.

### 8.3 Planes a features

| Plan | Features base |
|---|---|
| `TABLET_SOLO` | `pos.sales.complete`, `pos.ticket.local`, `inventory.local.decrement`, `report.today.basic`, `export.local.basic`, `support.basic` |
| `TABLET_PRO` | todo Solo + `pos.returns.create`, `pos.sale.cancel`, `shift.open`, `shift.close`, `inventory.local.adjust`, `event.outbox.view`, `export.local.advanced`, `backup.local.scheduled` |
| `PC_BACKOFFICE` | `catalog.write`, `inventory.backoffice.view`, `inventory.backoffice.adjust`, `purchase.write`, `receiving.write`, `audit.view`, `dashboard.kpis`, `sync.ingest`, `support.advanced` |
| `TABLET_PC_MANAGED` | `managed.devices`, `sync.managed`, `sync.conflict.resolve`, `catalog.snapshot.publish`, `license.remote.refresh`, `plugin.remote.activate`, `support.remote` |

---

## 9. Activacion de dispositivo

### 9.1 Que debe ligar una activacion

Una activacion debe ligar:

```text
customerId
businessId
licenseId
deviceId
terminalId
installationFingerprint
plan
status
activatedAt
lastSeenAt
```

### 9.2 Fingerprint recomendado

```text
sha256(machine-guid + app-install-id + terminal-id + business-id)
```

Reglas:

- no depender de `cwd`;
- no depender de rutas temporales;
- no usar datos personales innecesarios;
- crear `app-install-id` una vez y persistirlo;
- auditar resets de dispositivo.

### 9.3 Estados de dispositivo

```text
pending
active
suspended
revoked
replaced
```

### 9.4 Reset controlado

Un reset debe registrar:

```text
actorId
reason
previousDeviceId
newDeviceId
businessId
licenseId
occurredAt
```

No debe existir “reset porque me dio hueva”, ese deporte nacional de soporte sin bitacora.

---

## 10. Offline grace

### 10.1 Regla central

```text
Falla de internet no debe detener venta local basica inmediatamente.
```

### 10.2 Comportamiento esperado

Cuando no hay servidor:

1. Runtime usa la ultima licencia local valida.
2. Verifica firma y vigencia local.
3. Si el refresh remoto falla, entra a `offline_grace` si aplica.
4. Mantiene venta local basica.
5. Limita features premium/sensibles si la politica lo indica.
6. Muestra banner claro al admin/owner.
7. Registra evento administrativo.
8. Reintenta refresh cuando vuelva conexion.

### 10.3 Que no se debe hacer

- bloquear venta basica de golpe por timeout;
- borrar licencia local por no contactar servidor;
- ocultar que se esta en grace;
- permitir cambios sensibles sin marca offline;
- dejar errores mudos;
- depender de PC para vender.

---

## 11. Seguridad de firma

### 11.1 Modelo correcto

```text
Servidor firma.
Cliente verifica.
```

El servidor puede tener material privado productivo. El cliente no.

### 11.2 Dev vs production

| Entorno | Permitido | Prohibido |
|---|---|---|
| Dev local | material dev-local controlado, fixtures aprobados | simular que dev es production |
| Production | firma con llaves productivas fuera del repo | llaves privadas productivas commiteadas |
| Repo | fixtures aprobados y escaneados | PEM privado real en codigo/config/runtime |

### 11.3 Regla 11D

Un bloque PEM privado solo se permite si:

1. esta bajo `tooling/licensing/`;
2. pertenece a fixtures/regression/tamper/corpus aprobados;
3. coincide con la allowlist `tooling/licensing/server11d/repo_secret_scan_policy_11d.json`.

Todo lo demas bloquea.

### 11.4 Smokes indispensables

El smoke de firma debe probar:

- config local presente;
- no hay PEM privado real fuera de fixtures aprobados;
- firma local dev funciona;
- verificacion valida funciona;
- tamper de payload se rechaza;
- tamper de firma se rechaza;
- keyId incorrecto se rechaza;
- production se niega a firmar con material dev.

---

## 12. No Payment Processing Boundary

PRISMA no procesa pagos bancarios en esta etapa.

No hace:

```text
card processing
bank transfer initiation
SPEI validation
wallet integration
payment gateway settlement
chargebacks
PCI scope
KYC
custody of funds
bank reconciliation automation
```

Si la licencia habilita algo comercial, eso ocurre fuera de PRISMA o se refleja como entitlement. PRISMA puede registrar pagos manuales operativos, pero no mueve dinero ni valida bancos.

Dicho como taqueria legal: PRISMA anota que te pagaron en efectivo; no se vuelve banco, no se pone traje y no empieza a custodiar lana ajena.

---

## 13. UX esperada

### 13.1 Pantallas minimas

Tablet y PC deben poder mostrar:

```text
/settings/license
/api/license/status
/api/license/features
/api/license/refresh/status
```

### 13.2 Informacion visible minima

La pantalla de licencia debe mostrar:

- plan actual;
- estado actual;
- vigencia;
- negocio/sucursal;
- terminal/dispositivo;
- modo online/offline/grace;
- features principales habilitadas;
- ultima validacion/refresh;
- acciones permitidas para soporte/admin.

### 13.3 Mensajes segun estado

| Estado | Mensaje recomendado |
|---|---|
| `active` | Licencia activa. Operacion normal. |
| `offline_grace` | Sin conexion con servidor. Venta local basica disponible temporalmente. |
| `past_due_external` | Hay pendiente administrativo. Algunas funciones premium pueden estar limitadas. |
| `suspended` | Licencia suspendida. Exportacion y soporte disponibles. |
| `expired` | Licencia vencida. Renueva para recuperar funciones completas. |
| `revoked` | Licencia revocada. Contacta soporte. Exportacion y respaldo disponibles segun politica. |
| `signature_invalid` | La licencia fue alterada o no es confiable. Operacion bloqueada segun politica de seguridad. |

---

## 14. Auditoria obligatoria

Toda accion sensible debe dejar evento.

### 14.1 Eventos minimos

```text
license.created
license.renewed
license.suspended
license.reactivated
license.revoked
license.refreshed
license.refresh.failed
license.signature.invalid
license.offline_grace.entered
license.offline_grace.exited
device.activated
device.suspended
device.revoked
device.replaced
plan.upgraded
plan.downgraded
feature.denied
```

### 14.2 Payload minimo de auditoria

```json
{
  "eventId": "evt_001",
  "topic": "license.refreshed",
  "customerId": "cus_001",
  "businessId": "biz_001",
  "licenseId": "lic_001",
  "deviceId": "dev_tablet_001",
  "actorId": "system",
  "source": "tablet-runtime",
  "occurredAt": "2026-04-29T00:00:00.000Z",
  "schemaVersion": "license-event.v1",
  "payload": {}
}
```

---

## 15. Implementacion recomendada por etapas

### Etapa A - Canon local estable

Objetivo: que Tablet/PC lean licencia local firmada y calculen estado/features sin depender de servidor live.

Debe incluir:

- lector de licencia local;
- verificador de firma;
- parser de estado;
- calculo de features;
- endpoints `/api/license/status` y `/api/license/features`;
- UI `/settings/license`;
- fixtures activos, suspendidos, vencidos, revoked y tampered;
- tests de tampering.

### Etapa B - Activacion y refresh remoto

Objetivo: que el cliente pueda activar terminal y refrescar licencia.

Debe incluir:

- endpoint servidor de activacion;
- generacion de fingerprint;
- control de limite de dispositivos;
- refresh firmado;
- manejo de offline grace;
- auditoria de activacion y refresh.

### Etapa C - Portal admin MVP

Objetivo: operar clientes y licencias sin editar JSON a mano.

Debe incluir:

- clientes;
- negocios;
- licencias;
- dispositivos;
- renovaciones;
- suspensiones/revocaciones;
- auditoria;
- descarga de licencia firmada;
- confirmaciones en acciones criticas.

### Etapa D - Hardening production

Objetivo: preparar seguridad real.

Debe incluir:

- llaves productivas fuera del repo;
- rotacion de `keyId`;
- scanner de secretos como gate;
- rechazo de material dev en production;
- logs y reportes;
- pruebas de regression;
- runbook de soporte.

---

## 16. Decisiones que no se deben romper

1. Tablet vende sola.
2. PC no es permiso para vender.
3. La licencia local permite continuidad.
4. Internet caido no bloquea venta basica inmediatamente.
5. Firma invalida si es bloqueo duro.
6. Suspender no borra datos.
7. Exportacion y soporte sobreviven a estados administrativos.
8. Features se controlan por keys, no por labels.
9. Llaves privadas productivas no viven en repo.
10. PRISMA no procesa pagos bancarios.
11. Todo cambio sensible deja auditoria.
12. Todo paquete debe tener dry-run, apply, verify, rollback y log.

---

## 17. Checklist antes de tocar codigo de licencias

Antes de implementar algo, responde:

```text
1. Que plan o entitlement toca?
2. Afecta Tablet, PC o ambos?
3. Afecta venta basica local?
4. Que pasa offline?
5. Que pasa si la firma falla?
6. Que pasa si la licencia vence?
7. Que pasa si se suspende?
8. Permite exportar/respaldo/soporte?
9. Que evento de auditoria genera?
10. Que smoke prueba el cambio?
11. Donde queda documentado?
12. Tiene rollback?
```

Si no puedes contestar eso, no implementes. Estarias programando como quien arma mueble sin leer instrucciones y luego le sobran tornillos “porque seguro eran extra”.

---

## 18. Checklist de acceptance

Una entrega de licencias se acepta solo si:

- `--dry-run` muestra que cambiara;
- `--apply` instala controlado;
- `--verify` prueba archivos y comportamiento;
- `--rollback` puede regresar;
- deja log unico en `F:\descargasf`;
- no depende del directorio actual;
- no mete secretos productivos al repo;
- no rompe venta local basica;
- no toca PC/Tablet fuera del alcance declarado;
- documenta features afectadas;
- documenta estados de licencia afectados;
- prueba tamper si toca firma;
- prueba offline grace si toca refresh/conectividad;
- prueba denegacion de feature si toca entitlements.

---

## 19. Comandos utiles

### 19.1 Smoke de firma 11D

```powershell
F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd license-server-signing-smoke
```

### 19.2 Audit de fixtures 11D

```powershell
F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd license-server-signing-fixture-audit
```

### 19.3 Operacion historica de licencias

Puede existir launcher dedicado:

```powershell
F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta_license_ops.cmd --full-check --ensure-running
```

Si el launcher fue reubicado por limpieza de raiz, buscar en:

```text
tools/launchers/
```

---

## 20. Glosario corto

| Termino | Significado |
|---|---|
| License | documento firmado que habilita plan/features |
| Entitlement | permiso tecnico granular para una capacidad |
| Feature key | nombre estable de una capacidad |
| Plan | paquete comercial que agrupa entitlements |
| Device activation | amarre entre licencia y dispositivo/terminal |
| Fingerprint | huella tecnica estable del dispositivo/instalacion |
| Offline grace | periodo de continuidad sin refresh remoto |
| Refresh | renovacion/validacion remota de licencia local |
| Tamper | alteracion del payload o firma |
| keyId | identificador de llave publica/privada usada para firma |
| Signed license | licencia con firma verificable |
| Local store | ruta donde vive la licencia del cliente |
| Revoked | estado de revocacion fuerte |
| Suspended | estado administrativo limitado, no borrado de datos |

---

## 21. Resumen de una pagina

```text
Cliente compra plan.
Admin crea cliente/negocio/licencia.
Servidor firma licencia.
Dispositivo se activa.
Tablet/PC guarda licencia local.
Runtime valida firma y estado.
Feature gates habilitan capacidades.
Si no hay internet, aplica offline grace.
Si hay suspension, se limitan premium pero no se secuestran datos.
Si hay firma invalida, bloqueo duro segun politica.
Todo cambio sensible deja auditoria.
PRISMA no procesa pagos bancarios.
Tablet no depende de PC para vender localmente.
```

En corto: licencias son control comercial y tecnico, no una pistola en la sien de la operacion. Si una tiendita no puede vender porque se cayo internet diez minutos, el sistema fallo. Si una licencia alterada pasa como valida, tambien fallo. El punto es equilibrio: continuidad sin ingenuidad, seguridad sin ponerse payaso.

---

## 22. Orden recomendado para siguientes entregas

1. Consolidar este README como indice canonico.
2. Limpiar docs obsoletos de licencias viejas y moverlos a `F:\Trash-old` si ya no son fuente viva.
3. Crear `license-contract.index.json` con rutas canonicas y estado de cada doc.
4. Implementar o verificar endpoints `/api/license/status` y `/api/license/features` en Tablet/PC.
5. Formalizar `license.remote.refresh` y offline grace con pruebas.
6. Construir portal/admin MVP si el producto ya necesita operacion comercial real.

---

## 23. Nota final para futuros cambios

Cada vez que alguien quiera tocar licencias, este README debe funcionar como torniquete de sentido comun.

Si el cambio:

- bloquea venta local basica sin grace;
- mete secreto al repo;
- borra datos por suspension;
- procesa pagos bancarios;
- duplica feature rules en UI;
- depende de PC para vender;
- no deja audit trail;

entonces se rechaza. Sin drama. Como antro decente: no entra porque viene con tenis del caos.
