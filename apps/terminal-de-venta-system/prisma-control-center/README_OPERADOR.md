# PRISMA Launcher OS - README Operador

Botonera oficial para levantar y diagnosticar PRISMA. Cada corrida genera ZIP directo en:

`F:\descargasf`

No se usa carpeta `PRISMA_LAUNCHER_RUNS` dentro de Descargasf.

## Mapa confirmado de puertos

- `3000`: Chart Lab
- `3110`: PRISMA Web / EIT / pagina
- `3120`: Tablet
- `3130`: PC Backoffice
- `3140`: Mobile
- `3150`: Control Center

`3100` y `3200` solo se incluyen en `09_KILL_EVERYTHING_PRISMA.cmd` como limpieza legacy/discutida.

## Botones

1. `01_LEVANTAR_TODO_LOCAL.cmd`
   - Libera `3000,3110,3120,3130,3140,3150`.
   - Levanta Chart Lab local.
   - Ejecuta local-up del Control Center.
   - Abre panel local `3150`.
   - Deja ZIP en `F:\descargasf`.

2. `02_LEVANTAR_TODO_CLOUDFLARE.cmd`
   - Solo Cloudflare.
   - No mata puertos.
   - Deja ZIP en `F:\descargasf`.

3. `03_LEVANTAR_TODO_LOCAL_Y_CLOUDFLARE.cmd`
   - Local primero, Cloudflare despues.
   - Deja ZIP en `F:\descargasf`.

4. `04_DIAGNOSTICO_LOCAL_Y_CLOUDFLARE.cmd`
   - Diagnostico puro.
   - No mata nada.
   - No levanta nada.
   - Si health sale FAIL, el launcher no falla: genera ZIP de evidencia.

5. `05_LEVANTAR_WEB_CONTROL_LOCAL.cmd`
   - Libera `3110,3150`.
   - Levanta Web/EIT y Control Center.

6. `06_LEVANTAR_WEB_CONTROL_LOCAL_Y_CLOUDFLARE.cmd`
   - Web + Control local, despues Cloudflare.

7. `07_ABRIR_PANEL_CONTROL_3150.cmd`
   - Solo abre `http://127.0.0.1:3150`.

8. `08_LEVANTAR_CHART_LAB_LOCAL.cmd`
   - Libera `3000`.
   - Levanta Chart Lab con `pnpm chart-lab:dev`.

9. `09_KILL_EVERYTHING_PRISMA.cmd`
   - Libera `3000,3100,3110,3120,3130,3140,3150,3200`.
   - No levanta servicios.

## ZIP generado

Cada ZIP contiene:

- `transcript.log`
- `summary.json`

El log vivo de Chart Lab se queda en `%TEMP%` y su ruta queda anotada en `summary.json`.
