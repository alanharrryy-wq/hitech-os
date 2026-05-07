# PRISMA_TABLET_CATALOG_EDIT_DRAWER_FIX_01

Fix quirúrgico para que el botón **Editar** del catálogo de Tablet tenga feedback visible y no parezca botón muerto.

## Problema

El click en `Editar` sí llenaba el panel derecho, pero el cambio era silencioso: sin aviso, sin foco, sin desplazamiento al drawer y sin estado claro en el botón. En una pantalla ancha o con panel derecho parcialmente fuera de vista, parecía que no pasaba nada.

## Cambio

- `CatalogScreen` ahora usa `beginEditProduct(product)` como handler explícito.
- Al editar:
  - carga el producto al formulario;
  - muestra aviso `Editando ...`;
  - hace scroll suave al panel derecho;
  - enfoca y selecciona el campo Nombre.
- La tabla cambia el botón de `Editar` a `Editando` cuando la fila está activa.
- El drawer recibe highlight visual de modo edición.

## Límites

No toca POS, cobro, APIs, DB, sync, PC, shared-kernel ni packshots.

## Validación esperada

1. Abrir `http://127.0.0.1:3120/`.
2. Entrar a Catálogo.
3. Click en `Editar`.
4. Debe verse aviso superior, fila seleccionada, botón `Editando`, drawer resaltado y campo Nombre enfocado.
5. Guardar cambios debe seguir usando `/api/pos/products/update`.
