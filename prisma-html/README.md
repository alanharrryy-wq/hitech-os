# PRISMA HTML

Rama de trabajo aislada para el sitio HTML modular de PRISMA, el deck para inversionistas y las páginas visuales futuras.

## Estado

- Rama: `feature/prisma-html-investor-site`
- Base: `main`
- Clasificación Factory Ledger: `BUILD`
- Producción: no desplegada
- Merge: bloqueado hasta aprobación explícita
- Superficies operativas PRISMA: excluidas

## Checkpoint remoto actual

El área `prisma-html/` ya contiene un checkpoint ejecutable y navegable para desarrollar desde GitHub sin tocar las aplicaciones existentes:

- `index.html`: índice remoto de trabajo.
- `sistema-ui/css/prisma-ui.css`: baseline compartido compacto.
- `paginas/pagina-3-por-que-prisma/`: Página 3 funcional.
- `reports/page3-validation.json`: validación estática honesta.
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

`PASS_STATIC` para referencias locales, estructura JavaScript, tabs por teclado, responsive y ausencia de parches prohibidos.

No se declara todavía `VISUAL_CERTIFIED`: faltan revisión alojada desde móvil, capturas y comparación visual.

## Próximos checkpoints

1. Importar el baseline modular completo del último ZIP validado.
2. Incorporar el logo oficial como asset normal.
3. Publicar un preview móvil automático.
4. Añadir la portada y el deck de inversionistas.
5. Construir la demo guiada.
6. Sustituir placeholders financieros únicamente por evidencia verificada.

## Regla de rama

Cada avance debe entrar mediante commits temáticos y verificables. No se hará merge, deploy ni cambio sobre `main` sin autorización explícita.
