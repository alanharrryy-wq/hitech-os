# ATLAS MOBILE RUNTIME DELIVERY

## 1. Propósito

Este documento registra runtime, delivery, PWA, verificación y riesgos de despliegue de Mobile según el contenido confirmable del ZIP `ATLAS_CHAT_MOBILE.zip`.

No modifica código funcional. No toca rutas finales. No declara propiedad sobre Android tooling, Cloudflare tooling, Tablet, PC o Shared Core cuando esos archivos no están dentro del snapshot Mobile.

## 2. Runtime confirmado

El snapshot Mobile se identifica como app Next/PWA ubicada en:

`source_snapshot/products/mobile/app`

Archivos de configuración confirmados por el paquete:

- `package.json`
- `next.config.mjs`
- `tsconfig.json`
- `postcss.config.mjs`
- `tailwind.config.ts`
- `app/*`
- `public/*`
- `scripts/*`

## 3. Stack observado

Desde el `package.json` del snapshot Mobile se observó la intención de runtime moderna basada en Next, React y TypeScript. Las versiones exactas deben confirmarse contra el repo actual antes de tocar dependencias.

Dependencias relevantes observadas durante la revisión de Ronda 2:

- Next
- React
- TypeScript
- Zod

Restricción de Node observada:

- `>=20.0.0 <26.0.0`

## 4. PWA delivery

Archivos/superficies PWA confirmadas o referenciadas:

- `public/manifest.webmanifest`
- PWA runtime/service worker bajo `public` cuando esté presente en el snapshot
- `src/components/prisma-app/PrismaMobilePwaInstallCard.tsx`
- `src/components/prisma-app/PrismaMobilePwaRuntime.tsx`
- `app/prisma-app/install/page.tsx`
- `app/prisma-app/offline/page.tsx`

## 5. Hallazgo crítico PWA

El ZIP referencia PNGs que no están presentes en el snapshot. Este atlas no inventa esos assets ni los marca como existentes.

Referencias pendientes de confirmar:

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

### Implicación

`verify:pwa` no debe considerarse verde desde este ZIP hasta resolver el gap de assets o corregir referencias. Es como tener llave, chapa y puerta, pero el letrero de entrada apunta a una calle que no existe.

## 6. Offline delivery

Ruta confirmada:

`/prisma-app/offline`

Archivo confirmado:

`app/prisma-app/offline/page.tsx`

El offline flow debe revisarse junto con:

- service worker/runtime PWA
- cache/snapshot utilities
- estados stale/degraded en UI

## 7. Data plane runtime

Raíz confirmada:

`src/lib/prisma-app/mobile-data-plane`

Variables de configuración observadas o derivadas del snapshot:

- `PRISMA_MOBILE_TABLET_ORIGIN`
- `PRISMA_MOBILE_PC_ORIGIN`
- `PRISMA_MOBILE_SOURCE_TIMEOUT_MS`
- `PRISMA_MOBILE_RETRY_COUNT`
- `PRISMA_MOBILE_STALE_AFTER_MS`
- `PRISMA_MOBILE_LOW_STOCK_THRESHOLD`
- `PRISMA_MOBILE_OVERSTOCK_THRESHOLD`

Defaults observados en revisión:

- Tablet: `http://127.0.0.1:3120`
- PC: `http://127.0.0.1:3130`
- Mobile: `http://127.0.0.1:3140`

Tablet y PC son dependencias externas para Mobile.

## 8. Scripts de verificación observados

El snapshot contiene referencias a scripts/verificadores como:

- `verify:pwa`
- `verify:playstore-readiness`
- `verify:production-data`
- `verify:hydration`
- `verify:command-center`
- `verify:action-inbox`
- `verify:daily-brief`
- `verify:decision-ledger`
- `verify:pulse-timeline`
- `verify:health-radar`
- `verify:data-plane-types`
- `verify:runtime-error-guard`
- `verify:premium-navigation`
- `verify:data-readiness`
- `verify:source-states`
- `verify:release-hardening`
- `verify:mando`
- `typecheck`
- `build`

## 9. Verificación confirmada durante Ronda 2

### Confirmado verde

- `verify:release-hardening` pasó en revisión local del paquete.
- `atlas.mobile.json` parseó correctamente antes del staging.

### Confirmado con falla esperada desde ZIP parcial

- `verify:pwa` falla por assets PNG faltantes referenciados.
- Cualquier verificador que dependa de Android tooling externo puede fallar porque el ZIP no incluye todo el árbol Android/infra.

## 10. Limitación del ZIP como build aislado

El ZIP funciona como paquete de contexto y atlas, pero no debe tratarse como repo completo. Se observaron referencias a recursos externos o rutas de monorepo que no están físicamente incluidas en el snapshot Mobile.

Categorías externas:

- Shared UI
- shared visual styles
- Android tooling
- Cloudflare/infra scripts
- Tablet/PC services
- Shared Core

## 11. Delivery readiness checklist

Antes de mover contenido desde staging a una ruta final de atlas o usarlo para cambios funcionales:

1. Confirmar que los 10 archivos estén en `docs/atlas/_incoming/mobile/`.
2. Validar `atlas.mobile.json` con parser JSON.
3. Confirmar que no se modificó `products/mobile/app/docs/atlas/`.
4. Confirmar que no se tocaron carpetas Tablet, PC ni Shared Core.
5. Confirmar que assets PWA faltantes están resueltos o documentados como blocking issue.
6. Correr `typecheck` y `build` desde repo completo.
7. Correr verificadores PWA/runtime/data plane desde repo completo.

## 12. Rollback de delivery

Como esta entrega es solo staging documental, rollback seguro:

```bash
git rm docs/atlas/_incoming/mobile/ATLAS_MOBILE.md
git rm docs/atlas/_incoming/mobile/ATLAS_MOBILE_VISUAL.md
git rm docs/atlas/_incoming/mobile/ATLAS_MOBILE_INTERACTION.md
git rm docs/atlas/_incoming/mobile/ATLAS_MOBILE_FUNCTIONAL_ENGINES.md
git rm docs/atlas/_incoming/mobile/ATLAS_MOBILE_RUNTIME_DELIVERY.md
git rm docs/atlas/_incoming/mobile/atlas.mobile.json
git rm docs/atlas/_incoming/mobile/RESULT_SUMMARY.md
git rm docs/atlas/_incoming/mobile/FILE_MANIFEST.json
git rm docs/atlas/_incoming/mobile/OPEN_QUESTIONS.md
git rm docs/atlas/_incoming/mobile/COVERAGE_NOTES.md
```

No se requiere rollback de código funcional porque esta entrega no modifica código funcional.
