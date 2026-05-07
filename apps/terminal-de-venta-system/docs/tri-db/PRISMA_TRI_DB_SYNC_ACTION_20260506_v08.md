# PRISMA Tri-DB Sync Action v08

Agrega accion manual en PC `/sync` para ejecutar sincronizacion desde la interfaz.

## Que instala

- API route: `POST /api/sync/tri-db/run`
- Servicio server-side que ejecuta:
  - `tools/prisma/tri_db_bridge.py --run`
  - `tools/prisma/tri_db_status.py --run`
- Boton cliente `Sincronizar ahora`
- Verificador funcional

## Requisitos

- Bridge v04 instalado: `tools/prisma/tri_db_bridge.py`
- Status v06 instalado: `tools/prisma/tri_db_status.py`
- PC app corriendo como Next.js

## No cambia

- No toca schema Prisma.
- No modifica DB directamente desde TypeScript.
- No reemplaza el bridge Python.
- No elimina el flujo por PowerShell.

La UI solo dispara el flujo ya probado.
