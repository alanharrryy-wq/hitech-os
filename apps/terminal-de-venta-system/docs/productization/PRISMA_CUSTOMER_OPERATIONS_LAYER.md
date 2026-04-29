# PRISMA_CUSTOMER_OPERATIONS_LAYER

**Documento:** `PRISMA_CUSTOMER_OPERATIONS_LAYER.md`  
**Proyecto:** PRISMA Terminal de Venta  
**Area:** Productizacion / Operacion cliente / Remote Ops  
**Estado:** especificacion fundacional  
**Version:** `0.1.0`  
**Idioma visible:** `es-MX`  
**Ruta sugerida en repo:** `docs/productization/PRISMA_CUSTOMER_OPERATIONS_LAYER.md`

---

## 0. Frase madre

**PRISMA debe funcionar localmente para vender, pero debe poder administrarse remotamente para licencias, soporte, comunicacion, novedades, actualizaciones y plugins, sin procesar pagos bancarios dentro del sistema.**

En corto:

```text
PRISMA vende local.
PRISMA se administra remoto.
PRISMA no procesa pagos bancarios.
PRISMA comunica cliente-proveedor.
PRISMA permite plugins.
PRISMA prepara IA sin meterla al corazon de caja.
```

---

## 1. Proposito del documento

Este documento define la capa de operacion cliente de PRISMA desde la perspectiva de un cliente que ya compro, instalo y usa el sistema.

La meta no es describir solo como se desarrolla PRISMA, sino como se mantiene vivo en operacion real:

- activacion y desactivacion remota de licencias;
- habilitacion de funciones por plan;
- canal de comunicacion entre cliente y proveedor;
- soporte tecnico desde Tablet y PC;
- anuncios y novedades dentro de las apps;
- solicitud de plugins o caracteristicas extra;
- actualizaciones remotas controladas;
- diagnosticos de soporte;
- preparacion para IA futura;
- cero procesamiento de pagos bancarios dentro de PRISMA.

Este documento se usara como base para construir la capa tecnica futura sin romper la regla principal del producto:

> Tablet vende sola. PC gobierna cuando existe. Remote Ops administra, soporta y extiende, pero no debe bloquear la venta local basica.

---

## 2. Decision canonica

PRISMA no debe ser solamente:

```text
Tablet POS + PC Backoffice
```

Debe evolucionar hacia:

```text
Producto local-first administrable remotamente
```

Eso significa:

1. **La operacion critica vive localmente.**
   - ventas;
   - tickets;
   - stock local;
   - eventos;
   - outbox;
   - exportacion;
   - backups;
   - modo offline.

2. **La administracion extendida puede ser remota.**
   - licencia;
   - planes;
   - plugins;
   - soporte;
   - novedades;
   - actualizaciones;
   - diagnosticos;
   - futura IA.

3. **Remote Ops no debe ser dependencia dura para vender.**
   - si no hay internet, Tablet debe seguir vendiendo dentro de sus reglas locales;
   - si Remote Ops cae, el negocio no se detiene;
   - si hay licencia pendiente de refrescar, debe existir periodo de gracia;
   - si hay update pendiente, la app no debe romper la caja.

---

## 3. No pagos bancarios dentro de PRISMA

### 3.1 Decision

PRISMA no debe procesar pagos bancarios, tarjetas, transferencias, SPEI, wallets ni pasarelas de pago.

Esta decision evita entrar por ahora en problemas regulatorios, conciliacion bancaria, chargebacks, datos financieros sensibles, custodia de dinero, certificaciones y obligaciones que no pertenecen al primer objetivo del producto.

### 3.2 PRISMA no debe integrar por ahora

```text
Stripe
Mercado Pago
Clip
OpenPay
terminales bancarias integradas
SPEI automatico
tarjetas
wallets
conciliacion bancaria automatica
procesamiento de transferencias
validacion bancaria
custodia de dinero
```

### 3.3 Lo que si puede hacer

PRISMA puede registrar de forma operativa un metodo de pago local si el negocio lo necesita para corte o ticket, por ejemplo:

```text
efectivo
pago externo confirmado manualmente
credito local
por cobrar
otro
```

Regla:

> PRISMA puede registrar que el operador marco una forma de pago, pero no debe iniciar, validar, liquidar ni custodiar el pago.

### 3.4 Upgrades y plugins sin pago interno

Cuando una caracteristica no este incluida en el plan del cliente, PRISMA puede mostrar:

```text
Esta funcion no esta incluida en tu plan actual.
Puedes solicitar activacion a soporte PRISMA.
```

Acciones permitidas:

```text
Ver detalles
Solicitar activacion
Contactar soporte
Cerrar
```

No debe existir boton:

```text
Pagar ahora
```

El acuerdo comercial, pago, contrato o autorizacion ocurre fuera de PRISMA. Luego el proveedor activa remotamente la licencia, entitlement o plugin correspondiente.

---

## 4. Principios de producto

## 4.1 Local-first

PRISMA debe operar localmente aun si no hay internet.

Tablet debe poder:

- abrir POS;
- cargar catalogo local;
- crear venta;
- cerrar ticket;
- descontar stock local;
- registrar movimiento;
- crear evento;
- guardar outbox;
- mostrar ventas del dia;
- exportar informacion local;
- operar offline dentro de sus politicas.

## 4.2 Remote-managed

Cuando haya conexion, PRISMA puede:

- refrescar licencia;
- recibir anuncios;
- recibir mensajes;
- abrir o actualizar tickets de soporte;
- enviar diagnosticos autorizados;
- revisar updates;
- descargar paquetes;
- habilitar plugins;
- reportar health;
- preparar contexto para soporte futuro con IA.

## 4.3 No dependencia dura de Remote Ops

Remote Ops puede mejorar, administrar y extender la experiencia, pero no debe ser requisito para la venta local basica.

Prohibido:

```text
No permitir cerrar venta solo porque no hay conexion con Remote Ops.
No pedir autorizacion remota para cada ticket.
No bloquear exportacion de datos del cliente por falta de internet.
No borrar ni secuestrar datos por suspension de licencia.
```

## 4.4 Consentimiento visible

El cliente debe ver y autorizar acciones sensibles:

- enviar diagnostico;
- iniciar soporte remoto;
- aplicar update mayor;
- instalar plugin;
- activar caracteristica nueva;
- compartir logs;
- adjuntar datos operativos a un ticket.

## 4.5 Auditoria

Toda accion sensible debe dejar rastro:

```text
quien
cuando
desde donde
sobre que negocio
sobre que dispositivo
accion solicitada
resultado
error si hubo
```

## 4.6 IA fuera del nucleo critico

La IA futura debe vivir en soporte, ayuda, analisis, configuracion guiada y recomendaciones, no en el motor transaccional de caja.

No debe decidir sola:

- totales de venta;
- descuento de stock;
- cierre de ticket;
- cambios de precio;
- ajustes de inventario;
- activacion de licencias;
- instalacion de plugins.

---

## 5. Arquitectura conceptual

```text
Cliente usando PRISMA
  Tablet POS
    vende local
    tickets
    stock local
    outbox
    soporte basico
    mensajes
    novedades controladas

  PC Backoffice
    catalogo
    inventario
    dashboard
    sync
    soporte avanzado
    plugins
    licencia
    mensajes
    novedades

  PRISMA Local Agent
    licencia local
    feature flags
    updates
    plugins
    diagnostics
    remote inbox
    health report

  Runtime local
    DBs
    config
    logs
    backups
    exports
    diagnostics
    support bundles

Proveedor PRISMA
  PRISMA Remote Ops
    clientes
    negocios
    dispositivos
    licencias
    planes
    entitlements
    plugins
    releases
    mensajes
    anuncios
    tickets de soporte
    diagnosticos
    futuras capacidades IA
```

---

## 6. Componentes principales

## 6.1 PRISMA Remote Ops

Panel o servicio del proveedor para operar clientes instalados.

Responsabilidades:

- registrar clientes;
- registrar negocios;
- registrar dispositivos;
- emitir licencias;
- activar o desactivar licencias;
- cambiar planes;
- habilitar entitlements;
- publicar anuncios;
- responder mensajes;
- administrar tickets de soporte;
- publicar releases;
- publicar plugins;
- revisar health reports;
- recibir diagnosticos;
- preparar capa de IA futura.

Remote Ops no debe ser una consola para ejecutar comandos arbitrarios en maquinas cliente.

## 6.2 PRISMA Local Agent

Componente instalado en el entorno del cliente.

Puede implementarse por fases como:

1. modulo interno dentro de PC Backoffice;
2. proceso local lanzado por la app;
3. tray app;
4. Windows service;
5. agente separado formal.

Responsabilidades:

- guardar licencia local;
- refrescar licencia cuando haya conexion;
- aplicar feature flags;
- recibir anuncios;
- sincronizar mensajes;
- generar diagnosticos;
- revisar updates;
- instalar plugins autorizados;
- validar firmas/checksums;
- ejecutar acciones remotas permitidas;
- reportar health.

## 6.3 Centro PRISMA

Nombre visible recomendado para el cliente.

En Tablet:

```text
Centro PRISMA
  Estado
  Soporte
  Mensajes
  Novedades
  Exportar diagnostico
```

En PC:

```text
Centro PRISMA
  Mi plan
  Licencia
  Plugins
  Novedades
  Soporte
  Mensajes
  Actualizaciones
  Diagnostico
  Dispositivos
```

La idea es que el cliente tenga una ventanilla clara para comunicarse, recibir ayuda, ver su plan y gestionar funciones sin tener que entender la maquinaria interna.

---

## 7. Licencias y entitlements

## 7.1 Licencia

La licencia representa el derecho general de uso para un negocio, cliente o dispositivo.

Archivo local sugerido:

```text
C:\ProgramData\PRISMA\config\license.json
```

Ejemplo conceptual:

```json
{
  "licenseId": "lic_123",
  "customerId": "cus_abc",
  "businessId": "biz_abc",
  "plan": "TABLET_PRO",
  "status": "active",
  "features": [
    "pos.sales",
    "pos.returns",
    "shifts",
    "exports.advanced",
    "support.channel"
  ],
  "plugins": [
    "promotions.basic"
  ],
  "validUntil": "2026-12-31",
  "offlineGraceUntil": "2027-01-15",
  "lastRemoteCheckAt": "2026-04-28T12:00:00Z",
  "signature": "..."
}
```

## 7.2 Estados de licencia

| Estado | Significado |
|---|---|
| `dev` | uso de desarrollo |
| `trial` | prueba temporal |
| `active` | licencia activa |
| `offline_grace` | no se pudo validar remoto, pero puede seguir operando temporalmente |
| `past_due_external` | pendiente administrativo externo |
| `suspended` | suspendida remotamente |
| `revoked` | revocada |
| `expired` | vencida |

## 7.3 Entitlements

Los entitlements habilitan funciones especificas.

Ejemplos:

```text
pos.sales
pos.returns
shift.open_close
exports.basic
exports.advanced
inventory.local_adjust
inventory.advanced
dashboard.kpis
sync.managed
plugins.promotions
support.channel
support.remote_diagnostics
ai.support.readonly.future
```

Cada feature debe poder resolverse asi:

```json
{
  "featureKey": "pos.returns",
  "enabled": true,
  "source": "license",
  "expiresAt": null
}
```

## 7.4 Desactivacion remota

La desactivacion remota debe ser gradual y segura.

Reglas recomendadas:

- avisar antes de bloquear;
- respetar grace offline;
- permitir exportar datos;
- permitir backups;
- permitir soporte;
- bloquear primero funciones premium;
- evitar secuestro de datos;
- no borrar informacion del cliente.

| Funcion | Suspencion leve | Suspencion fuerte |
|---|---:|---:|
| venta local basica | permitir temporalmente | eventualmente bloquear nuevas ventas segun politica, sin borrar datos |
| exportacion | permitir | permitir |
| backups | permitir | permitir |
| soporte | permitir | permitir |
| plugins premium | bloquear | bloquear |
| dashboard avanzado | bloquear | bloquear |
| multi-sucursal | bloquear | bloquear |

---

## 8. Planes comerciales

## 8.1 TABLET_SOLO

Incluye:

- POS standalone;
- ventas locales;
- tickets;
- stock local;
- reporte del dia;
- exportacion basica;
- soporte basico;
- licencia local;
- mensajes y novedades controladas.

No requiere PC.

## 8.2 TABLET_PRO

Incluye todo TABLET_SOLO, mas:

- devoluciones/cancelaciones;
- turnos/cortes;
- ajustes locales controlados;
- export avanzado;
- outbox visible;
- backups programados;
- plugins operativos permitidos;
- soporte con diagnostico.

## 8.3 PC_BACKOFFICE

Incluye:

- catalogo avanzado;
- inventario;
- compras;
- recepcion;
- reabasto;
- auditoria;
- dashboard;
- sync ingest si aplica;
- Centro PRISMA completo;
- gestion de plugins;
- updates;
- soporte avanzado.

## 8.4 TABLET_PC_MANAGED

Incluye:

- Tablet POS local;
- PC Backoffice;
- sync local/LAN;
- snapshots de catalogo;
- reconciliacion;
- conflictos;
- dispositivos administrados;
- Remote Ops conectado;
- plugins por negocio/dispositivo;
- soporte y diagnostico avanzado.

Regla:

> En modo managed, Tablet sigue vendiendo aunque PC o red caigan, dentro de las politicas locales.

---

## 9. Canal de comunicacion cliente-proveedor

## 9.1 Objetivo

Permitir comunicacion dentro de Tablet y PC entre el cliente y el proveedor PRISMA.

Casos de uso:

- soporte tecnico;
- dudas de uso;
- solicitud de plugin;
- solicitud de activacion;
- avisos administrativos;
- capacitacion;
- seguimiento de bugs;
- respuesta a diagnosticos;
- preparacion para IA futura.

## 9.2 Tipos de mensaje

```text
support
license
plugin_request
announcement_reply
training
bug_report
feature_request
admin_external
```

## 9.3 Esquema conceptual de mensaje

```json
{
  "messageId": "msg_123",
  "threadId": "thr_123",
  "businessId": "biz_abc",
  "deviceId": "dev_tablet_01",
  "channel": "support",
  "senderType": "customer",
  "senderRole": "owner",
  "body": "No puedo exportar ventas del dia.",
  "category": "support",
  "contextRefs": [
    "diagnostic_bundle:diag_123"
  ],
  "attachments": [],
  "createdAt": "2026-04-28T12:00:00Z"
}
```

## 9.4 Reglas

- Tablet no debe interrumpir ventas por mensajes normales;
- PC puede mostrar comunicacion completa;
- mensajes criticos deben respetar roles;
- adjuntos deben ser controlados;
- diagnosticos requieren consentimiento;
- todo soporte debe ser auditable.

---

## 10. Soporte y tickets

## 10.1 Ticket de soporte

```json
{
  "ticketId": "tic_123",
  "businessId": "biz_abc",
  "deviceId": "dev_pc_01",
  "category": "support",
  "priority": "normal",
  "status": "open",
  "subject": "Error al exportar ventas",
  "diagnosticBundleIds": ["diag_123"],
  "createdAt": "2026-04-28T12:00:00Z",
  "updatedAt": "2026-04-28T12:00:00Z"
}
```

## 10.2 Estados

```text
open
waiting_customer
waiting_provider
in_progress
resolved
closed
```

## 10.3 Categorias

```text
soporte_tecnico
licencia
plugin
actualizacion
capacitacion
bug
sugerencia
facturacion_externa
```

`facturacion_externa` no significa pagos dentro de PRISMA. Solo comunicacion administrativa.

---

## 11. Diagnosticos de soporte

## 11.1 Support bundle

PRISMA debe poder generar:

```text
support-bundle.zip
```

Debe incluir, segun permiso:

- version instalada;
- package type;
- estado de licencia;
- rutas runtime;
- sistema operativo;
- espacio en disco;
- estado DB;
- estado outbox;
- estado sync;
- plugins activos;
- ultimos errores;
- logs recientes;
- manifest instalado;
- resultado de verificaciones.

No debe incluir por defecto:

- contrasenas;
- tokens;
- secretos;
- datos bancarios;
- ventas completas;
- informacion sensible innecesaria;
- archivos fuera de PRISMA.

## 11.2 Consentimiento

Antes de enviar diagnostico:

```text
Deseas enviar diagnostico tecnico a soporte PRISMA?
Incluye version, logs recientes, estado de sync, plugins y errores recientes.
No incluye contrasenas ni datos bancarios.
```

---

## 12. Announcements, novedades y popups

## 12.1 Objetivo

Enviar avisos al cliente dentro de Tablet y PC.

Tipos:

- novedades;
- nuevas funciones;
- mejoras incluidas;
- funciones disponibles para solicitar;
- mantenimiento programado;
- advertencias de licencia;
- updates disponibles;
- capacitacion;
- incidentes tecnicos.

## 12.2 Severidad

| Severidad | UI recomendada |
|---|---|
| `info` | card o badge |
| `notice` | banner suave |
| `warning` | banner persistente |
| `critical` | modal solo si requiere accion |
| `commercial` | centro de novedades, no interrumpir venta |

## 12.3 Reglas de interrupcion

- No mostrar popup comercial durante checkout.
- No interrumpir una venta por anuncio normal.
- Los avisos comerciales deben ir a Novedades o Plugins.
- Los avisos criticos deben respetar rol y contexto.
- El cajero ve lo minimo.
- El dueño/admin ve licencia, plugins y upgrades.

## 12.4 Esquema conceptual

```json
{
  "announcementId": "ann_123",
  "title": "Nuevo modulo de promociones disponible",
  "body": "Puedes solicitar la activacion del modulo de promociones para crear combos y descuentos controlados.",
  "severity": "commercial",
  "targetPlans": ["TABLET_PRO", "TABLET_PC_MANAGED"],
  "targetRoles": ["owner", "admin"],
  "targetVersions": [">=1.0.0"],
  "showFrom": "2026-05-01T00:00:00Z",
  "showUntil": "2026-06-01T00:00:00Z",
  "dismissible": true,
  "showOnce": true,
  "ctaType": "request_activation",
  "ctaTarget": "plugin:promotions.basic"
}
```

---

## 13. Plugin Catalog

## 13.1 Objetivo

Permitir que PRISMA pueda crecer por modulos activables sin convertir cada instalacion en un Frankenstein con botas.

Ejemplos de plugins futuros:

| Plugin | Tipo |
|---|---|
| promociones basicas | comercial |
| fidelidad | comercial |
| reportes avanzados | backoffice |
| multi-sucursal | expansion |
| bascula | hardware |
| impresora especifica | hardware |
| alertas de merma | control |
| inventario avanzado | operacion |
| soporte IA | futuro |
| asistente de catalogo IA | futuro |

## 13.2 Manifest de plugin

```json
{
  "pluginId": "promotions.basic",
  "name": "Promociones basicas",
  "version": "1.0.0",
  "compatiblePrismaVersions": [">=1.0.0 <2.0.0"],
  "requiredPlan": ["TABLET_PRO", "TABLET_PC_MANAGED"],
  "permissions": [
    "catalog.read",
    "sales.read",
    "promotions.write"
  ],
  "runtimeSurfaces": [
    "pc.plugins",
    "tablet.pos.banner"
  ],
  "dbMigrations": [],
  "events": [
    "plugin.enabled",
    "promotion.created",
    "promotion.applied"
  ],
  "rollbackPlan": {
    "disableFirst": true,
    "dataDestructive": false
  },
  "signature": "..."
}
```

## 13.3 Permisos de plugin

Ejemplos:

```text
catalog.read
catalog.write
sales.read
sales.write
inventory.read
inventory.adjust
reports.create
sync.emit
device.access
support.context.read
```

Regla:

> Plugin que toca dinero, stock, ventas, permisos o auditoria debe generar evento y ser auditable.

## 13.4 Instalacion de plugin

Flujo recomendado:

```text
1. Validar licencia
2. Validar entitlement
3. Validar compatibilidad
4. Validar firma/checksum
5. Crear backup
6. Instalar en staging
7. Aplicar migracion si existe
8. Ejecutar verify
9. Activar plugin
10. Registrar evento
11. Permitir rollback o disable
```

## 13.5 Desinstalacion

Primero debe existir:

```text
disable
```

No todos los plugins deben borrarse fisicamente de inmediato, especialmente si generaron datos. Desactivar suele ser mas seguro que destruir.

---

## 14. Updates remotos

## 14.1 Objetivo

Permitir actualizaciones controladas, con backup, verify y rollback.

## 14.2 Canales

| Canal | Uso |
|---|---|
| `stable` | clientes normales |
| `pilot` | clientes piloto |
| `hotfix` | correcciones urgentes |
| `internal` | desarrollo/proveedor |

## 14.3 Flujo de update

```text
1. Remote Ops publica release
2. Local Agent detecta update
3. Descarga paquete firmado
4. Verifica firma/checksum
5. Revisa compatibilidad
6. Revisa licencia/plan
7. Revisa si hay venta o turno critico abierto
8. Crea backup
9. Instala en staging
10. Aplica migraciones
11. Ejecuta verify
12. Cambia version activa
13. Si falla, rollback automatico
14. Registra resultado
```

## 14.4 Reglas

- No actualizar durante una venta abierta.
- Evitar update silencioso destructivo.
- Updates mayores deben pedir confirmacion de admin.
- Hotfixes pueden tener flujo mas rapido, pero siempre con verify y rollback.
- Todo update debe dejar log.

---

## 15. Remote commands seguros

## 15.1 Permitidos

Remote Ops solo debe poder solicitar acciones predefinidas.

Ejemplos:

```text
CHECK_HEALTH
GENERATE_DIAGNOSTIC_BUNDLE
REFRESH_LICENSE
CHECK_FOR_UPDATES
STAGE_UPDATE
APPLY_APPROVED_UPDATE
DISABLE_PLUGIN
ENABLE_PLUGIN
RETRY_SYNC
EXPORT_SUPPORT_SUMMARY
```

## 15.2 Prohibidos

```text
RUN_ARBITRARY_COMMAND
EXECUTE_POWERSHELL
DELETE_DATABASE
EDIT_FILE_RAW
UPLOAD_SECRET_FILES
DISABLE_AUDIT
BYPASS_LICENSE
```

Regla:

> No debe existir ejecucion remota arbitraria. Todo debe pasar por acciones conocidas, auditadas y limitadas.

---

## 16. Heartbeat y health report

## 16.1 Objetivo

Reportar salud tecnica sin mandar datos sensibles.

## 16.2 Ejemplo

```json
{
  "deviceId": "dev_123",
  "businessId": "biz_abc",
  "app": "tablet",
  "version": "1.0.0",
  "licenseStatus": "active",
  "syncStatus": "pending_events",
  "pendingOutboxCount": 32,
  "lastBackupAt": "2026-04-28T12:00:00Z",
  "diskFreeMb": 20480,
  "plugins": ["promotions.basic"],
  "errorsLast24h": 2,
  "createdAt": "2026-04-28T12:05:00Z"
}
```

## 16.3 No incluir

- ventas completas;
- tickets completos;
- datos personales innecesarios;
- secretos;
- tokens;
- datos bancarios.

---

## 17. APIs conceptuales futuras

Estas APIs son conceptuales. No implican implementacion inmediata.

```text
POST /api/devices/register
POST /api/devices/heartbeat
POST /api/licenses/refresh
GET  /api/announcements
GET  /api/messages
POST /api/messages
POST /api/support/tickets
POST /api/diagnostics/upload
GET  /api/releases/check
GET  /api/plugins/catalog
POST /api/plugins/request-activation
```

## 17.1 Modelo de conexion recomendado

Preferir que el cliente consulte periodicamente a Remote Ops:

```text
Local Agent -> Remote Ops: hay algo para mi?
Remote Ops -> Local Agent: mensajes, licencia, comandos permitidos, updates
```

Evitar abrir puertos entrantes en la red del cliente en primeras fases.

---

## 18. IA futura

## 18.1 Decision

La IA debe prepararse desde la estructura, no meterse de golpe al nucleo de caja.

Debe iniciar como:

```text
read-only assistant
```

Luego evolucionar a:

```text
suggest actions
```

Y solo mucho despues:

```text
execute approved actions
```

## 18.2 Casos buenos para IA

Soporte:

- explicar errores;
- resumir diagnosticos;
- sugerir pasos;
- preparar respuestas;
- clasificar tickets;
- detectar patrones de fallas.

Operacion:

- resumen del dia;
- productos mas vendidos;
- productos bajos;
- reabasto sugerido;
- productos sin barcode;
- precios posiblemente viejos;
- ventas inusuales;
- movimientos raros.

## 18.3 Casos prohibidos al inicio

La IA no debe:

- cerrar ventas;
- modificar totales;
- descontar stock por decision propia;
- borrar datos;
- cambiar precios sola;
- instalar plugins sola;
- suspender licencias sola;
- ejecutar comandos remotos;
- modificar inventario sin confirmacion.

## 18.4 Preparacion tecnica desde ahora

Crear datos estructurados para:

- mensajes;
- tickets;
- diagnosticos;
- health reports;
- eventos;
- permisos;
- roles;
- contexto permitido.

---

## 19. UX cliente

## 19.1 Tablet

Tablet debe priorizar venta.

Navegacion sugerida:

```text
Ventas
Catalogo
Ventas de hoy
Stock bajo
Exportar
Centro PRISMA
```

Centro PRISMA en Tablet:

```text
Estado
Soporte
Mensajes
Novedades
Exportar diagnostico
```

Reglas:

- no interrumpir checkout por anuncios comerciales;
- mostrar badges en vez de modales cuando sea posible;
- solo errores criticos justifican bloqueo visual;
- cajero no debe ver configuracion compleja;
- dueño/admin ve plan, licencia y solicitudes.

## 19.2 PC Backoffice

PC puede tener administracion completa.

Navegacion sugerida:

```text
Dashboard
Catalogo
Inventario
Compras
Recepcion
Reabasto
Auditoria
Sync
Centro PRISMA
```

Centro PRISMA en PC:

```text
Mi plan
Licencia
Plugins
Novedades
Soporte
Mensajes
Actualizaciones
Diagnostico
Dispositivos
```

---

## 20. Rutas runtime recomendadas

```text
C:\ProgramData\PRISMA\
  config\
    runtime.json
    license.json
    devices.json
    paths.json
    sync.json

  businesses\
    <businessId>\
      business.json

      tablet\
        data\
        outbox\
        exports\
        backups\
        logs\
        diagnostics\

      pc\
        data\
        imports\
        exports\
        backups\
        logs\
        diagnostics\

      sync\
        inbox\
        outbox\
        archive\
        conflicts\

      shared\
        snapshots\
        contracts\
        audit\

  updates\
    downloads\
    staged\
    applied\

  rollback\
    snapshots\
    manifests\

  support\
    bundles\
```

Separacion:

- `Program Files`: app instalada / binarios / solo lectura normal;
- `ProgramData`: datos compartidos del negocio;
- `%LOCALAPPDATA%`: preferencias por usuario si aplica.

---

## 21. Seguridad y privacidad basica

## 21.1 Firmas y checksums

Deben validarse:

- licencias;
- updates;
- plugins;
- manifests;
- remote commands.

## 21.2 Minimizacion de datos

Recolectar solo lo necesario para soporte y operacion.

No recolectar por defecto:

- datos bancarios;
- contrasenas;
- tokens;
- documentos sensibles;
- ventas completas;
- informacion personal innecesaria.

## 21.3 Auditoria

Auditar:

- cambio de licencia;
- activacion de plugin;
- update;
- rollback;
- diagnostico enviado;
- soporte remoto;
- cambios de config;
- comandos remotos permitidos;
- errores criticos.

## 21.4 Roles

Roles sugeridos:

```text
cashier
supervisor
owner
admin
support
technician
```

No todos deben ver licencia, plugins, updates o mensajes administrativos.

---

## 22. Roadmap de implementacion

## Fase 0. Base local vendible

- Tablet standalone;
- PC backoffice;
- runtime separado;
- DB local;
- exports;
- backups;
- logs;
- no dependencia de repo.

## Fase 1. Licencia local basica

- `license.json` local;
- plan activo;
- features habilitadas;
- grace offline;
- pantalla Mi plan;
- mock local de licencia.

## Fase 2. Remote license refresh

- registro de dispositivo;
- refresh remoto de licencia;
- activacion/desactivacion de features;
- estado offline grace;
- auditoria de cambios.

## Fase 3. Customer communication channel

- mensajes en Tablet y PC;
- tickets de soporte;
- estados de ticket;
- respuestas;
- diagnostico adjunto manual.

## Fase 4. Announcements / popups

- novedades;
- banners;
- popups controlados;
- target por plan/rol/version;
- CTA solicitar activacion;
- sin pagos integrados.

## Fase 5. Plugin catalog local

- manifest de plugin;
- enable/disable;
- permisos;
- compatibilidad;
- rollback;
- instalacion local controlada.

## Fase 6. Remote plugin activation

- entitlement remoto;
- refresh local;
- instalacion por Local Agent;
- UI desbloqueada;
- auditoria.

## Fase 7. Support diagnostics

- support bundle;
- envio con permiso;
- health remoto;
- errores recientes;
- estado sync/outbox/backups.

## Fase 8. AI-ready support foundation

- mensajes estructurados;
- tickets categorizados;
- diagnosticos estructurados;
- contexto tecnico seguro;
- IA read-only futura.

---

## 23. Lo que no se debe construir todavia

No construir en esta etapa:

- pasarela de pagos;
- transferencias;
- facturacion fiscal;
- IA ejecutora;
- marketplace publico;
- plugin SDK abierto a terceros;
- control remoto libre tipo shell;
- actualizacion silenciosa destructiva;
- multi-tenant cloud gigante;
- chat en tiempo real complejo;
- cobro dentro de PRISMA.

---

## 24. Criterios de aceptacion futuros

Esta capa empieza a estar lista cuando:

- el cliente puede ver su plan;
- PRISMA puede resolver features por licencia;
- existe grace offline;
- Tablet no depende de Remote Ops para vender;
- PC muestra Centro PRISMA;
- el cliente puede crear ticket de soporte;
- se puede generar diagnostic bundle;
- anuncios se muestran sin interrumpir checkout;
- plugins tienen manifest y permisos;
- updates tienen backup, verify y rollback;
- remote commands estan limitados por allowlist;
- IA futura tiene canal estructurado, pero no controla caja.

---

## 25. Resumen ejecutivo

PRISMA debe crecer como un producto local-first con administracion remota segura.

La venta local vive en Tablet.

El gobierno operativo vive en PC cuando existe.

Remote Ops administra licencias, soporte, mensajes, novedades, updates y plugins.

El cliente puede comunicarse con el proveedor desde las apps.

El proveedor puede activar o desactivar licencias y funciones remotamente con grace y auditoria.

Las nuevas caracteristicas pueden anunciarse y solicitarse, pero no cobrarse dentro de PRISMA.

Los plugins deben instalarse con permisos, compatibilidad, backup, verify y rollback.

La IA futura debe entrar primero como soporte y ayuda read-only, no como motor que decide ventas o inventario.

Regla final:

```text
PRISMA puede estar conectado contigo.
PRISMA puede ser soportado por ti.
PRISMA puede recibir plugins tuyos.
PRISMA puede prepararse para IA.
Pero PRISMA no debe dejar de vender localmente por depender de ti.
```
