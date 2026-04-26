# Arquitectura PC 6.1

La gemela `pc` concentra catálogo, control de stock, compras, recepción, conteos, auditoría y sync.

## Cortes principales
- `app/*`: rutas visibles de operación
- `src/modules/*`: manifiestos de módulos por dominio
- `src/server/repositories/*`: acceso a datos con Prisma
- `shared/twin-kernel/*`: contrato compartido mínimo con la gemela tablet
- `..\..\..\prisma\*`: Prisma canónico del sistema
- `prisma/schema.prisma`: stub local deprecado, sin modelos
