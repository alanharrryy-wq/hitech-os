# PRISMA HTML · Sistema narrativo

Sitio HTML modular de PRISMA dentro del Draft PR `feature/prisma-html-investor-site`.

## Enlace maestro

La entrada completa es:

`index.html`

El recorrido público conserva las rutas existentes y distribuye cinco ideas en tres páginas:

1. Qué es PRISMA.
2. Qué hace.
3. Cómo funciona.
4. Por qué es diferente.
5. Qué ecosistema construye.

La distribución actual es:

- Página 1 · Qué es PRISMA + Qué hace.
- Página 2 · Investor Deck, separado del recorrido público.
- Página 3 · Cómo funciona + Por qué es diferente.
- Página 4 · Qué ecosistema construye.
- Catálogo · Sistema visual, separado del relato comercial.

## Contrato narrativo

Las páginas públicas comparten:

- identidad oficial desde `assets/images/prisma-logo.png`;
- atmósferas gobernadas;
- máximo tres escenas;
- navegación anterior/siguiente;
- progreso visible;
- máximo dos acciones principales por página narrativa;
- interacción adicional sólo cuando demuestra algo que el contenido estático no puede explicar;
- controles móviles de 44 CSS px;
- cero overflow horizontal;
- fallback sin `backdrop-filter`;
- soporte para movimiento reducido.

La autoridad compartida vive en:

- `sistema-ui/css/patrones/narrative-page.css`
- `sistema-ui/js/componentes/prisma-narrative.js`

El refactor narrativo aprovecha las autoridades locales de cada superficie y no altera la estructura de carpetas, las rutas ni los archivos compartidos.

## Atmósferas gobernadas

- `assets/atmosphere/aurora-slate-veil.svg`
- `assets/atmosphere/liquid-operations-smoke.svg`

## Validación actual

- Estado: `PASS_SOURCE_RUNTIME_PREVIEW_PENDING`.
- Validación fuente offline: ejecutada sobre el refactor.
- Validación visual: no ejecutada.
- Browser harness: no ejecutado.
- Servidores y puertos: no tocados.
- Certificación visual: `false`.
- Publicación: autorizada por el usuario y trazada en el PR existente `#178`.

## Límites

Este proyecto no modifica Tablet POS, PC Admin, Mobile Companion, Chart Lab, Control Center, bases de datos, Prisma schema, procesos, puertos ni despliegues.
