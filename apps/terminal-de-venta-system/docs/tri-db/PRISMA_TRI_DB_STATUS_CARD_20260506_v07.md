# PRISMA Tri-DB Status Card v07

Instala una tarjeta visible en PC `/sync` para leer `shared/tri-db/status.latest.json`.

## Objetivo

Mostrar en PC el estado del puente Tablet -> PC canonical -> Mobile:

- estado READY / READY_WITH_CAVEATS / BLOCKED;
- ultimo bridge;
- tablas proyectadas;
- filas copiadas o actualizadas;
- outbox reconocido;
- conteos Tablet vs PC;
- paridad de cobertura.

## No cambia

- No toca schema Prisma.
- No toca bases de datos.
- No modifica el bridge.
- No reemplaza Mobile.

Es solo una capa visible para dejar de depender de logs.
