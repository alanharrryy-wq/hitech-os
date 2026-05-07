# PRISMA Tri-DB Bridge 20260506 v04

## Propósito

Proyecta datos operativos de la base local de Tablet hacia la base canónica de PC para que PC y Mobile vean la misma operación sin convertir a Tablet en dependiente dura de PC.

## Cambio v04

v04 agrega mapeo de identidad Tablet -> PC:

- Si PC ya tiene la misma llave natural, se usa el `id` existente de PC.
- Si el `id` de Tablet ya existe en PC pero representa otra fila lógica, el bridge genera un `bridge_<tabla>_<hash>` determinístico.
- Los hijos se reescriben con el `id` de destino antes de insertarse: por ejemplo `Barcode.productId`, `SaleLine.productId`, `StockSnapshot.productId` y `Sale.terminalId`.
- No se sobreescriben primary keys de PC.
- No se borran filas.
- Hay backup de DB antes de sincronizar y rollback si falla.

## Orden de datos

Tablet sigue siendo write-owner de venta local. PC recibe proyección y consolida. Mobile consume por APIs, no por DB local.

## Comando instalado

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma\tri_db_bridge.py" --run --target-root "F:\repos\hitech-os" --out-root "F:\descargasf"
```

## Modos

- `--self-test`: prueba aislada en bases temporales.
- `--plan`: valida rutas y muestra tablas proyectables.
- `--run`: ejecuta backup + sync + rollback automático si falla.

## No objetivos

- No migra el schema Prisma.
- No borra datos duplicados.
- No resuelve conflictos de negocio ambiguos por magia negra con sombrero de Excel.
