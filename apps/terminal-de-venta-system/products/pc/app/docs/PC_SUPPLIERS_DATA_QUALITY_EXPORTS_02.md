# PRISMA PC - Proveedores Calidad de Datos y Exportables 02

## Proposito

Esta inyeccion agrega una capa de control para que Proveedores y Compra Inteligente no se vuelvan una pantallita bonita con datos flojos. La meta es revisar si proveedor, calendario, producto, pedido, recepcion, cuenta por pagar y auditoria estan suficientemente completos para operar sin vender humo.

## Por que existe

Compra Inteligente depende de ventas, inventario, caja, calendario y proveedor. Si uno de esos datos viene chueco, la recomendacion puede verse elegante pero decidir como compadre en oferta de mayoreo: emocionado, caro y peligroso.

Esta capa detecta:

- proveedor activo sin calendario;
- proveedor duplicado;
- producto sin proveedor valido;
- proveedor principal bloqueado;
- costo ausente o viejo;
- pedido sin lineas o con total descuadrado;
- recepcion con diferencias sin motivo;
- cuenta por pagar sin origen claro;
- recomendacion sin razones;
- recomendacion que intenta crear pedido con caja bloqueada;
- senales Tablet que intentan meter gobierno pesado fuera de PC;
- auditoria sin actor o motivo.

## Archivos tecnicos

- `src/lib/suppliers/data-quality.ts`: motor de calidad de datos.
- `src/lib/suppliers/export-contracts.ts`: construccion de CSVs operativos.
- `app/api/proveedores/calidad-datos/route.ts`: endpoint de reporte de calidad.
- `app/api/proveedores/exportables/route.ts`: endpoint de paquete exportable.

## Reporte de calidad

El reporte devuelve:

```ts
status: "ready" | "warning" | "blocked"
score: number
metrics: SupplierDataQualityMetric[]
findings: SupplierDataQualityFinding[]
sections: SupplierDataQualitySection[]
nextActions: string[]
```

## Criterio READY

La capa declara READY si:

- no hay bloqueos;
- proveedores activos tienen datos minimos;
- productos recomendables tienen proveedor y costo;
- recomendaciones explican razones;
- pedidos no quedan vacios;
- recepciones con diferencia tienen motivo;
- cuentas por pagar conservan origen;
- auditoria conserva actor y motivo;
- Tablet no recibe acciones de backoffice pesado.

## Criterio BLOCKED

Debe bloquear cuando:

- proveedor requerido no existe;
- recomendacion intenta crear pedido con proveedor bloqueado;
- recepcion con diferencia no tiene detalle;
- pedido total no cuadra con lineas;
- cuenta por pagar pendiente no tiene monto;
- auditoria sensible no tiene actor;
- Tablet intenta administrar proveedor, calendario, cuentas por pagar o aprobaciones pesadas.

## Exportables

El endpoint `exportables` prepara CSVs con:

- pedidos y lineas;
- recepciones y diferencias;
- cuentas por pagar;
- recomendaciones;
- auditoria;
- senales permitidas para Tablet y App movil.

Estos CSVs no son decoracion. Sirven para revisar operacion, soporte, demo controlada y auditoria ligera sin abrir la base de datos como si fuera lonchera de plomero.

## Reglas de no-humo

- No se exportan datos inventados como si fueran reales.
- No se ocultan datos faltantes.
- No se manda a Tablet ningun flujo pesado.
- No se declara compra segura si caja no alcanza.
- No se considera recomendacion valida si no explica razones.

## Smoke manual recomendado

```text
GET /api/proveedores/calidad-datos
GET /api/proveedores/exportables
```

Validar que:

- `ok` sea true;
- `status` exista;
- `score` sea numerico;
- `files` incluya CSVs esperados;
- cada exportable tenga `filename`, `description`, `rows` y `content`.
