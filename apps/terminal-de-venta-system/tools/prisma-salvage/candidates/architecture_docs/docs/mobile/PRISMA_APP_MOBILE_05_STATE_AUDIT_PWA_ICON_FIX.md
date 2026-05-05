# PRISMA App Mobile 05 - State audit + PWA icon fix

## Estado leído desde ZIP

ZIP revisado: `terminal_de_venta_chatgpt_share.zip`

Sin tocar código transaccional, el estado real de la superficie Mobile es:

- La raíz canónica existe en `products/mobile/app`.
- La ruta principal existe en `products/mobile/app/app/prisma-app/page.tsx`.
- La app móvil ya no está registrada como hija de PC.
- La intención de producto está clara: PRISMA App consulta, resume y alerta; Tablet vende sola; PC administra cuando existe.
- Hay scaffold PWA/TWA y documentos de Play Store readiness.
- No hay APIs reales bajo `app/api/mobile/**`; por ahora los contratos aparecen como rutas futuras documentadas.
- La UI actual usa demo data estática desde `src/lib/prisma-app/prisma-app-demo-data.ts`.

## Hallazgo bloqueante corregido

El manifest PWA declara estos iconos:

```text
/icons/prisma-app-icon.svg
/icons/prisma-app-maskable.svg
/icons/prisma-app-monochrome.svg
```

Pero en el ZIP sólo venían:

```text
/icons/prisma_playstore_icon(1).svg
/icons/prisma_playstore_icon(2).svg
```

Resultado: `verify:pwa` fallaba porque el manifest apuntaba a archivos inexistentes. Clásico caso de ponerle domicilio al repartidor y luego cambiarle la fachada.

Esta entrega agrega los tres iconos esperados por el manifest, sin borrar los iconos temporales existentes.

## Validaciones locales realizadas

Desde la copia extraída del ZIP:

```text
node products/mobile/app/tools/verify_prisma_app_mobile_03_product_root_rebase.mjs
  PASS

cd products/mobile/app && node tools/verify_prisma_mobile_pwa_readiness.mjs
  FAIL antes de esta entrega: manifest icon path not found
  PASS después de agregar iconos esperados

cd products/mobile/app && node tools/verify_prisma_mobile_playstore_readiness.mjs
  PASS
```

## Lo que sigue para desarrollo real

Orden recomendado:

1. `PRISMA_APP_MOBILE_06_API_CONTRACTS`
   - Crear `app/api/mobile/summary`, `sales/today`, `cash/current`, `inventory/watchlist`, `alerts`, `reports/daily`, `branches`.
   - Responder todavía con demo data, pero ya con contrato HTTP real.

2. `PRISMA_APP_MOBILE_07_DATA_ADAPTERS`
   - Separar fixtures de adapters.
   - Preparar consumo posterior de agregados PC/sync sin amarrar Mobile al backoffice como changarro pegado con cinta gris.

3. `PRISMA_APP_MOBILE_08_REAL_MOBILE_UX_PASS`
   - Convertir el blueprint largo en navegación móvil real por pantallas/secciones.
   - Mantener dashboard ejecutivo ligero, no sábana de Excel con complejo de mural.

## No-goals de esta entrega

- No crea APIs reales.
- No cambia PC.
- No cambia Tablet.
- No toca shared-kernel.
- No publica Play Store.
- No genera `.aab`.
- No mete autenticación todavía.
