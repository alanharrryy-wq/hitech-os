# Arquitectura Tablet 6.1

## Meta
Entregar una base bootable y modular para POS en tablet sin imports fantasma.

## Capas
- `app/`: rutas y pantallas
- `components/`: shell y UI mínima
- `src/modules/`: manifest por dominio
- `src/server/`: Prisma, repositorios y sync base
- `shared/twin-kernel/`: contratos compartidos de referencia única para ambas apps
- `..\..\..\prisma\*`: Prisma canónico del sistema
- `prisma/schema.prisma`: stub local deprecado, sin modelos

## Decisión clave
La tablet consume el mismo modelo Prisma canónico que PC; no mantiene un runtime de base de datos propio.
