# Pilot 06 · POS Final Gate Audit

## Objetivo

Instalar un contrato verificable antes de tocar POS. Este piloto no rediseña POS, no toca checkout, no toca DB, no instala dependencias y no hace deploy.

## Gate visual POS

POS sólo podrá aceptar recetas futuras si son `light-only`, `touch-first`, de bajo blur, sin WebGL, sin Pixi vapor, sin dark storm y sin fondos que compitan con producto/cobro.

## Evidencia esperada

El instalador genera un ZIP de resultado en `<OUTPUT_DIR>` con logs, receipt, hashes protegidos, scan POS y salida del verificador.

## Siguiente paso

Si este gate pasa, el siguiente piloto puede aplicar un shell POS light-safe mínimo con rollback y aceptación visual estricta.
