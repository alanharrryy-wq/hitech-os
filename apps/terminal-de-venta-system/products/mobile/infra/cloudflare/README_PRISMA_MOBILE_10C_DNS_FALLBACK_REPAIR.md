# PRISMA App Mobile 10C - Cloudflare DNS fallback repair

Este hotfix corrige el caso donde `cloudflared tunnel route dns engine prisma.hitechrts.com` devuelve exit code 1 aunque la ruta pueda existir o el registro DNS de Cloudflare ya este creado.

## Que cambia

- El bind DNS deja de ser fatal por defecto.
- Se intenta primero ruta normal y luego `--overwrite-dns` / `-f`.
- El script sigue actualizando `config.yml` si el DNS bind falla.
- Se fuerza/valida el `ImagePath` del servicio `cloudflared` para que use `--config C:\Users\alanh\.cloudflared\config.yml tunnel run engine`.
- El smoke publico sigue siendo la verdad final.
- Se agrega modo `-Diagnose` para capturar output completo.

## Comandos

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\repair_prisma_mobile_cloudflare_live_route.ps1" -Apply
```

Diagnostico sin mutacion fuerte:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\repair_prisma_mobile_cloudflare_live_route.ps1" -Diagnose
```

Si de verdad quieres que falle cuando Cloudflare no pueda crear/actualizar DNS:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\repair_prisma_mobile_cloudflare_live_route.ps1" -Apply -RequireDnsBind
```
