# PRISMA App Mobile 22 - Daily Brief

## Objetivo

Agregar un resumen ejecutivo móvil que el dueño pueda compartir por WhatsApp, correo o cierre de turno sin abrir PC ni hacer capturas manuales.

## Alcance

- Nuevo motor puro `prisma-mobile-daily-brief.ts`.
- Nuevo componente `PrismaMobileDailyBrief`.
- Nuevo endpoint `GET /api/mobile/daily-brief` con `no-store`.
- Integración visual debajo de la Bandeja del Dueño.
- Script `verify:daily-brief`.

## Contrato

El brief se deriva del snapshot móvil, Centro de Mando v20 y Bandeja del Dueño v21. No toca Tablet, PC ni `shared-kernel`.

## Salida de producto

El usuario ve:

- resumen listo para WhatsApp;
- asunto/cuerpo para correo;
- KPIs compactos;
- secciones por dueño, acciones inmediatas, seguimiento e inventario;
- texto exportable para cierre operativo.

## Validación

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app" run verify:daily-brief
```

## Riesgo residual

El envío por WhatsApp/correo usa enlaces del navegador. Si el dispositivo no tiene app o cliente configurado, el navegador decide el destino. La generación del resumen sí queda dentro de PRISMA.
