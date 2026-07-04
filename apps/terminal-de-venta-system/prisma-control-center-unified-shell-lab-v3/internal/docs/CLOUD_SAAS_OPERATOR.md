# Prisma Cloud Center Operator

Prisma Cloud Center corre localmente en `127.0.0.1:3160` y opera como consola de licencias para `https://app.hitechrts.com`.

## Abrir

1. Ejecutar `00_ABRIR_PRISMA_CLOUD_CENTER.cmd`.
2. Abrir `http://127.0.0.1:3160/unified-shell.html`.
3. Entrar al modulo `PRISMA Cloud` o a la pestana lateral `Cloud SaaS`.

## Modos

- `READ_ONLY_ADMIN_TOKEN_PRESENT`: host local y token admin presente, valor no leido.
- `READ_ONLY_NO_ADMIN_TOKEN`: host local sin token admin presente.
- `READ_ONLY_PUBLIC_HOST`: host no local; bloquea acciones sensibles.

Prisma Cloud Center detecta presencia de token, pero nunca lee el valor ni lo entrega al navegador o reportes.

## Acciones disponibles

- Ver LICFLOW3 como `LICFLOW3_CLOUDFLARE_ROUTES_LIVE`.
- Ver Worker `prisma-cloud-semilla` y D1 `prisma_cloud_semilla`.
- Ver activate/refresh/revoke con smoke esperado `401 ADMIN_TOKEN_REQUIRED` sin token.
- Consultar health, capabilities, tenant status, snapshot, commercial summary y contrato.
- Ver estado de licencias local adaptado desde el modulo de 3150 en modo read-only.

Las acciones admin/mutating quedan bloqueadas hasta LICFLOW4 Admin Bridge.

Si el puerto `3160` ya estaba corriendo antes del parche, no se mata el proceso. Cierra y reabre Prisma Cloud Center con el CMD existente para cargar la version nueva.
