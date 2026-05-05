# PRISMA App Mobile 26 - Runtime Error Guard

## Objetivo

Corregir el runtime error opaco `[object Object]` observado en Next.js/Turbopack durante la carga de PRISMA App Mobile.

## Diagnóstico

La causa más probable era una promesa rechazada sin `catch` dentro del runtime PWA o del service worker. En desarrollo, el service worker anterior podía interceptar rutas `/_next/` y `/api/mobile/`, intentar escribir respuestas no cacheables o assets inexistentes y dejar rechazos en segundo plano. Next dev overlay los mostraba como `[object Object]`, o sea, el clásico "se rompió algo pero no te digo qué", muy útil si uno administra un circo.

## Cambios

- El runtime PWA ya no registra service worker en desarrollo salvo que se habilite explícitamente con `NEXT_PUBLIC_PRISMA_ENABLE_SW_DEV=1`.
- Si existe un service worker viejo de PRISMA Mobile en desarrollo, se desregistra para que no siga mordiendo rutas de Turbopack.
- El service worker usa `safeCachePut()` para que `CacheStorage` nunca deje rechazos sin manejar.
- Las respuestas offline de `/api/mobile/*` ahora regresan JSON controlado.
- El flujo de instalación Android captura errores del prompt PWA.
- Se agrega normalización de errores para evitar que objetos crudos lleguen como `[object Object]`.

## Validación

Ejecutar desde `products/mobile/app`:

```powershell
node tools/verify_prisma_app_mobile_26_runtime_error_guard.mjs
```

Resultado esperado:

```text
OK PRISMA_APP_MOBILE_26_RUNTIME_ERROR_GUARD service worker/dev overlay guards verified
```

## Nota operativa

Para probar service worker en desarrollo de forma intencional:

```powershell
$env:NEXT_PUBLIC_PRISMA_ENABLE_SW_DEV="1"
pnpm dev
```

No se recomienda tenerlo activo en el flujo diario de Turbopack porque el service worker puede dejar caché vieja y luego todos fingimos sorpresa, como si la tecnología no fuera una licuadora con WiFi.
