# ATLAS TABLET INTERACTION - Ronda 2

## Objetivo

Documentar la interacción táctil y operativa confirmada para Tablet/POS desde el ZIP, sin inventar pantallas ni responsabilidades. Tablet se trata como terminal operativo POS, no como PC/backoffice.

## Principios táctiles observados

- La operación principal ocurre en superficies de venta, checkout, catálogo, ticket, turno, offline y sync.
- Las rutas usan páginas Next dedicadas, lo que permite separar flujos de mostrador sin mezclar ownership con PC.
- Los estados visibles son parte del contrato operativo: loading, error, not found, blocked/licensing, offline/outbox y release gate.
- La accesibilidad mínima aparece en verificadores de tickets, incluyendo aria label y foco interactivo.

## Flujos confirmados

### Venta POS

1. Usuario entra a `/pos` o `/checkout`.
2. Busca/resuelve producto mediante endpoints de catálogo/productos.
3. Completa venta con `/api/pos/sales/complete`.
4. El motor durable registra venta, líneas, movimientos de stock y evento de outbox.
5. El usuario puede revisar ventas en `/sales/today` y detalle en `/sales/today/[saleId]`.

### Ticket y devolución

1. Lista de ventas en `/sales/today`.
2. Detalle esperado en `/sales/today/[saleId]`.
3. Devolución desde `/sales/today/[saleId]/return` o `/returns`.
4. Creación de devolución por `/api/pos/returns/create`.

Hallazgo vigente: `verify:i03a-ticket-detail` falla porque el verificador espera llamada directa a endpoint de detalle y enlace con `encodeURIComponent(saleId)`. El atlas no lo declara resuelto.

### Turno

- `/shift` consume APIs de estado, apertura y cierre.
- Endpoints confirmados: `/api/pos/shift/current`, `/api/pos/shift/open`, `/api/pos/shift/close`.
- La responsabilidad local de Tablet es presentar/operar el turno; reglas corporativas externas quedan pendientes si dependen de Shared/Core no incluido.

### Offline, outbox y export

1. `/offline` llama `/api/pos/offline/audit`.
2. Auditoría integra reporte operacional, outbox, movimientos e información de exports.
3. Exportaciones confirmadas: ventas del día, eventos e inventario/movimientos.
4. Sync usa `/api/pos/sync/panel` y `/api/pos/sync/retry`.

Hallazgo vigente: `verify:04-offline` falla en `T04-008 screen renders outbox`. Es el punto exacto a corregir antes de release.

## Contratos de error/estado

| Estado | Evidencia |
| --- | --- |
| Ticket no encontrado | I03A espera `SALE_NOT_FOUND` y estado not_found visible |
| Error en ticket | I03A espera manejo de error visible |
| Loading | I03A valida que no sea estado permanente único |
| Outbox | T04 espera visibilidad explícita en pantalla offline |
| Licencia | Componentes Tablet consumen licencia externa y muestran estados, sin poseer motor externo |
| Release gate | `/release-gate` y API `pos/release-gate` exponen estado operativo |

## Pantallas con interacción crítica

| Pantalla | Interacción crítica |
| --- | --- |
| `/pos` | Venta rápida, búsqueda/selección de productos |
| `/checkout` | Confirmación/cierre de venta |
| `/sales/today` | Selección de ticket; debe enlazar con saleId codificado |
| `/sales/today/[saleId]` | Detalle directo de ticket |
| `/returns` | Captura/ejecución de devolución |
| `/shift` | Abrir/cerrar turno |
| `/offline` | Ver auditoría offline, outbox y descargar exports |
| `/sync` | Ver panel y reintentar sync |
| `/settings/license` | Ver estado de licencia/features externas |

## No confirmado

- Gestos físicos específicos de hardware Tablet.
- Rendimiento táctil real en dispositivo final.
- Smoke HTTP end-to-end con servidor Next activo.
- Ingestión PC de eventos exportados.

## Criterio de listo

Tablet Interaction no debe marcarse lista hasta que pasen I03A y T04. En barrio: primero que abra la cortina, cobre bien y entregue ticket; luego ya le ponemos letrero luminoso.
