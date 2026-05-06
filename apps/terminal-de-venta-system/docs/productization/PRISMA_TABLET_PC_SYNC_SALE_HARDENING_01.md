# PRISMA_TABLET_PC_SYNC_SALE_HARDENING_01

Cierra los riesgos detectados en venta local, inventario demo, sync PC y resolución de DB.

Incluye:
- seed seguro que no pisa stock operativo;
- idempotencia por `clientRequestId`;
- `clientRequestId` único en Prisma Sale;
- UI generando request id por intento de cobro;
- PC sólo marca venta fuera de turno cuando la política exige `cashSessionId`;
- hash profundo estable para eventos rechazados;
- resolución PC más explícita con `TV_SYSTEM_ROOT`.

Validación esperada:
1. `python install_prisma_hardening_01.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --dry-run`
2. `python install_prisma_hardening_01.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --apply`
3. `python install_prisma_hardening_01.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --verify`
4. correr `tablet-db-init`, `tablet-typecheck`, `tablet-build`, `pc-typecheck`, `pc-build`.
