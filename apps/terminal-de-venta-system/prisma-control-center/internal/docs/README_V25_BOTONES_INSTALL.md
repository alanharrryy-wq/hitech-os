# PRISMA Control Center V25 - instalación botones reales

## Instalación recomendada

1. Descomprime el ZIP en:

```powershell
F:\descargasf\prisma_control_center_v25_extract
```

2. Ejecuta:

```powershell
cd "F:\descargasf\prisma_control_center_v25_extract\prisma-control-center"
.\INSTALAR_V25_REEMPLAZAR_CONTROL_CENTER.ps1
```

3. Reinicia el panel:

```powershell
cd "F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center"
.\07_ABRIR_PANEL_CONTROL_3150.cmd
```

4. Abre:

```text
http://127.0.0.1:3150/?v=25_buttons
```

## Qué debe verse

Sección visible: **Botones de motores** con 8 botones:

- Levantar local
- Levantar Cloudflare
- Levantar todo
- Web Control local
- Chart Lab
- Diagnóstico
- Operator Brief
- Kill PRISMA

## Endpoints agregados

- `/api/ops/actions`
- `/api/ops/action/local`
- `/api/ops/action/cloudflare`
- `/api/ops/action/all`
- `/api/ops/action/web-control`
- `/api/ops/action/chart-lab`
- `/api/ops/action/run-health`
- `/api/ops/operator-brief`
- `/api/ops/action/kill`

