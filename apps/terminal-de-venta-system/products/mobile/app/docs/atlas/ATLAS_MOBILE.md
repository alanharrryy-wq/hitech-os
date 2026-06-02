# ATLAS MOBILE

## 1. Propósito

Este atlas inicial documenta el dominio Mobile encontrado dentro del ZIP `ATLAS_CHAT_MOBILE.zip`. Su función es servir como mapa de trazabilidad para cambios futuros: intención humana, rutas a revisar, archivos probables, dependencias externas, verificación y rollback.

Este documento no modifica código funcional y no declara propiedad sobre Shared Core, Tablet, PC, Android tooling ni estilos compartidos externos.

## 2. Alcance confirmado

Raíz Mobile confirmada dentro del ZIP:

`source_snapshot/products/mobile/app`

Raíz de producto que el atlas describe:

`products/mobile/app`

Archivos de soporte dentro del ZIP usados como contexto:

- `README_PACKAGE.md`
- `START_HERE_PROMPT.md`
- `EXPECTED_OUTPUTS.md`
- `analysis/*`
- `global_context/*`
- `templates/*`

Las rutas documentadas en este atlas se consideran confirmadas solo cuando aparecen en el snapshot Mobile o en los manifests del ZIP. Cuando algo depende de contexto externo o no está presente físicamente en el ZIP, se marca como pendiente de confirmar.

## 3. Fronteras de propiedad

### Mobile-owned dentro del snapshot

- `app/*`
- `src/components/prisma-app/*`
- `src/lib/prisma-app/*`
- `public/*` presente bajo el snapshot Mobile
- `scripts/*` presente bajo el snapshot Mobile
- `package.json`, `next.config.mjs`, `tsconfig.json`, `postcss.config.mjs`, `tailwind.config.ts`

### Dependencias externas, no propiedad Mobile

- Shared Core
- Shared UI
- estilos globales externos al snapshot Mobile
- Tablet service
- PC service
- Android/Play Store tooling fuera del snapshot
- Cloudflare/infra fuera del snapshot

## 4. Modelo mental del producto

Mobile es el tablero rápido de supervisión del ecosistema PRISMA. No está documentado como POS ni como consola completa de administración. Su intención principal es mostrar pulso operativo: ventas, caja, alertas, inventario, salud, acciones pendientes y resumen diario.

La regla de barrio: Tablet vende en mostrador, PC gobierna la oficina, Mobile es el dueño mirando el changarro desde la banqueta con el celular en la mano. No se le carga la camioneta completa, solo lo necesario para decidir rápido.

## 5. Rutas confirmadas

| Ruta | Archivo | Responsabilidad confirmada |
|---|---|---|
| `/` | `app/page.tsx` | Entrada raíz del snapshot Mobile. |
| `/prisma-app` | `app/prisma-app/page.tsx` | Superficie principal de la app Mobile. |
| `/prisma-app/install` | `app/prisma-app/install/page.tsx` | Flujo de instalación/PWA. |
| `/prisma-app/offline` | `app/prisma-app/offline/page.tsx` | Superficie offline. |

## 6. APIs confirmadas

APIs bajo `app/api/mobile/*`:

- `/api/mobile/summary`
- `/api/mobile/snapshot`
- `/api/mobile/sales/today`
- `/api/mobile/cash/current`
- `/api/mobile/inventory/watchlist`
- `/api/mobile/alerts`
- `/api/mobile/reports/daily`
- `/api/mobile/branches`
- `/api/mobile/health`
- `/api/mobile/command-center`
- `/api/mobile/action-inbox`
- `/api/mobile/daily-brief`
- `/api/mobile/decision-ledger`
- `/api/mobile/pulse-timeline`
- `/api/mobile/health-radar`

Estas rutas deben tratarse como contratos Mobile. Cualquier cambio futuro debe revisar consumers de UI, schemas/normalizadores y verificadores asociados.

## 7. Superficies visuales confirmadas

Componentes encontrados bajo `src/components/prisma-app`:

- `PrismaMobileDashboard.tsx`
- `PrismaMobilePremiumNavigator.tsx`
- `PrismaMobileCommandCenter.tsx`
- `PrismaMobileActionInbox.tsx`
- `PrismaMobileDailyBrief.tsx`
- `PrismaMobileDecisionLedger.tsx`
- `PrismaMobilePulseTimeline.tsx`
- `PrismaMobileHealthRadar.tsx`
- `PrismaMobilePwaInstallCard.tsx`
- `PrismaMobilePwaRuntime.tsx`

## 8. Motores funcionales confirmados

Motores encontrados bajo `src/lib/prisma-app`:

- Command Center
- Action Inbox
- Daily Brief
- Decision Ledger
- Pulse Timeline
- Health Radar
- Snapshot/cache
- API contracts
- Formatters
- PWA client/runtime
- Mobile data plane

## 9. Runtime y delivery

Mobile se documenta como app Next/PWA. El snapshot incluye `manifest.webmanifest`, service worker/runtime PWA y scripts de verificación relacionados con readiness, release hardening, hydration, production data, data plane y superficies premium.

Variables/env observadas o inferidas por archivos del snapshot:

- `PRISMA_MOBILE_TABLET_ORIGIN`
- `PRISMA_MOBILE_PC_ORIGIN`
- `PRISMA_MOBILE_SOURCE_TIMEOUT_MS`
- `PRISMA_MOBILE_RETRY_COUNT`
- `PRISMA_MOBILE_STALE_AFTER_MS`
- `PRISMA_MOBILE_LOW_STOCK_THRESHOLD`
- `PRISMA_MOBILE_OVERSTOCK_THRESHOLD`

Defaults observados desde el snapshot/contexto:

- Tablet origin: `http://127.0.0.1:3120`
- PC origin: `http://127.0.0.1:3130`
- Mobile origin: `http://127.0.0.1:3140`

## 10. Hallazgos corregidos de Ronda 1

### 10.1 Assets PWA faltantes

El ZIP referencia PNGs de iconos PWA que no están presentes en el snapshot. No se inventaron ni se documentaron como existentes. Quedan como pregunta abierta y como riesgo de release.

Ejemplos referenciados por manifest/runtime según inspección de Ronda 2:

- `/icons/prisma_playstore_icon_192.png`
- `/icons/prisma_playstore_icon_512.png`
- `/apple-touch-icon.png`
- `/apple-touch-icon-precomposed.png`
- `/icons/prisma_ios_touch_icon_180.png`
- `/icons/prisma_whatsapp_install_icon.png`

Assets confirmados presentes:

- `public/icons/prisma-app-icon.svg`
- `public/icons/prisma-app-maskable.svg`
- `public/icons/prisma-app-monochrome.svg`
- `public/icons/prisma_playstore_icon(1).svg`
- `public/icons/prisma_playstore_icon(2).svg`
- `public/screenshots/prisma-mobile-pwa-dashboard.png`

### 10.2 Analysis no tratado como verdad absoluta

Los manifests de `analysis/*` pueden reflejar un estado distinto del contenido real del ZIP. El atlas los usa como contexto, pero la presencia física en el ZIP manda.

### 10.3 Shared Core no apropiado por Mobile

Shared Core y shared styles quedan listados como dependencia externa, no como propiedad Mobile.

### 10.4 No se usaron rutas finales para staging

Esta entrega se sube únicamente a:

`docs/atlas/_incoming/mobile/`

No se toca `products/mobile/app/docs/atlas/`.

## 11. Intenciones de cambio principales

### Cambiar dashboard principal

Revisar:

- `app/prisma-app/page.tsx`
- `src/components/prisma-app/PrismaMobileDashboard.tsx`
- `src/components/prisma-app/PrismaMobilePremiumNavigator.tsx`
- APIs de snapshot/summary/sales/cash/alerts según el bloque afectado.

Verificar:

- typecheck
- build
- verificadores de dashboard/premium navigation si están disponibles en el repo completo

Rollback:

- revertir cambios en componentes y mantener contracts API intactos.

### Cambiar navegación premium

Revisar:

- `PrismaMobilePremiumNavigator.tsx`
- surfaces dependientes: command center, inbox, daily brief, ledger, timeline, radar.

Verificar:

- release hardening
- premium navigation verifier

Rollback:

- revertir el componente navegador y conservar rutas API sin cambios.

### Cambiar flujo PWA/install

Revisar:

- `app/prisma-app/install/page.tsx`
- `src/components/prisma-app/PrismaMobilePwaInstallCard.tsx`
- `src/components/prisma-app/PrismaMobilePwaRuntime.tsx`
- `public/manifest.webmanifest`
- service worker/runtime PWA presente en `public`

Verificar:

- `verify:pwa`
- manifest icon availability
- install prompt behavior manual

Rollback:

- revertir manifest/runtime/install card. No borrar assets compartidos sin confirmar ownership.

### Cambiar offline behavior

Revisar:

- `app/prisma-app/offline/page.tsx`
- PWA runtime/service worker
- snapshot/cache utilities en `src/lib/prisma-app`

Verificar:

- PWA/offline manual
- hydration verifier
- production-data verifier cuando aplique

Rollback:

- restaurar runtime/cache previo y mantener endpoint contracts.

### Cambiar APIs Mobile

Revisar ruta específica bajo `app/api/mobile/*/route.ts`, schemas de contratos, engines asociados y components consumers.

Verificar:

- typecheck
- endpoint smoke manual
- verifier específico si existe

Rollback:

- revertir route handler y mantener respuesta compatible.

## 12. Verificación sugerida

Desde repo completo, no desde ZIP parcial:

```bash
cd products/mobile/app
npm run typecheck
npm run build
npm run verify:pwa
npm run verify:release-hardening
npm run verify:premium-navigation
npm run verify:data-plane-types
npm run verify:runtime-error-guard
```

Si se trabaja solo con el ZIP, algunos checks pueden fallar por dependencias externas ausentes. Eso debe tratarse como limitación del paquete, no necesariamente como falla funcional del repo completo.

## 13. Pendientes críticos

- Confirmar si los PNG PWA faltantes existen en otra parte del monorepo.
- Confirmar si Android tooling y Cloudflare tooling deben considerarse parte de otro paquete de release.
- Confirmar cómo se materializan los shared styles importados por CSS Mobile.
- Confirmar si `analysis/mobile_public_asset_manifest.json` debe regenerarse desde el ZIP real.

## 14. Regla para cambios futuros

Antes de tocar código, mapear siempre:

1. Intención humana.
2. Ruta visible o API afectada.
3. Componentes y engines owners.
4. Dependencias externas.
5. Verificador mínimo.
6. Rollback concreto.

Sin ese mapa, el cambio es meter la mano al tablero eléctrico con los ojos cerrados. Puede funcionar, pero el madrazo llega con intereses.
