# pc clean3 0506 1522

Limpieza visual PC para el indicador rojo inferior izquierdo de Next/dev tools visto en recaptura `surf8 pc full 0506 145555357 result.zip`.

## Alcance

- Instala `app/prisma-dev-issue-badge-cleaner.tsx`.
- Conecta el componente en `app/layout.tsx`.
- Oculta únicamente badges compactos de Next/dev, incluyendo el círculo `N` y el pill `Issue/Issues`, ubicados en la esquina inferior izquierda.
- No oculta overlays grandes de error runtime ni cambia rutas, Prisma, navegación o procesos.
- No mata procesos, no libera puertos, no reinicia ni levanta dev server.

## Rutas donde se observó el badge rojo en la recaptura

- `/dashboard`
- `/alertas-operativas`
- `/catalogo-activo`
- `/conteos-operativos`
- `/existencias-criticas`
- `/exportables`
- `/glosario`
- `/gobierno`
- `/incidencias-recepcion`
- `/movements`
- `/ordenes-compra`
- `/purchasing`
- `/receiving`
- `/stock`

Nota: el badge proviene del entorno dev/captura. Este paquete limpia el indicador de desarrollo para que no contamine el producto PC presentado al cliente.
