# PRISMA Control Center V24 - Noir Leather Topology

## Cambio principal

- Reemplaza `internal/web/index.html` por el cockpit visual V24.
- Agrega `internal/web/v24_cockpit.js` para que el selector de temas y microinteracciones funcionen sin violar el CSP del panel (`script-src 'self'`).
- Conserva wrappers, Python APIs, configuraciones y assets existentes.
- Guarda copia de los archivos web previos en `.prisma_control_center_backups/v24_noir_leather_topology_previous_web/`.

## Instalacion rapida

Ejecutar desde la carpeta donde descomprimiste este ZIP:

```powershell
$ErrorActionPreference = "Stop"
$Target = "F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center"
$Source = Join-Path (Get-Location) "prisma-control-center"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Backup = "$Target.BACKUP_BEFORE_V24_$Stamp"
if (Test-Path $Target) { Rename-Item -Path $Target -NewName (Split-Path $Backup -Leaf) }
Copy-Item -Path $Source -Destination $Target -Recurse -Force
cd $Target
.\07_ABRIR_PANEL_CONTROL_3150.cmd
```

## Validaciones ejecutadas en sandbox

- `node --check internal/web/v24_cockpit.js`: PASS.
- `python3 -m compileall -q internal/py`: PASS.
- Validacion estatica de HTML/JS: PASS.
- Smoke real de `panel_3150.smoke_panel()`: no ejecutable en sandbox Linux porque el proyecto llama `powershell.exe` dentro de `ports_inspector.py`. En Windows debe correr con PowerShell disponible.
- Playwright visual: no ejecutable en sandbox porque Chromium no estaba instalado y el entorno no pudo descargarlo por DNS/red.
