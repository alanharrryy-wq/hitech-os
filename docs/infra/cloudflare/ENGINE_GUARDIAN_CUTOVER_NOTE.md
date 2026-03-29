# Nota de cutover operativo hacia Engine Guardian v3

Esta nota existe para evitar dos verdades peleándose.

## Desde esta v3
La superficie oficial para scheduler, arranque, validación, heal y status del engine público pasa por:
- `engine_guardian`
- `igniters`
- tasks `HITECH-EngineGuardian-Boot` y `HITECH-EngineGuardian-Pulse`

## Lo que NO cambia
- no se reescriben internals de `tools\infra\cloudflare`
- scripts legacy siguen siendo wrapped dependencies
- tasks legacy pueden exportarse y deshabilitarse, pero no se borran de entrada
