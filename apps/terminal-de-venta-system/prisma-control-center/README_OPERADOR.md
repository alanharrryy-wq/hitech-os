# PRISMA Control Center

Centro operativo para salud local, Cloudflare, panel visual y supervision de PRISMA Terminal de Venta.

## Botones principales

1. `01_LEVANTAR_TODO_LOCAL.cmd`
   - Revisa `3110`, `3120`, `3130`, `3140`.
   - No toca servicios sanos.
   - Arranca servicios faltantes con el comando configurado.
   - Reinicia solo procesos PRISMA reconocidos.
   - Bloquea procesos desconocidos con `BLOCKED_UNKNOWN_PROCESS`.

2. `02_LEVANTAR_TODO_CLOUDFLARE.cmd`
   - Valida `cloudflared`, version, servicio Windows, config, tunel, DNS y URLs publicas.
   - No modifica servicios locales salvo que se habilite en config.

3. `03_CHECAR_SALUD_LOCAL_Y_CLOUDFLARE.cmd`
   - Diagnostico puro. No mata, no reinicia, no modifica configs.

4. `04_LEVANTAR_LOCAL_LUEGO_CLOUDFLARE.cmd`
   - Ejecuta local primero.
   - Confirma salud local.
   - Ejecuta Cloudflare despues.
   - Genera reporte final.

5. `05_ABRIR_PANEL_CONTROL_3150.cmd`
   - Abre `http://127.0.0.1:3150`.
   - No toca `3110`, `3120`, `3130`, `3140`.
   - En localhost muestra `LOCAL_FULL`.
   - En `control.hitechrts.com` muestra `PUBLIC_REDACTED`.

## CLI

El motor esta en:

`F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center\internal\py\prisma_control_center.py`

Acciones:

- `health`
- `local-up`
- `cloudflare-up`
- `all-up`
- `panel`
- `doctor`
- `self-test`
- `export-support-bundle`

## Puertos

- `3110`: PRISMA Web / EIT
- `3120`: Tablet Core
- `3130`: PC Backoffice
- `3140`: Mobile Adder
- `3150`: PRISMA Control Center panel

El Control Center no monta nada nuevo en `3110`, `3120`, `3130` o `3140`.

## Panel Cloudflare

URL publica esperada:

`https://control.hitechrts.com/`

Origen local esperado:

`http://127.0.0.1:3150/`

El panel publico no tiene autenticacion avanzada. Por eso queda estrictamente read-only y usa `PUBLIC_REDACTED`:

- no muestra PIDs
- no muestra command lines
- no muestra cwd
- no muestra rutas locales completas
- no muestra credentials/certs/tokens
- no exporta support bundles completos
- no expone acciones destructivas

El reporte publico sanitizado se genera en:

`F:\repos\hitech-os\tools\_local\logs\prisma-control-center\latest\public-health.json`

Si `control.hitechrts.com` falla, la operacion local no se considera caida; Cloudflare se reporta como degradado cuando corresponda.

## Logs y reportes

Todos los reportes se escriben en:

`F:\repos\hitech-os\tools\_local\logs\prisma-control-center`

Cada corrida genera:

- `run_YYYYMMDD_HHMMSS.log`
- `health_YYYYMMDD_HHMMSS.json`
- `health_YYYYMMDD_HHMMSS.txt`
- `health_YYYYMMDD_HHMMSS.html`
- `latest\health.json`
- `latest\health.txt`
- `latest\health.html`
- `latest\public-health.json`

## Suposicion documentada

El puerto `3110` esta configurado como `PRISMA Web / EIT` porque el repo lo documenta como origen local de `eit.hitechrts.com`. Por seguridad, si ese proceso no fue iniciado por el Control Center y no cae dentro del allowlist PRISMA, se reporta como desconocido y no se detiene.

## Cloudflare ingress esperado

El Control Center valida que el `config.yml` industrial contenga:

```yaml
  - hostname: control.hitechrts.com
    service: http://127.0.0.1:3150
```

Debe estar antes del fallback final:

```yaml
  - service: http_status:404
```

El Control Center valida drift y DNS, pero no borra rutas existentes.

<!-- PRISMA_BLACKBOX_BRIDGE_V1_README_BEGIN -->
## PRISMA Black-box bridge

Black-box no vive dentro del wrapper. Este Control Center queda configurado para escribir su caja negra aqui:

F:\Black-box

Orden real para resolver la ruta:

1. argumento directo del bridge
2. variable de entorno PRISMA_BLACKBOX_ROOT
3. internal/config/blackbox_bridge.json
4. default compilado en internal/py/blackbox_bridge.py

Salidas principales:

F:\Black-box\runtime\prisma_black_box_events.jsonl
F:\Black-box\runtime\control_center_latest.json
F:\Black-box\runtime\control_center_bridge_latest.json
F:\Black-box\reports\prisma_control_center_bridge_*.json
F:\Black-box\incidents\active\INC_CC_*\incident.json
F:\Black-box\incidents\timeline\control_center.timeline.jsonl

Endpoint local:

http://127.0.0.1:3150/api/incidents
<!-- PRISMA_BLACKBOX_BRIDGE_V1_README_END -->

