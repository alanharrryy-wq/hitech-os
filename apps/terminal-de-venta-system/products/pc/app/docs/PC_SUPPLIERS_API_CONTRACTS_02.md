# PRISMA PC - Contratos API Proveedores Lifecycle 02

## Principio

Estas rutas son contratos operativos para bajar a persistencia real sin rediseñar toda la aplicacion. En esta entrega usan motor deterministico y fixtures. En la siguiente pueden apuntar a repositorio Prisma manteniendo forma de entrada y salida.

## GET /api/proveedores/operacion

Devuelve snapshot completo:

- lifecycle;
- readiness gates;
- calendario;
- workflow de pedidos;
- movimientos previstos;
- plan de cuentas por pagar;
- auditoria;
- reporte READY/WARNING/BLOCKED;
- politica de caja.

## POST /api/proveedores/compra-inteligente/simular

Entrada:

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

Salida:

```json
{
  "ok": true,
  "data": {
    "originalTotalCents": 480000,
    "simulatedTotalCents": 360000,
    "cashAfterPurchaseCents": 260000,
    "cashImpact": "safe",
    "coverageSummary": "Cobertura promedio recalculada",
    "canCreateOrder": true,
    "warnings": []
  }
}
```

Bloqueos:

- recomendacion inexistente;
- presupuesto bloqueado;
- todas las lineas excluidas;
- caja negativa.

## POST /api/proveedores/compra-inteligente/crear-pedido

Entrada:

```json
{
  "recommendationId": "rec_sup_beverages",
  "reason": "Se reviso cobertura y proveedor antes del fin de semana.",
  "actor": {
    "id": "usr_admin_prisma",
    "name": "Administrador PRISMA",
    "role": "Administrador"
  }
}
```

Salida:

```json
{
  "ok": true,
  "code": "SUGGESTED_ORDER_CREATED",
  "message": "Pedido creado desde Compra Inteligente. Revisa cantidades antes de enviarlo.",
  "data": {
    "order": {
      "source": "smart_purchase",
      "status": "suggested"
    }
  },
  "auditEvents": []
}
```

Bloqueos:

- actor sin permiso;
- falta motivo;
- compra bloqueada;
- recomendacion sin lineas;
- proveedor bloqueado.

## POST /api/proveedores/recepciones/confirmar

Entrada:

```json
{
  "orderId": "po_001",
  "reason": "Factura revisada contra mercancia recibida.",
  "actor": {
    "id": "usr_admin_prisma",
    "name": "Administrador PRISMA",
    "role": "Administrador"
  },
  "receivedUnitsByLineId": {
    "pol_001": 24,
    "pol_002": 12
  }
}
```

Salida:

- receipt;
- movementPreview;
- payable;
- warnings si hay diferencia;
- auditEvents.

## POST /api/proveedores/cuentas-pagar/registrar-pago

Entrada:

```json
{
  "payableId": "pay_001",
  "amountCents": 120000,
  "reason": "Abono registrado desde banca.",
  "actor": {
    "id": "usr_owner_prisma",
    "name": "Dueño PRISMA",
    "role": "Dueño"
  }
}
```

Salida:

- payable actualizado;
- remainingCents;
- warning si queda saldo;
- auditoria.

## GET endpoints de lectura

- `/api/proveedores/auditoria`
- `/api/proveedores/calendario`
- `/api/proveedores/senales`
- `/api/proveedores/pedidos`
- `/api/proveedores/recepciones`
- `/api/proveedores/cuentas-pagar`
- `/api/proveedores/qa/escenarios`

## Estado de esta entrega

Contrato listo para persistencia. No sustituye schema real. No toca Tablet. No toca shared-kernel. No infla menu con rutas visuales extra: las APIs quedan como capa tecnica del modulo.
