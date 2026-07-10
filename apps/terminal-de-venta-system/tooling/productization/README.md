<!-- PRISMA_LICENSING_CANON_GUARD:START -->
# PRISMA Productization Tooling

Este directorio es el canon para schemas, examples, fixtures de producto, runtime config, catálogos y test-cases de productización.

## No hacer

- No usar esta carpeta como basurero de ZIPs históricos.
- No mezclar runtime cloud real con examples.
- No borrar examples duplicados sólo porque también existen fixtures técnicos en `tooling/licensing`.

## Hacer

- Guardar aquí schemas, examples, catalog files, runtime config examples y test-cases.
- Mantener la separación:
  - `tooling/licensing` = tooling técnico.
  - `tooling/productization` = producto, schemas y examples.
  - `docs/productization` = contrato.
  - `docs/ndc` = significado neutral.
  - `Prisma Cloud Ctr` e `infra/cloudflare/licflow3-worker` = runtime/data boundary.

Ver flujo completo en:

`docs/productization/PRISMA_LICENSE_PRODUCTIZATION_FLOW.md`

Última actualización por paquete: `licdoc3 1007 1001`.
<!-- PRISMA_LICENSING_CANON_GUARD:END -->
