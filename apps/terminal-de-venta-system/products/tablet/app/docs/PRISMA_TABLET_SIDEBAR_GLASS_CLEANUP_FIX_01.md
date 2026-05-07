# PRISMA Tablet Sidebar Glass Cleanup Fix 01

## Objetivo
Pulir la navegación lateral y la cabecera visual de Tablet para que se vea realmente glass/light premium.

## Cambios incluidos
- Oculta el recuadro de **Venta guiada / Operación diaria / Consulta / Soporte**.
- Corrige los grupos colapsables para que no muestren contadores tipo `3` / `4` y se vean como headers limpios.
- Agrega glow tipo neón suave cuando un grupo está activo.
- Mantiene los grupos en azul apagado cuando no están activos.
- Refuerza la transparencia glass del sidebar.
- Quita el rectángulo del logo PRISMA y lo integra al fondo.
- Limpia el selector de apariencia para que no se vea encimado con doble óvalo.

## Alcance técnico
Solo toca estilos visuales del shell de Tablet.

## Archivos funcionales esperados
- `components/tablet-shell/prisma-tablet-shell.module.css`

## No toca
- navegación lógica
- rutas
- checkout / POS
- sincronización
- APIs / DB
