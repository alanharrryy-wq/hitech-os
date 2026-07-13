# PRISMA HTML

Rama de trabajo aislada para el sitio HTML modular de PRISMA, el deck para inversionistas y las páginas visuales futuras.

## Estado

- Rama: `feature/prisma-html-investor-site`
- Base: `main`
- Clasificación Factory Ledger: `BUILD`
- Producción: no desplegada
- Merge: bloqueado hasta aprobación explícita
- Superficies operativas PRISMA: excluidas

## Preview móvil

Página 3, **Por qué elegir PRISMA**:

`https://raw.githack.com/alanharrryy-wq/hitech-os/feature/prisma-html-investor-site/prisma-html/preview/pagina-3.html`

El preview usa los CSS y JavaScript reales de la rama e incorpora el logotipo oficial como asset independiente. Sirve para revisión desde teléfono; no es un despliegue de producción.

## Checkpoint remoto actual

- `index.html`: índice remoto de trabajo.
- `sistema-ui/css/prisma-ui.css`: baseline compartido compacto.
- `paginas/pagina-3-por-que-prisma/`: Página 3 modular.
- `assets/images/prisma-logo-oficial.svg`: logotipo oficial sin figura posterior.
- `preview/pagina-3.html`: preview móvil navegable.
- `reports/page3-validation.json`: validación estática de la página.
- `reports/page3-mobile-preview.json`: estado honesto del preview.
- `BRANCH-CONTEXT.md`: alcance, exclusiones y siguientes gates.

## Página 3 · Por qué elegir PRISMA

Incluye:

- hero Clear Pearl Glass;
- tres casos interactivos: restaurante, tienda y servicios;
- flujo universal de operación;
- cuatro razones concretas;
- navegación mediante ratón, toque y teclado;
- composición responsive;
- cero `!important`;
- cero `document.write()`.

## Estado de validación

`PASS_STATIC_PREVIEW_READY`.

No se declara todavía `VISUAL_CERTIFIED`: falta revisión en un dispositivo móvil real, capturas y aprobación visual del usuario.

## Próximos checkpoints

1. Revisar el preview móvil y corregir observaciones.
2. Importar el baseline modular completo del último ZIP validado.
3. Añadir la portada y el deck de inversionistas.
4. Construir la demo guiada.
5. Sustituir placeholders financieros únicamente por evidencia verificada.

## Regla de rama

Cada avance entra mediante commits temáticos y verificables. No se hará merge, deploy de producción ni cambio sobre `main` sin autorización explícita.
