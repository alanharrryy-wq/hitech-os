# PC I05 Sync Release - Instalador autocontenido

## Comando principal

```powershell
python "F:\descargasf\install_pc_i05_sync_release.py" --run --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

## Rollback manual

```powershell
python "F:\descargasf\install_pc_i05_sync_release.py" --rollback --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

## Genera localmente

- `F:\descargasf\pc_i05_sync_release.zip`
- `F:\descargasf\pc_i05_YYMMDD_HHMM.log`
- `F:\descargasf\pc_i05_backups\...`
- `F:\descargasf\pc_i05_evidence\...`

## Alcance

Cierra sync ingest PC con endpoint canónico, validación de contrato, dedupe, conflictos, UI de estado y release notes.
