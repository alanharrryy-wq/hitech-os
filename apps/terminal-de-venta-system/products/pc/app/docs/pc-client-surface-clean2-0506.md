# PC clean2 0506

Objetivo: estabilizar la recaptura PC después de aislar laboratorio oscuro y limpiar overlays rojos.

## Cambios

- `/` deja de cargar landing pesada y redirige a `/dashboard`.
- `/laboratorio-pc` queda como hub estático ligero.
- `/laboratorio-pc/dashboard-governor` queda como laboratorio estático y con import de tipo CSSProperties explícito.
- `/metricas-dia`, `/ordenes-compra` y `/outbox-operativo` quedan estáticas porque son pantallas de contrato humano sin DB.
- `/license-runtime` y `/movements` usan timeout de pantalla y fallback honesto para evitar overlay rojo si Prisma/DB tarda.
- Se añaden `loading.tsx` y `error.tsx` a rutas que fallaron en recaptura.

## No hace

- No mata procesos.
- No libera puertos.
- No reinicia ni levanta dev server.
- No oculta errores con CSS; convierte fallos de runtime en estado seguro visible.
