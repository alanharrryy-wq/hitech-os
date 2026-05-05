# PRISMA PC Proveedores - Persistencia minima v10

## Alcance

Esta inyeccion agrega persistencia minima del cockpit de Proveedores:

- conserva el borrador de recomendacion, pedido, cuenta, presupuesto, pago y motivo;
- guarda los ultimos resultados de simulacion, pedido, recepcion, pago y auditoria;
- permite exportar el registro local como JSON;
- permite limpiar el registro local.

## Limite declarado

Esto no reemplaza la base de datos formal. Es una capa local de continuidad para que la operacion no se pierda al refrescar la pagina mientras se prepara persistencia real en repositorio/Prisma.

## Superficies tocadas

- PC Proveedores solamente.
- No toca Tablet.
- No toca shared-kernel.

## Validacion esperada

- El cockpit muestra la seccion `Persistencia minima v10`.
- El borrador se conserva al recargar.
- Los resultados quedan listados en `Registro local de decisiones`.
- No aparecen rutas tecnicas visibles ni copy tecnico al usuario.
