# PRISMA Cloudglass PC Sales Control Patch

Este paquete aplica el look Cloudglass Executive OS a la interfaz PC tipo `DecisionScreen/AppShell`, incluyendo `/sales-control`.

## Contenido

- Assets de fondo por capas en `public/backgrounds/prisma/`.
- Overrides visuales al final de `app/globals.css`.
- Default de skin PC en modo graphite/dark.
- Capa interactiva `PrismaPcInteractionLayer` con command palette (`Ctrl+K`), toast y animación inicial.
- Dependencias declaradas en `products/pc/app/package.json`: `cmdk`, `sonner`, `motion`, `gsap`, `@gsap/react`, `lucide-react`, `echarts`.

## Cómo aplicar

Copia el contenido de este ZIP sobre la raíz del repo, respetando rutas. Luego corre:

```powershell
pnpm install
pnpm -C products/pc/app dev
```

Abre:

```txt
http://127.0.0.1:3130/sales-control
```

## Qué probar

- `Ctrl+K` abre command palette.
- Click en acción primaria dispara toast.
- Hover en cards/nav/table rows.
- Fondo graphite fracturado por capas.
- Sidebar/topbar/hero/cards/table en glass oscuro.

## Nota

Es un patch visual/interactivo seguro, no una migración total de arquitectura. El siguiente salto sería migrar tablas a TanStack, overlays completos a Radix y charts reales de ruta a ECharts.
