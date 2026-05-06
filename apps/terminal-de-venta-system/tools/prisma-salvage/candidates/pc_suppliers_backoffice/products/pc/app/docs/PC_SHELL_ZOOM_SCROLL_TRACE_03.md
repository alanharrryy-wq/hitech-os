# PRISMA PC - Shell Zoom Scroll Trace 03

## Objetivo
Corregir el problema donde el zoom del navegador mocha la navegación lateral y no deja llegar a todos los módulos.

## Cambios reales
- La barra lateral de PC tiene scroll vertical propio en desktop.
- Se neutraliza el bloqueo práctico provocado por `min-height: 720px` cuando hay zoom in.
- Se agrega `skip-link` para saltar al contenido con teclado.
- La topbar tolera mejor anchos intermedios.
- `/proveedores` muestra un bloque visible llamado “Dónde pegó este cambio”.

## No toca
- Tablet.
- Shared-kernel.
- Contratos de sincronización.
- Persistencia real.

## Verificación visual
Abrir PC, subir zoom a 125%, 150% o 175%, y verificar que la barra lateral permita scroll. Después entrar a `/proveedores` y ver el mapa de inyección.
