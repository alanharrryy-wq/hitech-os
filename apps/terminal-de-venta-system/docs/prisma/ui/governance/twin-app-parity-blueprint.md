# PRISMA Twin App Parity Blueprint

## Decisión madre

Las apps no deben emparejarse copiando pantallas una en la otra. Eso sería vestir al cajero con traje de auditor y al auditor con mandil de taquero. Se emparejan por contrato, lenguaje visual, datos, eventos y responsabilidades.

- **PC** gobierna, configura, audita, consolida, resuelve conflictos y decide.
- **Tablet** ejecuta, cobra, registra, opera en piso, soporta offline y genera eventos.

La paridad correcta no es igualdad de botones. Es igualdad de sistema.

## Estado observado

| Superficie | Estado actual | Lectura |
|---|---|---|
| PC | Backoffice con catálogo, existencias, conteos, compras, recepción, reabasto, auditoría y sync | Va más madura como centro de control. Tiene más rutas, más documentos y más granularidad ejecutiva. |
| Tablet | Terminal operacional con ventas, cobro, turno, devoluciones, stock y sync | Va más enfocada y usable para piso. Tiene menos superficie, pero mejor claridad de rol. |
| Shared twin-kernel | Contrato compartido mínimo para módulos y eventos sync | Existe base compartida, pero todavía está flaca para gobernar paridad real. |
| Prisma canónico | Validación canonical PASS con generación PC y Tablet | Buena señal: la base de datos ya no está como vecindad de datos donde cada quien cuelga su cable. |

## Principio de emparejamiento

Cada capacidad debe responder cuatro preguntas:

1. **Qué hace PC**: supervisa, configura, autoriza, resuelve o reporta.
2. **Qué hace Tablet**: ejecuta, captura, cobra, escanea, confirma o encola.
3. **Qué contrato comparten**: entidad, evento, permiso, estado offline y evidencia.
4. **Qué no debe duplicarse**: modelos, reglas de negocio, permisos o navegación canónica.

## Mapa de paridad funcional

| Dominio | PC | Tablet | Paridad buscada |
|---|---|---|---|
| Dashboard | KPIs ejecutivos, alertas, scorecards | Inicio operativo, riesgos del turno, señales de caja/stock/sync | Misma salud del negocio, distinta profundidad. |
| Catálogo | Alta, edición, validación, precios, barcodes | Consulta rápida, escaneo, selección para venta | PC manda catálogo; Tablet consume y marca incidencias. |
| Stock | Existencias globales, auditoría, ajustes, conteos | Stock operativo, quiebres, señales de reabasto | Misma verdad de inventario; Tablet no inventa stock mágico. |
| Ventas | Supervisión, análisis, tickets, márgenes | Venta, checkout, devoluciones | Tablet ejecuta; PC audita y explota datos. |
| Caja / turno | Reglas, reportes, arqueos, diferencias | Apertura, cierre, movimientos | Un mismo ciclo de caja con dos vistas. |
| Compras / recepción | Órdenes, proveedores, recepción formal | Recepción rápida o confirmación física ligera | PC formaliza; Tablet captura evidencia de piso. |
| Sync | Monitor, conflictos, outbox, recuperación | Estado local, cola, reintentos, modo offline | PC resuelve; Tablet no se queda muda. |
| Auditoría | Trazabilidad, permisos, bitácora | Evidencia mínima por acción sensible | Evento común, profundidad distinta. |

## Brechas prioritarias

### Brecha 1: contrato compartido demasiado chico

`TwinModuleManifest` hoy alcanza para navegación básica, pero no para gobernar paridad. Falta declarar dominio, superficie, eventos, permisos, offline y relación espejo.

**Propuesta:** evolucionar a `TwinCapabilityManifest` sin romper el manifiesto actual.

### Brecha 2: PC tiene mucha granularidad, Tablet tiene mucha operación

Eso es bueno, pero hay que conectar los reflejos. Por ejemplo, lo que Tablet hace en checkout debe tener espejo PC en auditoría, ventas, caja y sync.

**Propuesta:** crear matriz `pc_tablet_capability_map` y usarla como check de PR.

### Brecha 3: nombres y rutas todavía no cuentan una historia común

PC usa dominios de control y rutas detalladas. Tablet usa rutas limpias. Si no se normaliza el vocabulario, en tres iteraciones parecerán primos que se saludan de lejos en Navidad.

**Propuesta:** glosario común de dominios: `sales`, `cash`, `stock`, `catalog`, `procurement`, `sync`, `audit`.

### Brecha 4: QA de paridad debe volverse gate

Ya hay QA por tablet y validación canónica, pero falta una prueba explícita: cada evento de Tablet debe aterrizar en una vista PC o reporte de control.

**Propuesta:** gate `twin-parity-acceptance` antes de cerrar incrementos.

## Regla de oro

Nada entra como pantalla nueva si no declara su pareja:

- pareja PC,
- pareja Tablet,
- evento compartido,
- permiso,
- estado offline,
- evidencia,
- rollback.

Si no puede declarar eso, todavía no es feature. Es ocurrencia con CSS.
