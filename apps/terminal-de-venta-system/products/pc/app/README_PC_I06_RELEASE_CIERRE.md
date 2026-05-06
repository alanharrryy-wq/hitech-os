# PC I06 Release Cierre v3

Este cierre consolida PRISMA PC Backoffice tras I02-I05.

## Comando principal

```powershell
python "F:\descargasf\install_pc_i06_release_cierre_v3.py" --run --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

## Rollback

```powershell
python "F:\descargasf\install_pc_i06_release_cierre_v3.py" --rollback --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system"
```

## Nota

La v3 valida la forma real instalada por I02-I05 y no exige archivos que no forman parte del diseno real, como `sync.repository.ts`.
