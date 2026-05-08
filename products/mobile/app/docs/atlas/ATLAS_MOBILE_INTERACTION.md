# ATLAS MOBILE INTERACTION

## 1. Propósito

Este documento describe los flujos de interacción confirmados o inferibles desde el snapshot Mobile del ZIP `ATLAS_CHAT_MOBILE.zip`, sin inventar rutas ni responsabilidades externas.

La meta es que un cambio futuro parta de una intención humana clara y llegue a archivos, rutas, verificadores y rollback sin andar tanteando como si el repo fuera un cuarto oscuro lleno de Legos.

## 2. Principios de interacción Mobile

Mobile debe comportarse como una superficie de supervisión rápida:

- lectura primero, edición solo si está confirmada por código;
- decisiones visibles;
- estados offline/stale claros;
- navegación corta;
- feedback inmediato ante fallas de datos;
- densidad compatible con pantalla móvil.

No se documenta Mobile como propietario de flujos Tablet, PC o Shared Core.

## 3. Flujo: entrada al dashboard

### Intención humana

Abrir la app y entender el estado operativo actual.

### Ruta

`/prisma-app`

### Archivos a revisar

- `app/prisma-app/page.tsx`
- `src/components/prisma-app/PrismaMobileDashboard.tsx`
- `src/components/prisma-app/PrismaMobilePremiumNavigator.tsx`
- `src/lib/prisma-app/*` relacionado con snapshot/summary/formatters

### APIs relacionadas

- `/api/mobile/summary`
- `/api/mobile/snapshot`
- `/api/mobile/sales/today`
- `/api/mobile/cash/current`
- `/api/mobile/inventory/watchlist`
- `/api/mobile/alerts`
- `/api/mobile/health`

### Estados que deben conservarse

- loading
- loaded
- error
- stale data
- offline or degraded source
- empty state cuando una fuente no devuelve datos

### Verificación

- typecheck
- build
- smoke manual de `/prisma-app`
- verificadores de runtime/error guard si existen en el repo completo

### Rollback

Revertir cambios en page/componentes y cualquier ajuste de contract asociado. No tocar Shared Core como rollback de Mobile.

## 4. Flujo: navegación premium

### Intención humana

Cambiar entre superficies de supervisión avanzada.

### Componente principal

`src/components/prisma-app/PrismaMobilePremiumNavigator.tsx`

### Superficies destino

- Command Center
- Action Inbox
- Daily Brief
- Decision Ledger
- Pulse Timeline
- Health Radar

### Archivos a revisar

- `PrismaMobilePremiumNavigator.tsx`
- componentes `PrismaMobile*` de cada superficie
- APIs `/api/mobile/*` correspondientes

### Verificación

- `verify:premium-navigation` si está disponible
- smoke manual de todas las tabs/secciones
- confirmar que labels y destinos no quedan huérfanos

### Rollback

Revertir navigator y mantener contratos de datos sin cambios salvo que el cambio haya tocado APIs.

## 5. Flujo: instalación PWA

### Intención humana

Instalar o preparar la app como PWA.

### Ruta

`/prisma-app/install`

### Archivos a revisar

- `app/prisma-app/install/page.tsx`
- `src/components/prisma-app/PrismaMobilePwaInstallCard.tsx`
- `src/components/prisma-app/PrismaMobilePwaRuntime.tsx`
- `public/manifest.webmanifest`
- service worker/runtime PWA bajo `public` si existe

### Riesgo confirmado

El ZIP referencia PNGs que no están presentes. El flujo PWA no debe considerarse release-ready desde este ZIP hasta resolver assets faltantes o ajustar referencias.

### Verificación

- `verify:pwa`
- manifest parse
- icon existence check
- instalación manual en navegador compatible

### Rollback

Revertir manifest/runtime/install card. No crear ni borrar assets externos sin confirmar propiedad.

## 6. Flujo: offline

### Intención humana

Entender que la app no tiene conexión o que está usando datos cacheados/degradados.

### Ruta

`/prisma-app/offline`

### Archivo confirmado

`app/prisma-app/offline/page.tsx`

### Archivos relacionados

- PWA runtime
- service worker si está presente
- snapshot/cache utilities en `src/lib/prisma-app`

### Verificación

- cargar app sin red
- revisar fallback `/prisma-app/offline`
- confirmar que no parezca crash de Next
- revisar que el usuario pueda volver o reintentar

### Rollback

Revertir fallback/offline page y runtime PWA relacionado.

## 7. Flujo: Command Center

### Intención humana

Ver señales priorizadas para tomar decisiones.

### Archivos

- `src/components/prisma-app/PrismaMobileCommandCenter.tsx`
- `app/api/mobile/command-center/route.ts`
- engine/contract asociado bajo `src/lib/prisma-app`

### Verificación

- respuesta API válida
- render de estados vacío/error/loading
- verifier específico si existe

## 8. Flujo: Action Inbox

### Intención humana

Ver acciones pendientes o recomendadas.

### Archivos

- `src/components/prisma-app/PrismaMobileActionInbox.tsx`
- `app/api/mobile/action-inbox/route.ts`
- engine/contract asociado

### Reglas de interacción sugeridas

- cada acción debe tener estado entendible;
- severidad o prioridad debe ser visible;
- si no hay acciones, empty state explícito.

## 9. Flujo: Daily Brief

### Intención humana

Leer un resumen diario compacto.

### Archivos

- `src/components/prisma-app/PrismaMobileDailyBrief.tsx`
- `app/api/mobile/daily-brief/route.ts`
- engine/contract asociado

### Riesgo

Sobrecargar el brief con demasiadas tarjetas lo vuelve periódico dominical, no brief. Mantener resumen corto.

## 10. Flujo: Decision Ledger

### Intención humana

Revisar decisiones pasadas con contexto temporal.

### Archivos

- `src/components/prisma-app/PrismaMobileDecisionLedger.tsx`
- `app/api/mobile/decision-ledger/route.ts`
- engine/contract asociado

### Cuidado

No romper orden temporal ni significado de estados.

## 11. Flujo: Pulse Timeline

### Intención humana

Ver eventos operativos en secuencia.

### Archivos

- `src/components/prisma-app/PrismaMobilePulseTimeline.tsx`
- `app/api/mobile/pulse-timeline/route.ts`
- engine/contract asociado

### Cuidado

Preservar orden, agrupación y legibilidad en móvil.

## 12. Flujo: Health Radar

### Intención humana

Entender salud operativa y riesgos.

### Archivos

- `src/components/prisma-app/PrismaMobileHealthRadar.tsx`
- `app/api/mobile/health-radar/route.ts`
- engine/contract asociado

### Cuidado

La severidad debe ser inequívoca. No esconder alertas críticas detrás de decoración visual.

## 13. Patrón de cambio seguro

Para cualquier cambio de interacción:

1. Identificar intención humana.
2. Identificar ruta visible.
3. Identificar componente Mobile.
4. Identificar API/engine si hay datos.
5. Revisar dependencias externas.
6. Correr verificación mínima.
7. Definir rollback.

