# PRISMA Crystal Ops Console - README Operador

## Puertos locales principales

- Chart Lab: http://127.0.0.1:3000
- PRISMA Web / EIT: http://127.0.0.1:3110
- Tablet: http://127.0.0.1:3120
- PC Backoffice: http://127.0.0.1:3130
- Mobile: http://127.0.0.1:3140
- Control Center: http://127.0.0.1:3150
- PRISMA Cloud Command Center: http://127.0.0.1:3160/unified-shell.html

## Logs ZIP obligatorios

Cada launcher deja evidencia directa en:

`F:\descargasf`

Usa los `latest_*.zip` para subir rapido la ultima corrida.

## Operacion normal

Para abrir todo local:

- `01_LEVANTAR_TODO_LOCAL.cmd`

Para abrir todo local y Cloudflare:

- `02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd`

Para levantar solo un modulo:

- `03_LEVANTAR_SOLO_UN_MODULO.cmd`

Para abrir el atlas:

- `04_ABRIR_ATLAS_DEPENDENCIAS.cmd`

Limpieza total de puertos PRISMA:

- `00_KILL_ALL_LOCAL.cmd`
- `09_KILL_EVERYTHING_PRISMA.cmd`

Para abrir el cockpit privado PRISMA Cloud:

- `12_ABRIR_PRISMA_CLOUD_COMMAND_CENTER_3160.cmd`
