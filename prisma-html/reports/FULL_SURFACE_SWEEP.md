# PRISMA HTML · Refactor narrativo esencial

## Resultado

`PASS_SOURCE_RUNTIME_PREVIEW_PENDING`

La estructura de carpetas, rutas y autoridades compartidas permanece intacta. El cambio se distribuyó en los HTML, CSS y JavaScript locales que ya gobernaban cada superficie.

## Nuevo orden

1. Qué es PRISMA.
2. Qué hace.
3. Cómo funciona.
4. Por qué es diferente.
5. Qué ecosistema construye.

## Distribución

- Página 1: qué es + qué hace.
- Página 3: cómo funciona + por qué es diferente.
- Página 4: ecosistema.
- Investor Deck: ruta separada con navegación anterior/siguiente.
- Catálogo UI: herramienta separada con selector de vistas.

## Reducción de controles

| Superficie | Acciones visibles, sin contar la marca | Botones | Selectores |
|---|---:|---:|---:|
| index | 3 | 0 | 0 |
| page1 | 2 | 0 | 0 |
| investors | 3 | 2 | 0 |
| page3 | 2 | 0 | 0 |
| page4 | 2 | 0 | 0 |
| catalog | 3 | 2 | 3 |


## Refinamiento visual de la entrada

- Se recuperó un símbolo compacto desde la identidad completa transparente proporcionada por el usuario.
- La firma completa PRISMA se usa como protagonista de la portada.
- Las cinco tarjetas de secuencia se sustituyeron por cinco hitos SVG estáticos, elegantes y multicolor.
- No se agregaron botones ni comportamiento interactivo.
- No se modificaron autoridades compartidas ni la estructura de directorios.
- La revisión visual en navegador permanece pendiente y no se declara certificación visual.

## Validación fuente

- Estado: PASS.
- Checks: 376.
- Warnings: 0.
- Errores: 0.
- IDs duplicados: 0.
- Referencias locales rotas: 0.
- JavaScript inválido: 0.
- `!important`: 0.
- Browser harness: no ejecutado.
- Certificación visual: no declarada.

## Autoridades preservadas

No se modificaron:

- `sistema-ui/css/patrones/narrative-page.css`
- `sistema-ui/js/componentes/prisma-narrative.js`
- tokens globales;
- temas compartidos;
- estructura de directorios;
- rutas públicas.

## Pendiente

- Revisión visual manual del usuario.
