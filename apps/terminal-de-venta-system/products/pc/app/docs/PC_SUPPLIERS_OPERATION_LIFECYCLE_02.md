# PRISMA PC - Proveedores Operacion Compra Inteligente 02

## Que entrega este paquete

Esta inyeccion v02 convierte el primer modulo de Proveedores + Compra Inteligente en un ciclo operativo mas completo:

1. Compra Inteligente genera recomendaciones explicables.
2. Una recomendacion se puede simular con presupuesto, lineas excluidas y cantidades ajustadas.
3. Una recomendacion viable se convierte en pedido sugerido.
4. Un pedido puede confirmar recepcion completa o con diferencias.
5. La recepcion genera vista previa de movimientos de inventario.
6. La recepcion genera cuenta por pagar cuando corresponde.
7. El pago parcial o total genera auditoria.
8. Tablet y App movil reciben solo senales ligeras, no gobierno pesado.

No mete schema nuevo ni toca shared-kernel. Es una capa operativa deterministica sobre fixtures existentes y contratos claros para bajar a persistencia real despues.

## Frontera de producto

PC sigue siendo dueño de:

- proveedores;
- calendario;
- pedidos;
- recepciones;
- cuentas por pagar;
- Compra Inteligente;
- auditoria;
- decisiones sensibles.

Tablet solo ve:

- proveedor esperado hoy;
- producto critico;
- recepcion pendiente;
- aviso de revisar en PC.

App movil ve:

- compra critica;
- pago proximo;
- pedido esperando aprobacion;
- caja apretada.

## Archivos funcionales principales

### `src/lib/suppliers/lifecycle-engine.ts`

Motor puro. No depende de Next, React ni Prisma. Construye:

- readiness gates;
- calendario operativo;
- flujo de pedidos;
- vista previa de movimientos por recepcion;
- plan de cuentas por pagar;
- señales para Tablet/App movil;
- eventos de auditoria.

Tambien expone acciones puras:

- `createSuggestedOrderFromRecommendation`
- `confirmSupplierReceiving`
- `registerSupplierPayment`

### `src/lib/suppliers/server.ts`

Capa servidor. Junta fixtures, motor de Compra Inteligente y motor lifecycle. Expone funciones usadas por rutas API y pagina `/proveedores`.

### Rutas API nuevas

- `GET /api/proveedores/operacion`
- `POST /api/proveedores/compra-inteligente/simular`
- `POST /api/proveedores/compra-inteligente/crear-pedido`
- `POST /api/proveedores/recepciones/confirmar`
- `POST /api/proveedores/cuentas-pagar/registrar-pago`

## Contrato de ejemplo: simular

```json
{
  "recommendationId": "rec_sup_beverages",
  "budgetCents": 620000,
  "excludedLineIds": ["line_prod_003"],
  "quantityOverrides": {
    "line_prod_001": 48
  }
}
```

Respuesta esperada:

```json
{
  "ok": true,
  "data": {
    "recommendationId": "rec_sup_beverages",
    "simulatedTotalCents": 200000,
    "cashImpact": "safe",
    "canCreateOrder": true
  }
}
```

## Contrato de ejemplo: crear pedido sugerido

```json
{
  "recommendationId": "rec_sup_beverages",
  "reason": "Se reviso cobertura y el proveedor no vuelve antes del fin de semana.",
  "actor": {
    "id": "usr_admin_prisma",
    "name": "Administrador PRISMA",
    "role": "Administrador"
  }
}
```

La respuesta conserva:

- pedido;
- folio;
- origen `smart_purchase`;
- lineas;
- warnings;
- eventos de auditoria.

## Contrato de ejemplo: recepcion

```json
{
  "orderId": "po_001",
  "reason": "Mercancia revisada contra factura del proveedor.",
  "actor": {
    "id": "usr_admin_prisma",
    "name": "Administrador PRISMA",
    "role": "Administrador"
  },
  "receivedUnitsByLineId": {
    "pol_001": 48,
    "pol_002": 20
  }
}
```

Si hay diferencias, la respuesta no las borra. Las muestra como warnings y las audita.

## QA minimo cubierto por el verificador

`tools/verify_pc_suppliers_lifecycle_02.mjs` revisa:

- archivos esperados;
- rutas API nuevas;
- ausencia de copy tecnico visible peligroso en UI;
- `productId` en links de proveedor-producto;
- presencia de acciones sensibles auditadas;
- endpoints con metadatos es-MX;
- componente UI con secciones nuevas.

## Pendiente consciente

No se conecto todavia a Prisma real. Eso se deja como siguiente bloque para no mezclar schema, migraciones y UX en una sola sopa de cables. Esta entrega deja contratos y motor listos para persistencia real.
