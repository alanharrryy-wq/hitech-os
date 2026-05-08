# ATLAS MOBILE VISUAL

## 1. Propósito

Este documento mapea las superficies visuales confirmadas de Mobile en el ZIP `ATLAS_CHAT_MOBILE.zip`. Sirve para cambios futuros de UI sin confundir Mobile con Shared UI, PC, Tablet o Shared Core.

Todo lo listado aquí corresponde a archivos encontrados o referenciados por el snapshot Mobile, salvo que se marque como dependencia externa o pendiente de confirmar.

## 2. Superficie principal

### Ruta

`/prisma-app`

### Archivo de entrada

`app/prisma-app/page.tsx`

### Componentes relacionados

- `src/components/prisma-app/PrismaMobileDashboard.tsx`
- `src/components/prisma-app/PrismaMobilePremiumNavigator.tsx`

### Responsabilidad visual

La superficie principal concentra el pulso Mobile: resumen operativo, navegación premium y acceso a módulos de supervisión. Cualquier cambio visual en esta ruta debe revisar estado inicial, jerarquía de tarjetas, navegación, estados vacíos y comportamiento responsive.

## 3. Dashboard Mobile

### Archivo confirmado

`src/components/prisma-app/PrismaMobileDashboard.tsx`

### Intención humana asociada

Cambiar cómo el dueño o supervisor entiende el estado del negocio desde el celular.

### Revisión mínima antes de cambiar

- Qué datos consume.
- Qué bloques visuales muestra.
- Qué estados maneja: loading, error, stale, offline, empty.
- Qué formato de moneda, fecha o conteo usa.
- Qué API alimenta cada bloque.

### Dependencias externas

- tokens/estilos compartidos importados por CSS si existen fuera del snapshot.
- contratos de datos de `src/lib/prisma-app`.

No documentar esos estilos como propiedad de Mobile si viven fuera del snapshot.

## 4. Navegación premium

### Archivo confirmado

`src/components/prisma-app/PrismaMobilePremiumNavigator.tsx`

### Responsabilidad visual

Organizar acceso a superficies avanzadas: command center, action inbox, daily brief, decision ledger, pulse timeline y health radar.

### Riesgo de cambio

Un ajuste de labels, tabs, orden o visibilidad puede romper trazabilidad del usuario aunque la app compile. Cambiar navegación es como mover los pasillos del mercado: todos siguen los olores, pero se pierden si cambias la esquina del puesto.

### Verificación sugerida

- `verify:premium-navigation` si está disponible.
- revisión manual de todos los destinos.
- navegación por teclado/touch cuando aplique.

## 5. Command Center

### Ruta API asociada

`/api/mobile/command-center`

### Componente confirmado

`src/components/prisma-app/PrismaMobileCommandCenter.tsx`

### Intención visual

Presentar decisiones o señales de mando de forma priorizada.

### Archivos a revisar

- componente visual
- engine/contract asociado en `src/lib/prisma-app`
- API route correspondiente

## 6. Action Inbox

### Ruta API asociada

`/api/mobile/action-inbox`

### Componente confirmado

`src/components/prisma-app/PrismaMobileActionInbox.tsx`

### Intención visual

Mostrar acciones pendientes o recomendaciones operativas.

### Consideraciones

- priorización
- estado de acción
- severidad
- fecha/hora
- branch/source si aplica
- empty state claro

## 7. Daily Brief

### Ruta API asociada

`/api/mobile/daily-brief`

### Componente confirmado

`src/components/prisma-app/PrismaMobileDailyBrief.tsx`

### Intención visual

Resumen ejecutivo diario. Debe evitar exceso de ruido y privilegiar lectura rápida.

## 8. Decision Ledger

### Ruta API asociada

`/api/mobile/decision-ledger`

### Componente confirmado

`src/components/prisma-app/PrismaMobileDecisionLedger.tsx`

### Intención visual

Historial o bitácora de decisiones. Debe mantener claridad temporal y trazabilidad.

## 9. Pulse Timeline

### Ruta API asociada

`/api/mobile/pulse-timeline`

### Componente confirmado

`src/components/prisma-app/PrismaMobilePulseTimeline.tsx`

### Intención visual

Línea de tiempo del pulso operativo. Cambios aquí deben cuidar orden temporal, agrupación y densidad visual.

## 10. Health Radar

### Ruta API asociada

`/api/mobile/health-radar`

### Componente confirmado

`src/components/prisma-app/PrismaMobileHealthRadar.tsx`

### Intención visual

Estado de salud operativa. Cambios visuales deben conservar lectura de severidad y causa.

## 11. PWA Install

### Ruta

`/prisma-app/install`

### Archivos confirmados

- `app/prisma-app/install/page.tsx`
- `src/components/prisma-app/PrismaMobilePwaInstallCard.tsx`
- `src/components/prisma-app/PrismaMobilePwaRuntime.tsx`

### Riesgo confirmado

El ZIP referencia PNGs PWA no presentes. Cualquier cambio visual/install debe revisar `manifest.webmanifest`, service worker/runtime y assets reales en `public`.

## 12. Offline

### Ruta

`/prisma-app/offline`

### Archivo confirmado

`app/prisma-app/offline/page.tsx`

### Intención visual

Explicar estado offline sin parecer crash. Debe separar: sin conexión, datos stale, cache disponible y recuperación esperada.

## 13. Assets visuales confirmados

Confirmados presentes en el snapshot:

- `public/icons/prisma-app-icon.svg`
- `public/icons/prisma-app-maskable.svg`
- `public/icons/prisma-app-monochrome.svg`
- `public/icons/prisma_playstore_icon(1).svg`
- `public/icons/prisma_playstore_icon(2).svg`
- `public/screenshots/prisma-mobile-pwa-dashboard.png`

Referenciados pero pendientes de confirmar porque no están presentes en el ZIP:

- `public/icons/prisma_playstore_icon_192.png`
- `public/icons/prisma_playstore_icon_512.png`
- `public/apple-touch-icon.png`
- `public/apple-touch-icon-precomposed.png`
- `public/icons/prisma_ios_touch_icon_180.png`
- `public/icons/prisma_whatsapp_install_icon.png`

## 14. Verificación visual mínima

Antes de aceptar un cambio visual Mobile:

1. Abrir `/prisma-app`.
2. Abrir `/prisma-app/install`.
3. Abrir `/prisma-app/offline`.
4. Probar estados loading/error/empty/stale cuando existan fixtures o mocks.
5. Correr typecheck/build.
6. Correr verificadores de PWA y navigation si están disponibles.

## 15. Rollback visual

Rollback seguro por capas:

1. Revertir componente visual tocado.
2. Revertir CSS local Mobile si se tocó.
3. No revertir ni editar Shared UI/shared styles desde Mobile sin confirmar ownership.
4. Si cambió contrato API, revertir también consumers y route handler juntos.

