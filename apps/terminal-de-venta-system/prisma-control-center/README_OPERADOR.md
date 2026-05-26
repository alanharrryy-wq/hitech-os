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
   - Menu quirurgico para levantar un modulo y Cloudflare sin abrir rutas viejas.
   - Deja `latest_MODULE_CLOUDFLARE.zip`.

5. `04_ABRIR_ATLAS_DEPENDENCIAS.cmd`
   - Abre el atlas local de dependencias.
   - Deja `latest_DEPENDENCY_ATLAS_OPEN.zip`.

6. `09_KILL_EVERYTHING_PRISMA.cmd`
   - Libera `3000,3100,3110,3120,3130,3140,3150,3200`.
   - No levanta servicios.
   - Deja `latest_KILL_EVERYTHING.zip`.

## ZIP generado

Cada ZIP contiene:

- `transcript.log`
- `summary.json`

El diagnostico operativo se obtiene desde esos ZIPs y desde los health checks ejecutados por los launchers definitivos.
