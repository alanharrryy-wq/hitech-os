# PRISMA BLACK-BOX i02 - Runtime Supervisor

## Objetivo

Agregar a black-box la capacidad de arrancar, vigilar y detener procesos propios de Tablet, PC y Mobile con logs y diagnostico.

## Alcance

- `start tablet|pc|mobile|all`
- `stop owned`
- `restart tablet|pc|mobile|all`
- `watch`
- conserva `doctor`, `status`, `last-error`, `collect`, `repair plan`, `repair apply --safe`

## Seguridad

- No toca `shared-kernel`.
- No toca DB destructivamente.
- No mata procesos ajenos.
- Solo detiene PIDs que black-box registro en `tools/_local/black-box/runtime_state.json`.

## Estado esperado

READY si instala, verifica y el self-test corre.
READY_WITH_CAVEATS si el self-test pasa pero no se pudo hacer smoke runtime por dependencias locales.
BLOCKED si falla manifest, checksum, lane, apply o verify.
