# PRISMA Liquid Glass Fixed Geometry Background 0306

## Objetivo

Cambiar la banca visual de `liquid-glass-capsules` para que el resultado se lea sin camuflaje:

- fondo claro fijo `#efe7db`;
- figuras geométricas estáticas con colores sólidos;
- la página hace scroll encima de ese fondo;
- las cápsulas pasan por encima y muestran claramente refracción/transparencia;
- sin gradientes ni animaciones en el fondo geométrico.

## Razón técnica

`position: fixed` deja el backplate amarrado al viewport durante scroll. Las figuras se mantienen estáticas, mientras la UI y las pills cambian de posición encima del fondo. Así se puede ver si `backdrop-filter` realmente toma el color/forma que hay detrás.

## Figuras sólidas

- círculo azul `#1e8cff`
- rectángulo rosa `#ff4f9a`
- triángulo ámbar `#ffb000`
- cuadrado índigo `#5138ff`
- cápsula menta `#24d8a7`
- diamante naranja `#ff6a00`
- bloque lima `#c6ea27`
- círculo violeta `#a84cff`

## Verificación

Se agrega `tools/verify_prisma_glasscaps_fixed_geometry_0306.mjs`, que valida:

- backplate fixed;
- color de fondo plano;
- clases de figuras geométricas;
- colores sólidos esperados;
- triángulo con `clip-path: polygon`;
- ausencia de gradientes en el backplate;
- ausencia de animación en la geometría.
