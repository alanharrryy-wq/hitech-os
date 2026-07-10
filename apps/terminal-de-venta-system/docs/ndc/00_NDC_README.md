# PRISMA NDC Canon Documental

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Propósito

Este docset define la mecánica completa del **Neutral Data Center / NDC Matrix Substrate** para PRISMA. No inventaría pantallas primero. Define scope, significado, relaciones, evidencia, curation, proyecciones canónicas y matrices generadas.

Frase madre:

```text
PRISMA no necesita primero un inventario de pantallas. Necesita un registro neutral de scope y significado, donde cada tenant, negocio, tienda, dispositivo, evento, dato, acción y superficie tenga identidad trazable. Las pantallas sólo son proyecciones de esa verdad.
```

## Capas

```text
TENANT SCOPE → BUSINESS SCOPE → STORE/SITE SCOPE → DEVICE/SURFACE SCOPE → EVENT PROVENANCE → CANONICAL PROJECTION → APP/SURFACE REPRESENTATION → UI COMPONENT
```

## Archivos

| Archivo | Función |
|---|---|
| `01_NDC_CANON_AND_DOCTRINE.md` | doctrina, autoridad, anti-patrones. |
| `02_NDC_ID_GRAMMAR_AND_NAMING.md` | gramática de IDs, prefijos, aliases. |
| `03_NDC_SCOPE_MODEL.md` | tenant/business/store/device/license/role/session. |
| `04_NDC_NEUTRAL_OBJECT_MODEL.md` | ENT/EVT/ACT/STA/MET/ALT/EVD/CAP/CAN. |
| `05_NDC_EVENT_ACTION_STATE_MODEL.md` | acciones, eventos, estados y envelopes. |
| `06_NDC_PROVENANCE_SYNC_LINEAGE.md` | provenance, sync, outbox, lineage y drift. |
| `07_NDC_CANONICAL_PROJECTION_MODEL.md` | canonical projections, status y promotion. |
| `08_NDC_CAPABILITY_LICENSE_MODULE_MODEL.md` | capabilities, modules, licenses, no-humo. |
| `09_NDC_SURFACE_UI_CHART_ATLAS.md` | surfaces, UI, panels, widgets, charts. |
| `10_NDC_EVIDENCE_CURATION_GOVERNANCE.md` | evidence, curation, gates. |
| `11_NDC_MATRIX_AND_CATALOG_VIEW_SYSTEM.md` | catálogo completo de matrices y vistas. |
| `12_NDC_PRISMA_OCR_HANDOFF_BLUEPRINT.md` | blueprint futuro para DB, sin DB todavía. |
| `13_NDC_EXAMPLES_AND_RECIPES.md` | ejemplos y recetas. |
| `14_NDC_NEXT_ITERATION_CONTRACT.md` | contrato para normalize2/curate1/db1. |

## Principios

1. Lo neutral define significado.
2. Lo específico define ubicación.
3. Toda matriz es vista/export, nunca fuente.
4. Toda corrección humana vive en curation.
5. Todo objeto visible rastrea a neutral object.
6. Todo dato proyectado conserva tenant, scope, provenance y canonical status.
7. Sin evento no hay reporte. Sin evidencia no hay PRISMA.


## Repack note

Este repack `ndc canon1 0907 0845` corrige el gate `Matrix doc too thin` expandiendo `11_NDC_MATRIX_AND_CATALOG_VIEW_SYSTEM.md` y agregando `19_NDC_CATALOG_EXTENSION_PLAYBOOK.md`. La intención no es bajar el gate; es cumplirlo con documentación más sustanciosa.
