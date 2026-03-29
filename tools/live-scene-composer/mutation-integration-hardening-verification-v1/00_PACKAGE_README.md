# Live Scene Composer | Mutation Integration Hardening + Verification Pack v1

Este paquete cierra la wave de `mutation-client` con dos objetivos prácticos:

1. **endurecer la instalación** del seam `Mutation Client + Bridge Preview/Commit`
2. **dejar evidencia verificable** después de instalar, para que el operador no se quede solo con el mensaje `Bundle launcher completado`

## Qué resuelve

- instala los docs canónicos y los deja apilados sobre los bundles previos
- stagea una versión completa del `mutation-client` y un seam adicional de `mutation-integration`
- opcionalmente espejea estos seams dentro del `composer src root` detectado
- ejecuta una verificación post-install con reportes `.txt` y `.json`
- ejecuta smoke checks estructurales y, cuando hay tooling disponible, checks adicionales de guard o toolchain
- deja toda la evidencia en `F:\OneDrive\Descargas`

## Qué NO hace

- no promete que el repo ya integra toda la lógica real del producto
- no fuerza commits ni mutaciones reales en runtime
- no trata preview como commit
- no salta `runtime-mutation-bridge`

## Entry points principales

- `install_live_scene_composer_mutation_integration_hardening_verification_v1.ps1`
- `run_live_scene_composer_mutation_integration_hardening_verification_v1_from_zip.ps1`
- `verify_live_scene_composer_mutation_integration_hardening_v1.ps1`
- `invoke_live_scene_composer_mutation_smoke_checks_v1.ps1`

## Resultado esperado

Al terminar, el operador debe poder responder con evidencia concreta:

- qué docs se copiaron
- qué source pack quedó stageado
- si hubo mirror a `composer src root`
- qué checks pasaron, fallaron o se saltaron
- dónde quedaron los logs y reportes
