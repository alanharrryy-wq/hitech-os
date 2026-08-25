# PRISMA App Mobile 27 - Premium Navigation

## Objetivo

Convertir el tablero móvil de PRISMA en una experiencia separada por intención: Resumen, Caja, Alertas, Inventario y Sync.

Antes, la pantalla crecía en vertical y algunos módulos avanzados caían sin estilos completos. El resultado visual era una sábana operativa: útil para una computadora estoica, pero cruel para un dueño revisando desde celular.

## Alcance instalado

- `PrismaMobilePremiumNavigator.tsx`
  - nuevo rail premium con `tablist`, `tab` y `tabpanel`.
  - soporte de teclado con flechas, Home y End.
  - render condicional por sección para no montar todo el tablero pesado de golpe.
  - badges operativos por sección.

- `PrismaMobileDashboard.tsx`
  - conserva hero, estado de datos y tarjeta PWA.
  - delega la entrega de información larga al navegador premium.
  - evita que Command Center, Action Inbox, Brief, Decision Ledger, Timeline y Radar aparezcan todos de corrido.

- `prisma-mobile-dashboard.module.css`
  - estilos premium para navegación, paneles y secciones.
  - estilos faltantes para Decision Ledger, Pulse Timeline y Health Radar.
  - `content-visibility:auto` para secciones pesadas.

- `verify_prisma_app_mobile_27_premium_navigation.mjs`
  - valida contrato visual, accesibilidad básica, registro de script, estilos críticos y documentación.

## Secciones

### Resumen

Entrega lectura ejecutiva: fuente activa, caja, diferencia, Command Center, KPIs, semáforo operativo y acciones sugeridas.

### Caja

Agrupa corte, ritmo por horario, reportes y brief diario compartible.

### Alertas

Agrupa bandeja del dueño, excepciones activas y bitácora de decisiones.

### Inventario

Agrupa productos a vigilar y salud por tienda.

### Sync

Agrupa advertencias de carga, radar de salud y timeline operativo.

## Qué corrige

1. La información ya no aparece como fila interminable.
2. Los módulos que antes podían verse como texto plano reciben estilos reales.
3. El usuario tiene navegación de alto nivel sin perder detalle.
4. La pantalla mantiene intención móvil: revisar, decidir y actuar.

## Fuera de alcance

- No toca Tablet POS.
- No toca PC Backoffice.
- No toca `shared-kernel`.
- No cambia contratos de datos ni endpoints.
- No cambia lógica de ventas, inventario ni sincronización.

## Validación esperada

```text
pnpm -C products/mobile/app run verify:premium-navigation
pnpm -C products/mobile/app run typecheck
```

Si el entorno no tiene dependencias instaladas, el verificador propio puede ejecutarse con Node desde `products/mobile/app`.
