# PRISMA_APP_MOBILE_03_PRODUCT_ROOT_REBASE

## Propósito

Esta entrega saca **PRISMA App / Mobile** del árbol técnico de PC y la convierte en una superficie de producto independiente junto a PC y Tablet.

La regla ya no queda a nivel de discurso. Queda en estructura de repo:

```text
products/tablet/app  -> Tablet POS autónomo de venta
products/pc/app      -> PC Backoffice / control avanzado cuando aplica
products/mobile/app  -> PRISMA App móvil / consulta, pulso, alertas y reportes ligeros
```

Dicho de barrio: la app móvil ya no vive rentando cuarto en la casa de PC. Tiene su propia puerta, su propio cuarto y deja de prestarle apellido al backoffice.

---

## Decisión canónica

```text
Tablet vende sola.
PC administra cuando existe.
PRISMA App consulta, resume y alerta.
Shared contracts mantienen consistencia sin imponer dependencia runtime.
```

La app móvil **no habilita**, **no bloquea** y **no condiciona** la venta local de Tablet.

PC tampoco habilita la venta básica de Tablet. PC es un asset administrativo para negocios que requieren backoffice, auditoría, inventario avanzado, compras, recepción, reabasto, sync y reportes.

---

## Por qué este rebase existe

Las iteraciones 01 y 02 instalaron PRISMA App bajo:

```text
products/pc/app/app/prisma-app
products/pc/app/src/lib/prisma-app
products/pc/app/docs/prisma-app
```

Eso sirvió para demo rápida, pero genera una ambigüedad peligrosa:

```text
Mobile parece PC por ruta,
pero es una superficie distinta por producto.
```

Esta entrega corrige esa deuda antes de seguir con demo data, reportes, MultiSucursal o APIs.

---

## Rutas nuevas

```text
products/mobile/app/app/page.tsx
products/mobile/app/app/prisma-app/page.tsx
products/mobile/app/app/prisma-app/prisma-app.module.css
products/mobile/app/src/lib/prisma-app/prisma-app-demo-data.ts
products/mobile/app/src/lib/prisma-app/prisma-app-section-contracts.ts
products/mobile/app/docs/prisma-app/**
products/mobile/app/tools/verify_prisma_app_mobile_03_product_root_rebase.mjs
```

La ruta HTTP dentro de la app móvil se conserva como:

```text
/prisma-app
```

pero ahora pertenece al producto:

```text
products/mobile/app
```

no a:

```text
products/pc/app
```

---

## Limpieza de rutas legacy

Esta entrega elimina del árbol PC:

```text
products/pc/app/app/prisma-app/page.tsx
products/pc/app/app/prisma-app/prisma-app.module.css
products/pc/app/src/lib/prisma-app/**
products/pc/app/docs/prisma-app/**
products/pc/app/docs/README_PRISMA_APP_MOBILE_02_SECTIONS.md
products/pc/app/docs/PRISMA_APP_MOBILE_02_SECTIONS.md
products/pc/app/tools/verify_prisma_app_mobile_01.mjs
products/pc/app/tools/verify_prisma_app_mobile_02_sections.mjs
```

También retira PRISMA App del menú de PC para evitar que el usuario piense que Mobile es una pantalla hija del backoffice.

---

## Funcionamiento esperado

### Tablet

- Vende sola.
- Cobra localmente.
- Genera tickets.
- Descuenta stock local permitido.
- Genera eventos/outbox.
- No necesita PC ni App móvil para venta básica.

### PC

- Administra catálogo avanzado, inventario, compras, recepción, auditoría, sync y reportes cuando el negocio lo requiere.
- Puede consumir eventos Tablet.
- No es requisito para que Tablet venda.

### PRISMA App

- Consulta ventas, caja, inventario bajo, alertas y reportes ligeros.
- Sirve para dueño, encargado o supervisor.
- Puede tener MultiSucursal como sección avanzada.
- No modifica el core transaccional.
- No manda sobre Tablet.
- No queda clasificada como PC.

---

## Beneficio para cliente

PRISMA App sirve para que el dueño vea cómo va su negocio desde el celular sin depender de llamadas, WhatsApps, capturas borrosas o promesas del encargado que dice “todo bien” aunque la caja esté bailando quebradita.

El cliente entiende:

```text
Venta de hoy
Tickets
Caja
Productos bajos
Alertas
Reportes rápidos
MultiSucursal si aplica
```

Primero sirve para cualquier negocio. MultiSucursal queda separado para negocios con más de una tienda.

---

## Beneficio técnico

- Quita ambigüedad de producto.
- Evita que PC absorba Mobile.
- Prepara scripts de arranque separados por producto.
- Permite gates tri-superficie reales.
- Permite que futuras APIs móviles vivan en su producto raíz.
- Reduce riesgo de acoplamiento mental y técnico.

---

## Comandos futuros sugeridos

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app dev
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app typecheck
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app verify:product-root
```

Puerto sugerido:

```text
3140
```

---

## Matriz tri-superficie de esta entrega

| Superficie | Surface ID | Estado | Archivos revisados | Archivos tocados | Evidencia | Razón si no se toca |
|---|---|---|---|---|---|---|
| PC | prisma.pc.backoffice | TOUCHED | module-registry.ts, app-shell.tsx | module-registry.ts, app-shell.tsx | verify confirma que PC ya no registra /prisma-app | N/A |
| Tablet | prisma.tablet.pos | EXCLUDED | products/tablet/app/app/api/health/route.ts | ninguno | verify confirma que no se tocó Tablet ni shared-ui | Esta entrega sólo migra Mobile fuera de PC. No toca Tablet, tokens, globals ni shared-ui. Reevaluar en el próximo pass visual compartido. |
| Mobile | prisma.mobile.app | TOUCHED | products/mobile/app/** | products/mobile/app/** | verify confirma product root independiente | N/A |

---

## Criterios de aceptación

- Existe `products/mobile/app`.
- Existe `products/mobile/app/app/prisma-app/page.tsx`.
- No existe `products/pc/app/app/prisma-app/page.tsx`.
- No existe `products/pc/app/src/lib/prisma-app`.
- PC navigation ya no registra `/prisma-app`.
- Surface IDs canónicos siguen siendo:
  - `prisma.pc.backoffice`
  - `prisma.tablet.pos`
  - `prisma.mobile.app`
- Mobile no contiene frases tipo `PC administra cuando existe`.
- El guardian 00C separa `reviewedFiles` de `touchedFiles`.
- El paquete conserva rollback.

---

## No-goals

Esta entrega no implementa datos reales, autenticación móvil, push notifications, API móvil ni MultiSucursal avanzado. Sólo corrige la raíz de producto y deja el terreno listo. Primero se levantan los muros de carga, luego colgamos el letrero luminoso, porque si no se cae y todavía culpan al CSS.
