---
title: PRISMA Local-First Data Custody Contract
path: docs/productization/PRISMA_LOCAL_FIRST_DATA_CUSTODY_CONTRACT.md
project: PRISMA Terminal de Venta
status: productization-contract
state: SOURCE_READY
version: 1.0.0
visible_language: es-MX
scope:
  - tablet
  - pc
  - mobile
  - local-agent
  - remote-ops
  - licensing
  - diagnostics
managed_by: custodia
---

# PRISMA Local-First Data Custody Contract

## 1. Decisión canónica

PRISMA adopta un modelo **local-first con custodia operativa del cliente**.

Los datos operativos generados por el negocio deben permanecer, por defecto, en dispositivos, servidores, redes o cuentas de almacenamiento controladas por el propio cliente. El proveedor de PRISMA no recibe, aloja, replica, consulta ni conserva automáticamente las bases operativas del negocio.

```text
TENANT / NEGOCIO / TIENDA
        ↓
Equipo, servidor, NAS o almacenamiento controlado por el cliente
        ↓
Bases locales de Tablet, PC y componentes autorizados
        ↓
Procesamiento local de PRISMA
        ↓
Sin transmisión de datos operativos al proveedor por defecto
```

Este contrato define la arquitectura y la frontera del producto. No declara por sí solo que cada runtime ya pasó una certificación de red o de ausencia de egreso.

## 2. Clasificación de datos

### 2.1 Datos operativos del cliente

Permanecen bajo custodia y control del cliente:

- ventas, tickets y líneas de venta;
- inventario, catálogo y movimientos;
- clientes del comercio;
- empleados, cajeros, roles y turnos;
- proveedores;
- cortes y sesiones de caja;
- datos fiscales capturados por el negocio;
- auditoría operativa;
- outbox, eventos, evidencia y proyecciones canónicas;
- bases, respaldos, exports y adjuntos;
- logs que incluyan contexto operativo identificable.

### 2.2 Datos de relación comercial de PRISMA

El proveedor puede tratar únicamente los datos necesarios para su propia relación comercial y soporte, por ejemplo:

- nombre y contacto del comprador o administrador;
- datos necesarios para cotización, contratación y facturación del servicio;
- tickets de soporte creados por el contacto;
- historial de licencia, plan, renovación y atención;
- comunicaciones autorizadas.

Estos datos son distintos de la base operativa del negocio.

### 2.3 Metadatos técnicos mínimos de licencia

Remote Ops o License Gateway pueden recibir sólo metadatos mínimos y disociados cuando sean necesarios:

- `licenseId`;
- plan y entitlements;
- estado de licencia y grace;
- versión instalada;
- canal de actualización;
- identificador técnico de dispositivo;
- superficie declarada;
- timestamps de activación o heartbeat;
- estado técnico resumido sin payload operativo.

Un identificador técnico no debe incluir nombres de clientes finales, productos, ventas, RFC, teléfonos, correos de compradores ni contenido de tickets.

## 3. Frontera de custodia

### 3.1 Regla por defecto

```text
providerOperationalDataAccess = none_by_default
providerOperationalDataStorage = prohibited_by_default
providerOperationalDataReplication = prohibited_by_default
customerControlsEncryptionKeys = required_when_applicable
customerControlsBackups = required
customerControlsExportAndDeletion = required
```

### 3.2 Almacenamiento controlado por el cliente

Se considera bajo control del cliente cuando éste decide y administra:

- el dispositivo o servidor;
- la cuenta de almacenamiento;
- las credenciales;
- las llaves de cifrado, cuando apliquen;
- la política de respaldo;
- los usuarios con acceso;
- la conservación y eliminación.

Un NAS, OneDrive, Google Drive, S3 u otro servicio contratado directamente por el cliente puede formar parte de su almacenamiento, siempre que PRISMA no controle la cuenta, las credenciales o las llaves.

### 3.3 Separación de planos

```text
PLANO OPERATIVO LOCAL
ventas / inventario / usuarios / tickets / auditoría / DB / backups
                    ≠
PLANO REMOTO MÍNIMO
licencia / plan / entitlement / versión / deviceId técnico / health resumido
```

El plano de licencia no puede consultar bases operativas para decidir si una venta local se completa.

## 4. Contrato de egreso

Todo egreso de red debe ser **default-deny** para payload operativo.

### Permitido por defecto

- validación y refresh de licencia;
- consulta de plan y entitlement;
- descarga de manifests y updates firmados;
- heartbeat técnico mínimo;
- recepción de mensajes administrativos sin datos operativos;
- envío de estado resumido expresamente permitido.

### Prohibido por defecto

- bases completas o parciales;
- filas de ventas, clientes, empleados o inventario;
- payloads de outbox;
- tickets o recibos;
- dumps SQL;
- backups;
- contenido crudo de logs;
- capturas de pantalla;
- archivos adjuntos;
- RFC, CURP, teléfonos, correos o domicilios contenidos en la operación;
- consultas remotas arbitrarias a la DB;
- telemetría que reconstruya la operación del negocio.

## 5. Telemetría, errores y diagnósticos

1. La telemetría no es requisito para vender ni operar localmente.
2. Crash reports no deben incluir DB, payloads, formularios, headers, tokens o contexto operativo identificable.
3. Logs enviados deben pasar allowlist y redacción.
4. Los support bundles usan conteos, versiones, hashes y estados antes que contenido.
5. Un diagnóstico profundo requiere autorización visible y específica.
6. Ningún diagnóstico se carga automáticamente por el mero hecho de generarse.
7. El cliente puede revisar el bundle antes de compartirlo.

## 6. Soporte excepcional

El proveedor puede convertirse temporalmente en receptor o encargado de datos sólo cuando el cliente autoriza una intervención que realmente los expone.

Toda excepción debe registrar:

- quién autoriza;
- qué incidente se atiende;
- qué datos o archivos se compartirán;
- finalidad;
- duración;
- técnico autorizado;
- canal de transferencia;
- redacción aplicada;
- conservación;
- eliminación o devolución;
- revocación;
- evidencia de cierre.

Reglas:

- acceso temporal, no permanente;
- mínimo privilegio;
- no copiar la DB completa cuando basten metadatos;
- no conservar bundles después de la finalidad acordada;
- no usar datos de soporte para entrenamiento, analítica comercial o demostraciones;
- no habilitar túneles o comandos arbitrarios;
- todo acceso sensible debe ser auditable.

## 7. Responsabilidades

### Cliente

- define las finalidades de su operación;
- decide qué datos captura;
- administra usuarios y permisos;
- protege dispositivos y respaldos;
- decide conservación, exportación y eliminación;
- cumple sus obligaciones frente a empleados, compradores y otros titulares;
- autoriza cualquier soporte que exponga información.

### Proveedor de PRISMA

- entrega software que respeta esta frontera;
- no inserta accesos ocultos;
- separa licencia de operación;
- mantiene allowlists de red y diagnóstico;
- documenta endpoints y payloads remotos;
- protege los datos comerciales que sí recibe directamente;
- informa cambios que amplíen el egreso;
- no convierte una actualización en autorización para extraer datos.

## 8. Control del cliente

La licencia no debe impedir:

- exportar datos;
- crear respaldos;
- restaurar respaldos compatibles;
- consultar información histórica disponible localmente;
- eliminar datos;
- migrar información mediante mecanismos documentados.

La pérdida de internet o la indisponibilidad de Remote Ops no debe bloquear la venta local dentro de las reglas de grace y operación autorizadas.

## 9. Claims permitidos

Mientras sólo exista evidencia documental `SOURCE_READY`, pueden usarse afirmaciones como:

- “PRISMA está diseñado con arquitectura local-first.”
- “Los datos operativos se almacenan en infraestructura controlada por el cliente.”
- “El servidor de licencias no necesita recibir ventas, clientes o inventarios.”
- “El soporte que exponga datos requiere autorización.”

## 10. Claims prohibidos hasta certificación runtime

No afirmar todavía:

- “PRISMA nunca transmite ningún dato.”
- “Custodia cero certificada.”
- “Cero telemetría en todos los runtimes.”
- “Cumplimiento legal integral garantizado.”
- “Ningún tercero puede recibir datos.”
- “Todos los endpoints fueron certificados.”

Esas frases requieren evidencia runtime, análisis de red, revisión de integraciones y verificación por superficie.

## 11. Gates de certificación

Para avanzar de `SOURCE_READY` a `RUNTIME_VERIFIED`:

1. inventario de endpoints por Tablet, PC, Mobile, Local Agent y Remote Ops;
2. captura de tráfico en flujos representativos;
3. verificador de payloads contra allowlist;
4. prueba de venta offline sin Remote Ops;
5. prueba de licencia sin lectura de DB operativa;
6. prueba de support bundle sin PII, secretos ni payloads;
7. revisión de crash reporting y analytics;
8. revisión de updates y plugins;
9. evidencia de exportación, backup y eliminación controlados por el cliente;
10. matriz de terceros y destinos de red.

Para avanzar a una afirmación comercial fuerte, el gate debe producir evidencia por versión y por superficie.

## 12. Autoridades relacionadas

Este contrato complementa, no reemplaza:

- `PRISMA_DATA_OUTSIDE_REPO_POLICY.md`;
- `PRISMA_CUSTOMER_RUNTIME_LAYOUT_CONTRACT.md`;
- `PRISMA_SECURITY_PRIVACY_BASELINE.md`;
- `PRISMA_REMOTE_OPS_ARCHITECTURE.md`;
- `PRISMA_SUPPORT_BUNDLE_LOCAL_04_DATA_ALLOWLIST.md`;
- `PRISMA_NO_PAYMENT_PROCESSING_BOUNDARY.md`;
- gobierno NDC de scope, provenance y proyección canónica.

## 13. Estado

```text
contractStatus = SOURCE_READY
runtimeNoEgressCertified = false
legalComplianceCertified = false
nextGate = RUNTIME_DATA_EGRESS_AND_SUPPORT_BUNDLE_CERTIFICATION
```

La arquitectura queda definida. La implementación debe demostrar que la respeta antes de convertirla en promesa absoluta.
