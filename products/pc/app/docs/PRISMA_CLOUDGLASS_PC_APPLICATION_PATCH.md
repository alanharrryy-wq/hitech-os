# PRISMA Cloudglass PC Application Patch

Aplicado sobre `products/pc/app` para llevar rutas DecisionScreen/AppShell como `/sales-control` hacia Cloudglass Executive OS.

## Qué cambia

- Default visual de PC pasa a `dark`/graphite en `app/layout.tsx` y `PrismaDarkSelector`.
- Se agregan assets de fondo por capas en `public/backgrounds/prisma/`.
- `app/globals.css` recibe un bloque final `PRISMA_CLOUDGLASS_PC_APPLY_01` con overrides no destructivos para AppShell, Sidebar, Topbar, Hero, Cards, tablas, buttons, chips y command palette.
- `AppShell` monta `PrismaPcInteractionLayer`, un client component con:
  - `cmdk` para command palette (`Ctrl+K`).
  - `sonner` para toast.
  - `motion` para entrada/salida del command palette.
  - `gsap` + `@gsap/react` para entrada inicial y drift atmosférico.
  - `lucide-react` para iconos.

## Bibliotecas nuevas declaradas en `products/pc/app/package.json`

```txt
gsap
@gsap/react
motion
cmdk
sonner
lucide-react
echarts
```

## Cómo probar

```powershell
pnpm install
pnpm -C products/pc/app dev
```

Abrir:

```txt
http://127.0.0.1:3130/sales-control
```

Prueba `Ctrl+K`, hover de cards/nav, click en acción primaria y tabla.

## Notas

Esto no reescribe la arquitectura. Es una primera aplicación visual segura: CSS global final + assets + client interaction layer. El siguiente paso sería migrar componentes puntuales a Radix/Motion/TanStack/ECharts de forma más profunda.
