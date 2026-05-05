# PC I03 Inventario - Uso del instalador autocontenido

## Nombre exacto del archivo

Guarda o descarga este archivo como:

```text
F:\descargasf\install_pc_i03_inventario.py
```

Si Windows lo descarga como `install_pc_i03_inventario (1).py`, renómbralo al nombre exacto. El comando principal usa ruta absoluta y no depende de dónde esté parada la terminal.

## Comando principal

```powershell
python "F:\descargasf\install_pc_i03_inventario.py" --run --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

## Rollback manual

```powershell
python "F:\descargasf\install_pc_i03_inventario.py" --rollback --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

## Qué genera localmente

- `F:\descargasf\pc_i03_inventario.zip`
- `F:\descargasf\pc_i03_YYMMDD_HHMM.log`
- `F:\descargasf\pc_i03_backups\...`
- `F:\descargasf\pc_i03_evidence\...`
