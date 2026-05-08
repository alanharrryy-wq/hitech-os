<!-- Coordinator consolidated on 2026-05-08 from four worker result ZIPs. -->

# ATLAS MASTER INDEX

Estado: **aprobado para integración de atlas con advertencias**. Esta aprobación cubre documentación y trazabilidad; no significa release verde de Mobile/Tablet/PC porque algunos verificadores reportaron fallos o dependencias externas ausentes.

## Atlases consolidados

| App | Atlas ID | Root | Intenciones | Superficies | Verificación | Estado |
|---|---|---|---:|---:|---:|---|
| mobile | `ATLAS_MOBILE_INITIAL_2026_05_08_V2` | `products/mobile/app` | 19 | 19 | 18 | PASS |
| tablet | `ATLAS_TABLET_INITIAL_FROM_ATLAS_CHAT_TABLET_ZIP` | `products/tablet/app` | 8 | 5 | 7 | PASS |
| pc | `ATLAS_PC_COORDINATOR_NORMALIZED_2026_05_08` | `products/pc/app` | 15 | 83 | 34 | PASS |
| shared | `ATLAS_SHARED_CORE` | `shared-core` | 8 | 4 | 5 | PASS |

## Ownership

- Mobile: `products/mobile/app/docs/atlas/**`.
- Tablet: `products/tablet/app/docs/atlas/**`.
- PC: `products/pc/app/docs/atlas/**`.
- Shared Core: `docs/atlas/**`, contratos compartidos, Visual OS, Prisma/global DB, shared UI, licensing y runtime común.

## Hallazgos del Coordinador

- Los 4 ZIPs entregaron todos los archivos esperados.
- `atlas.pc.json` fue normalizado por Coordinador porque la entrega original no seguía el schema canónico.
- No se detectaron duplicados de `intentId` después de la normalización.
- No se detectó traslape bloqueante de ownership entre Mobile, Tablet, PC y Shared Core.
- Mobile y Tablet documentan fallos de verificadores/runtime; quedan como advertencia de release, no como bloqueo del atlas.

## Archivos principales

- `products/mobile/app/docs/atlas/atlas.mobile.json`
- `products/tablet/app/docs/atlas/atlas.tablet.json`
- `products/pc/app/docs/atlas/atlas.pc.json`
- `docs/atlas/atlas.shared-core.json`

## Siguiente uso recomendado

Usar `atlas.registry.json` como mapa mecánico y los Markdown como lectura humana. Cuando se pida cambiar una función, primero buscar la intención equivalente en el atlas del producto y luego revisar Shared Core si aparece como dependencia.
