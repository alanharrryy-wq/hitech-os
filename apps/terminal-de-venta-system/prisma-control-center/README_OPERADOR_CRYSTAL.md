# PRISMA Crystal Ops Console - README Operador

## Puertos locales principales

- Chart Lab: http://127.0.0.1:3000
- PRISMA Web / EIT: http://127.0.0.1:3110
- Tablet: http://127.0.0.1:3120
- PC Backoffice: http://127.0.0.1:3130
- Mobile: http://127.0.0.1:3140
- Control Center: http://127.0.0.1:3150

## Logs ZIP obligatorios

Cada launcher deja evidencia directa en:

`F:\descargasf`

Usa los `latest_*.zip` para subir rapido la ultima corrida.

## Operacion normal

Para abrir todo local y Cloudflare:

1. `03_LEVANTAR_TODO_LOCAL_Y_CLOUDFLARE.cmd`
2. `07_ABRIR_PANEL_CONTROL_3150.cmd` si necesitas reabrir panel

Para solo diagnosticar:

- `04_DIAGNOSTICO_LOCAL_Y_CLOUDFLARE.cmd`

Para Web + Control:

- `05_LEVANTAR_WEB_CONTROL_LOCAL.cmd`
- `06_LEVANTAR_WEB_CONTROL_LOCAL_Y_CLOUDFLARE.cmd`

Para Chart Lab:

- `08_LEVANTAR_CHART_LAB_LOCAL.cmd`

Limpieza total de puertos PRISMA:

- `09_KILL_EVERYTHING_PRISMA.cmd`
