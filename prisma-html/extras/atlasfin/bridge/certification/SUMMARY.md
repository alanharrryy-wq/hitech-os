# Chat 5 Atlasfin Corpus Reference Certification

Status: `CERTIFIED_REFERENCE_CORPUS`

## Provenance

- Certification base: `8cc1918c5e015d1408335c15313e7364e04859c2`
- Source bridge: `chat5-atlasfin-bridge-20260904@c5ef78edcc1bcb50ca7b108e316cdc0dbe1034d0`
- Raw surface heads:
  - Tablet: `1b669d98dc9063fe4d6f5f8ddc06262a6968e728`
  - PC: `896f4a7f3463dc4ad1267f3e7d8f6a9fd70f4078`
  - Mobile: `7f32ce6f1b602a14781fa2f4f3f323035f8029ec`
  - Shared UI: `57b502f1064571cebd917b36882ef9c11e9fa7d8`

## Certification result

The exact raw corpus contains **2,097** surface outcome records. Across those records, **2,421 non-null Atlasfin references** were found and certified against current structured Atlasfin authority.

- hard invalid Atlasfin refs: **0**
- semantic mutations: **0**
- representation-only normalizations: **341**
- Materiality Catalog inspected: **false**
- canonical promotion performed: **false**
- product/runtime mutation performed: **false**

The 341 representation conversions are the qualified adapter values already present in the raw Mobile and Shared UI workers. The strict derivative representation strips only the `atlasfin::` domain prefix inside `atlasfin.*` fields while preserving the original serialized value and source-record hash in certification evidence. Authority-qualified evidence references remain qualified.

## Re-derived recipe review groups

| Atlasfin recipe | Tablet | PC | Total | Meaning |
|---|---:|---:|---:|---|
| `REC.table.governed.v2` | 66 | 105 | 171 | review-only convergence |
| `REC.card.governed.v2` | 41 | 54 | 95 | review-only convergence |
| `REC.panel.governed.v2` | 20 | 27 | 47 | review-only convergence |
| `REC.overlay.governed.v2` | 11 | 0 | 11 | Tablet-only review group |

Equal Atlasfin recipe IDs are **not** proof of one shared neutral meaning. They do not assign NDC meaning, Identity recipe, binding, application authority or canonical IDs. All-null and `NO_MATCH` records are excluded from semantic coalescing.

## Authority boundary

Atlasfin remains the priority human cockpit/reference, not a second editable Identity/RIFAT authority. The existing 418-element catalog is reused, not rebuilt. Materiality Catalog remains `STANDBY_USER_INVOKED_ONLY` and was not inspected.

No PR is opened by Chat 5 for this phase. `prisma-html/FILES_MANIFEST.json` remains integration-owned.
