# PRISMA App Mobile 19 - Hydration Guard

## Diagnóstico

El error reportado fue un desajuste de hidratación en `LoadingShell`: el HTML inicial y el bundle del cliente no traían el mismo texto de carga. El síntoma apareció justo después de aplicar una inyección en caliente con Next/Turbopack activo.

## Causa probable

El componente era estático, pero el dev server podía conservar una versión vieja del módulo mientras el cliente ya compilaba la nueva. Resultado: React detectaba dos textos distintos en el mismo nodo `<p>` y regeneraba el árbol en cliente.

## Corrección

- El texto de carga queda centralizado en `LOADING_SHELL_COPY`.
- El nodo `<p>` de carga usa `suppressHydrationWarning` para tolerar una transición de caché dev sin romper la ruta.
- Se agrega `dev:clean-cache` para limpiar `.next` de forma explícita.
- Se repara `package.json` para que no apunte a validadores retirados por la inyección 18.
- Se agrega gate `verify:hydration` con detección robusta de raíz.

## Uso recomendado después de aplicar

Desde `products/mobile/app`:

```powershell
pnpm run dev:clean-cache
pnpm run verify:hydration
pnpm run dev
```

Si el servidor de desarrollo está prendido, ciérralo antes de limpiar `.next` para que Windows no agarre archivos como perro con hueso.
