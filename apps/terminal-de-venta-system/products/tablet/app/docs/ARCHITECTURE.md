# Arquitectura Tablet 6.1

## Meta
Entregar una base bootable y modular para POS en tablet sin imports fantasma.

## Capas
- `app/`: rutas y pantallas
- `components/`: shell y UI mínima
- `src/modules/`: manifest por dominio
- `src/server/`: Prisma, repositorios y sync base
- `shared/twin-kernel/`: contratos compartidos de referencia única para ambas apps
- `prisma/`: esquema y DB de desarrollo

## Decisión clave
Este paquete incluye una copia local del `shared-kernel` para que **tablet.zip** sea autocontenido y verificable por sí solo.
