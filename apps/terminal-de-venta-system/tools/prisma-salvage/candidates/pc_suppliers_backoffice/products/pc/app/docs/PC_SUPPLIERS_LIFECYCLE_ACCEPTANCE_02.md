# PRISMA PC - Aceptacion Proveedores Lifecycle 02

## Objetivo

Cerrar la brecha entre una recomendacion bonita y una operacion defendible. El paquete v02 no intenta ser base de datos final. Su chamba es dejar el contrato operativo listo para que la siguiente iteracion conecte persistencia real sin discutir nombres, estados y auditoria como si fueran herencia familiar.

## Criterios READY

### Compra Inteligente

- Genera recomendaciones con razones visibles.
- Distingue compra critica, compra segura, esperar, configurar y bloqueada.
- Muestra impacto de caja.
- Permite simular con presupuesto, exclusiones y cantidades.
- No crea pedido si la simulacion queda bloqueada.

### Pedido sugerido

- Conserva origen `smart_purchase`.
- Tiene proveedor, folio, lineas, total y fechas.
- No permite pedido vacio.
- Requiere actor y motivo.
- Genera evento de auditoria.

### Recepcion

- Parte de pedido aprobado/enviado o flujo controlado.
- Captura cantidades recibidas por linea.
- Si hay diferencia, la muestra y advierte.
- Genera vista previa de movimiento de inventario.
- Genera cuenta por pagar cuando corresponde.
- No borra recepcion confirmada en silencio.

### Cuentas por pagar

- Conservan proveedor, monto, fecha y origen.
- Distinguen programado, proximo, vencido y pagado.
- Pago parcial deja saldo.
- Pago completo cierra cuenta.
- Pago registra auditoria.

### Auditoria

Cada accion sensible debe incluir:

- actor;
- rol;
- accion;
- entidad;
- motivo;
- antes/despues cuando aplique;
- resumen visible;
- fuente.

### Tablet/App movil

Tablet puede mostrar avisos ligeros:

- producto critico;
- proveedor esperado;
- recepcion pendiente;
- revisar en PC.

No puede administrar:

- proveedor completo;
- cuenta por pagar;
- reglas de credito;
- aprobacion final pesada;
- recepcion con diferencias.

App movil puede alertar y revisar impacto, pero no reemplaza PC para captura pesada.

## Criterios BLOCKED

- Recomendacion sin razones.
- Crear pedido sin lineas.
- Crear pedido con proveedor bloqueado.
- Simulacion bloqueada que aun permita crear pedido.
- Recepcion con diferencias sin motivo.
- Movimiento de inventario sin fuente.
- Cuenta por pagar sin origen.
- Pago sin actor.
- UI con copy tecnico como `Smart Purchasing`, `Purchase order`, `Payload`, `Runtime`, `Commit`.
- Tablet administrando proveedores.

## Smoke cases incluidos

El archivo `src/lib/suppliers/lifecycle-scenarios.ts` define escenarios de QA:

1. Simular compra segura.
2. Quitar producto critico.
3. Crear pedido desde recomendacion.
4. Bloquear pedido por cajero.
5. Confirmar recepcion con diferencia.
6. Confirmar recepcion completa.
7. Registrar pago parcial.
8. Bloquear pago por cajero.
9. Verificar frontera Tablet.
10. Verificar frontera App movil.

## Endpoints de inspeccion

- `GET /api/proveedores/operacion`
- `GET /api/proveedores/auditoria`
- `GET /api/proveedores/calendario`
- `GET /api/proveedores/senales`
- `GET /api/proveedores/pedidos`
- `GET /api/proveedores/recepciones`
- `GET /api/proveedores/cuentas-pagar`
- `GET /api/proveedores/qa/escenarios`

## Siguiente iteracion recomendada

Con este contrato ya en pie, lo siguiente serio es persistencia:

1. Repositorio Prisma para Supplier, SupplierProduct, PurchaseOrder, ReceivingReceipt, SupplierPayable y AuditEvent.
2. Migracion controlada.
3. Seed minimo no demo-humoso.
4. Conectar POSTs a DB real con rollback transaccional.
5. Mantener el mismo contrato de UI/API para no romper lo ya instalado.

## Nota de honestidad brutal

Este paquete todavia usa fixtures. No lo vendo como produccion real. Lo vendo como capa operativa de contrato y motor deterministico para que el siguiente ZIP ya conecte DB sin cambiar todo como albañil improvisando castillo en la banqueta.
