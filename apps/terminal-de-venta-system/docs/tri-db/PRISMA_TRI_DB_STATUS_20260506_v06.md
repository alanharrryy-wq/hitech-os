# PRISMA Tri-DB Status v06

## Propósito

Este paquete agrega una capa de verificación y estado consumible sobre el puente Tablet -> PC canonical.

La regla operativa queda así:

```text
Tablet vende y escribe local
Bridge proyecta hacia PC canonical
Status valida salud/paridad
PC y Mobile leen un estado común verificable
```

## Archivo instalado

```text
tools/prisma/tri_db_status.py
```

## Salidas generadas por el status

Cuando se ejecuta, genera:

```text
F:\descargasf\prisma_tri_db_status_YYYYMMDD_HHMMSS.json
apps\terminal-de-venta-system\shared\tri-db\status.latest.json
```

El archivo `status.latest.json` es la ruta estable pensada para que PC/Mobile puedan consumir el estado de sincronización sin andar buscando el JSON más reciente como detective de vecindad.

## Qué valida

- Existencia y lectura de Tablet DB.
- Existencia y lectura de PC canonical DB.
- Último resumen `prisma_tri_db_bridge_*.json`.
- Conteos por tabla clave.
- Estado del outbox por status.
- Paridad básica Tablet vs PC.
- Referencias rotas en PC para relaciones críticas.
- Métricas simples de ventas, productos, barcodes y stock bajo.

## Estados

```text
READY              Todo lo esencial está legible y PC cubre los conteos clave de Tablet.
READY_WITH_CAVEATS Hay advertencias, pero el reporte puede generarse.
BLOCKED            Falta o no se puede leer una DB esencial.
```

## No objetivos

Este paquete no crea UI, no modifica endpoints Next.js y no agenda sync automático. Es la capa de evidencia para construir esas piezas sin vender humo con moño.

## Comandos internos

El instalador ejecuta:

```powershell
python tools\prisma\tri_db_status.py --self-test
python tools\prisma\tri_db_status.py --run --target-root F:\repos\hitech-os --out-root F:\descargasf --fail-on-blocked
```

## Siguiente uso recomendado

La siguiente inyección puede conectar `shared/tri-db/status.latest.json` a una tarjeta visible en PC y a una lectura ligera en Mobile.
