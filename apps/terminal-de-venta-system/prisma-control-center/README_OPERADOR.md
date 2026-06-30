# PRISMA Launcher OS - README Operador

Botonera oficial para levantar PRISMA. Cada corrida genera ZIP directo en:

`F:\descargasf`

No se usa carpeta `PRISMA_LAUNCHER_RUNS` dentro de Descargasf.

## Mapa confirmado de puertos

- `3000`: Chart Lab
- `3110`: PRISMA Web / EIT / pagina
- `3120`: Tablet
- `3130`: PC Backoffice
- `3140`: Mobile
- `3150`: Control Center
- `3160`: PRISMA Cloud Command Center

`3100` y `3200` solo se incluyen en los launchers de kill como limpieza legacy/discutida.

## Botones definitivos

1. `00_KILL_ALL_LOCAL.cmd`
   - Libera puertos/procesos locales PRISMA y deja `latest_KILL_EVERYTHING.zip`.

2. `01_LEVANTAR_TODO_LOCAL.cmd`
   - Levanta stack local completo y abre Control Center.
   - Deja `latest_ALL_LOCAL.zip`.

3. `02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd`
   - Levanta local completo, reinicia/conecta Cloudflare cuando aplique y valida publico.
   - Deja `latest_ALL_LOCAL_CLOUDFLARE.zip`.

4. `03_LEVANTAR_SOLO_UN_MODULO.cmd`
   - Menu quirurgico para levantar un modulo sin abrir rutas viejas.
   - Si el modulo tiene hostname publico, reinicia/valida Cloudflare; el 3160 queda privado local.
   - Deja `latest_MODULE_CLOUDFLARE.zip`.

5. `04_ABRIR_ATLAS_DEPENDENCIAS.cmd`
   - Abre el atlas local de dependencias.
   - Deja `latest_DEPENDENCY_ATLAS_OPEN.zip`.

6. `09_KILL_EVERYTHING_PRISMA.cmd`
   - Libera `3000,3100,3110,3120,3130,3140,3150,3160,3200`.
   - No levanta servicios.
   - Deja `latest_KILL_EVERYTHING.zip`.

7. `12_ABRIR_PRISMA_CLOUD_COMMAND_CENTER_3160.cmd`
   - Abre el cockpit privado `PRISMA Cloud Command Center` en `http://127.0.0.1:3160/unified-shell.html`.
   - No toca Control Center 3150 ni levanta el stack completo.
   - Deja `latest_CLOUD_COMMAND_CENTER_3160.zip`.

## ZIP generado

Cada ZIP contiene:

- `transcript.log`
- `summary.json`

El diagnostico operativo se obtiene desde esos ZIPs y desde los health checks ejecutados por los launchers definitivos.
