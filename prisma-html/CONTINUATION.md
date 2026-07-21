# PRISMA HTML · Continuation

## Current status

`PASS_SOURCE_RUNTIME_PREVIEW_PENDING`

## Branch

`feature/prisma-html-investor-site`

## Narrative refactor

El recorrido público conserva la estructura de archivos y rutas existentes, pero ahora sigue este orden:

1. Qué es PRISMA.
2. Qué hace.
3. Cómo funciona.
4. Por qué es diferente.
5. Qué ecosistema construye.

Distribución:

- `paginas/pagina-1-prisma/`: qué es + qué hace.
- `paginas/pagina-3-por-que-prisma/`: cómo funciona + por qué es diferente.
- `paginas/pagina-4-ecosistema-producto/`: ecosistema.
- `paginas/pagina-2-inversionistas/`: deck separado, con navegación reducida.
- `sistema-ui/catalogo/`: catálogo separado, con selector de vistas en lugar de una fila de tabs.

## Validation policy

- Offline source validation: PASS
- Visual validation: not run
- Browser/server/ports: untouched
- `pip`: not run
- Publicación autorizada por el usuario; seguimiento en el PR existente `#178`

## Git policy

Publication was explicitly requested by the user. Preserve the source-only validation boundary until a real browser preview is collected.
