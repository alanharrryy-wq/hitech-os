# PRISMA_APP_MOBILE_06_API_CONTRACTS

## Objetivo

Convertir PRISMA App Mobile de maqueta visual a superficie móvil con contratos API reales, todavía alimentados por `demo-contract-fixture`.

La intención de esta entrega no es conectar producción ni meter auth todavía. Es dejar la tubería limpia para que la siguiente iteración conecte PC/sync/servicios sin romper UI, como quien primero pone contactos antes de colgar la pantalla del Oxxo con cinta canela.

## Alcance instalado

Se agregan contratos tipados y validados con Zod en:

```text
products/mobile/app/src/lib/prisma-app/prisma-app-api-contracts.ts
products/mobile/app/src/lib/prisma-app/prisma-app-api-demo-source.ts
```

Se agregan route handlers Next.js bajo:

```text
/api/mobile/summary
/api/mobile/sales/today
/api/mobile/cash/current
/api/mobile/inventory/watchlist
/api/mobile/alerts
/api/mobile/reports/daily
/api/mobile/branches
/api/mobile/health
```

Todos responden con sobre estándar:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "apiVersion": "2026-05-02.mobile.06",
    "source": "demo-contract-fixture",
    "runtimeMode": "demo",
    "contractId": "PRISMA_APP_MOBILE_06_API_CONTRACTS"
  }
}
```

## Decisión técnica

- Mobile queda como superficie local de consulta y alerta.
- No se toca Tablet.
- No se toca PC.
- No se toca shared-kernel.
- No se conecta base de datos todavía.
- No se introduce dependencia dura a PC.

Esto conserva la regla arquitectónica: Tablet vende sola, PC administra cuando existe, Mobile consulta, resume y alerta.

## Endpoints

| Endpoint | Propósito | Fuente actual |
|---|---|---|
| `/api/mobile/summary` | Pantalla Hoy | demo data |
| `/api/mobile/sales/today` | Ventas del día | demo data |
| `/api/mobile/cash/current` | Caja actual | demo data |
| `/api/mobile/inventory/watchlist` | Inventario prioritario | demo data |
| `/api/mobile/alerts` | Cola de alertas | demo data |
| `/api/mobile/reports/daily` | Reporte ejecutivo diario | demo data |
| `/api/mobile/branches` | Vista multisucursal | demo data |
| `/api/mobile/health` | Salud del contrato API | contrato local |

## Validación

Comando local desde `products/mobile/app`:

```powershell
pnpm run verify:api-contracts
```

O directo desde raíz del producto terminal:

```powershell
node products/mobile/app/tools/verify_prisma_app_mobile_06_api_contracts.mjs F:\repos\hitech-os\apps\terminal-de-venta-system
```

## Próxima iteración recomendada

`PRISMA_APP_MOBILE_07_UI_API_BINDING`

Objetivo: hacer que la pantalla `/prisma-app` consuma estos endpoints mediante un adapter interno, con fallback demo si falla API. Ahí dejamos de tener UI pegada directamente a fixtures, que es muy bonito hasta que quieres datos reales y la carreta se vuelve cohete de feria.
