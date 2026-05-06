# PC I02 Catálogo - Uso del instalador autocontenido

## Comando principal

```powershell
python "F:\descargasf\install_pc_i02_catalogo.py" --run --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

## Rollback manual

```powershell
python "F:\descargasf\install_pc_i02_catalogo.py" --rollback --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

## Qué genera localmente

- `F:\descargasf\pc_i02_catalogo.zip`
- `F:\descargasf\pc_i02_YYMMDD_HHMM.log`
- `F:\descargasf\pc_i02_backups\...`
- Evidencia dentro del ZIP y evidencia de ejecución bajo `F:\descargasf`.

## Estado final

El instalador debe terminar en `READY`, `READY_WITH_CAVEATS` o `BLOCKED`. No esconde pruebas omitidas.
