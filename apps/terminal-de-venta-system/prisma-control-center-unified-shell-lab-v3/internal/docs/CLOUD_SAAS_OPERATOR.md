# PRISMA Cloud Private Cockpit Operator

Este lab corre localmente en `127.0.0.1:3160` y opera como cockpit privado para `https://app.hitechrts.com`.

## Abrir

1. Ejecutar `00_ABRIR_UNIFIED_SHELL_LAB_V3.cmd`.
2. Abrir `http://127.0.0.1:3160/unified-shell.html`.
3. Entrar al modulo `PRISMA Cloud` o a la pestana lateral `Cloud SaaS`.

## Modos

- `LOCAL_FULL`: host local y token admin local disponible.
- `READ_ONLY_TOKEN_MISSING`: host local sin token admin local.
- `READ_ONLY_PUBLIC_HOST`: host no local; bloquea acciones sensibles.

El token se busca localmente bajo las carpetas recientes `prcloud*` de `F:/descargasf`, pero nunca se entrega al navegador ni a reportes.

## Acciones disponibles

- Crear nota admin para `demo-prisma`.
- Enviar smoke de integration receipt.
- Enviar smoke de device register.
- Consultar health, capabilities, tenant status, snapshot, commercial summary y contrato.
- Ver estado de licencias local adaptado desde el modulo de 3150 en modo read-only.

Si el puerto `3160` ya estaba corriendo antes del parche, no se mata el proceso. Cierra y reabre el lab con el CMD existente para cargar la version nueva.
