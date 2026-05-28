# PRISMA Surface Visual Governor · Toolbox Hub

**Ubicación:** `<REPO_ROOT>\apps\terminal-de-venta-system\tools\prisma-surface-visual-governor`
**Generado:** 2026-05-27T11:37:13

Este folder es el **centro de mando local** del PRISMA Surface Visual Governor.

No reemplaza las rutas vivas de las apps. Las organiza, espejea e indexa para que el siguiente trabajo, especialmente motores `.py`, tenga una base limpia.

## Qué es esto

El Surface Visual Governor es el sistema que gobierna:

- Materiality Catalog
- Chart Lab Recipe Studio
- Route Budget Enforcer
- Surface Runtime Adapter
- Visual Regression Harness
- POS / Checkout gates
- Tablet light-first
- Mobile thin mist
- PC dashboard/reference
- EIT/Web public sober

## Carpetas principales

| Carpeta | Uso |
|---|---|
| `engines/python` | Reservado para próximos motores `.py` |
| `engines/node` | Verificadores/enforcers `.mjs` |
| `engines/powershell` | Wrappers paste-ready |
| `docs` | Documentación consolidada |
| `tooling` | Tooling existente espejeado |
| `contracts` | Policies, adapters, contracts |
| `public-mirrors` | Copias organizadas de `public/surface-visual-governor` por app |
| `evidence` | Índice y extractos de result ZIPs |
| `inventory` | Mapas generados |
| `scripts` | Scripts auxiliares y verifiers originales |

## Punto de entrada

Lee primero:

1. `TREE.md`
2. `inventory/source-map.json`
3. `evidence/result_zip_inventory.md`
4. `engines/python/engine_contract.md`

## Regla importante

No metas motores que modifiquen POS, checkout, DB, package manifests, lockfiles o deploy sin gate explícito y rollback.

Versión banqueta: aquí va la caja de herramientas fina. No avientes el taladro encima de la caja registradora.
