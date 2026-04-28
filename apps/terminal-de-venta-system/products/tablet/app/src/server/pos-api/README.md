# PRISMA Tablet POS API 01B

Esta capa conecta la UI de Tablet con el motor POS local instalado en `01A_ENGINE`.

## Principio

Tablet debe poder vender sin PC. La API no sincroniza contra backoffice; opera sobre la base local `data/tablet-pos.db` mediante Prisma y deja eventos/outbox generados por el motor.

## Endpoints

| Metodo | Ruta | Uso |
|---|---|---|
| GET | `/api/pos/products/search?q=` | Buscar productos por nombre, SKU, categoria o barcode parcial |
| GET | `/api/pos/products/resolve?code=` | Resolver producto exacto por SKU, barcode o id |
| POST | `/api/pos/sales/complete` | Cerrar venta local con validacion de stock |
| GET | `/api/pos/sales/today` | Resumen operativo del dia |

## Contrato de error

Todas las respuestas de error usan:

```json
{
  "ok": false,
  "code": "INSUFFICIENT_STOCK",
  "message": "Stock insuficiente para cerrar la venta local."
}
```

Nada de mandar stacktraces al cliente. El changarro no necesita ver las tripas del motor para cobrar una Coca.
