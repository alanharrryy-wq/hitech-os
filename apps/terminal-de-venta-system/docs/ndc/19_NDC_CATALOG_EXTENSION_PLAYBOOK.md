# 19. NDC Catalog Extension Playbook

> Estado: complemento de canon. Define cómo agregar catálogos, paneles, métricas, widgets, evidence sources y handoff targets sin romper compatibilidad.

## Principio

Todo incremento entra como record, edge, evidence o curation. Ningún incremento nace editando una matriz generada.

## Checklist para un catálogo nuevo

1. Declarar familia.
2. Declarar propósito.
3. Declarar records consumidos.
4. Declarar edges requeridos.
5. Declarar evidencia aceptada.
6. Declarar curation permitida.
7. Declarar exports.
8. Declarar readiness.
9. Declarar si alimenta Prisma OCR después.
10. Declarar anti-fake-green.

## Checklist para panel/widget nuevo

- UI ID ubica, no gobierna.
- Debe ligar a surface_id.
- Debe ligar a neutral_object_id o explicar por qué es navegación/estado puro.
- Si dispara escritura, debe ligar a ACT.* y EVT.*.
- Si muestra dato, debe ligar a MET.*, ENT.*, CAN.* o Data_Binding_Map.
- Si es cliente-facing, debe declarar role/license/scope.

## Checklist para métrica/chart nuevo

- MET.*
- formula_id
- dataset_contract_id
- grain
- scope
- canonical dependency
- surface destinations
- license/pricing
- evidence
- no-humo status

## Versionado

Los catálogos se incrementan por append-compatible fields. Si un campo se elimina o cambia semántica, se crea nueva versión y migration note documental.
