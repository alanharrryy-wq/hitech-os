# ATLAS_MASTER_INDEX

**Estado:** borrador inicial.  
**Nota:** este índice debe validarse después contra los atlas Mobile, Tablet y PC.

## Atlas registrados

| Atlas | Ruta | Estado |
| --- | --- | --- |
| Shared Core | `docs/atlas/ATLAS_SHARED_CORE.md` | Borrador inicial generado en este paquete. |
| Mobile | Pendiente de confirmar | No incluido en `ATLAS_CHAT_SHARED_CORE.zip`. |
| Tablet | Pendiente de confirmar | No incluido en `ATLAS_CHAT_SHARED_CORE.zip`. |
| PC | Pendiente de confirmar | No incluido en `ATLAS_CHAT_SHARED_CORE.zip`. |

## Shared Core subíndices

- `docs/atlas/ATLAS_SHARED_CORE_CONTRACTS.md`
- `docs/atlas/ATLAS_SHARED_CORE_VISUAL_OS.md`
- `docs/atlas/ATLAS_SHARED_CORE_FUNCTIONAL_ENGINES.md`
- `docs/atlas/ATLAS_SHARED_CORE_RUNTIME_INFRA.md`
- `docs/atlas/atlas.shared-core.json`

## Reglas para consolidación posterior

1. No duplicar detalle interno de apps en Shared Core.
2. Mobile/Tablet/PC deben apuntar a Shared Core cuando un cambio toque contrato, Visual OS, licencia, Prisma/global DB, runtime común o tooling global.
3. `atlas.registry.json` debe volverse la fuente de indexación cuando los cuatro atlas estén disponibles.
4. Cualquier ruta no confirmada por el ZIP o por atlas futuros queda como pendiente de confirmar.
