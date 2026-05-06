# PRISMA App Mobile 10B - Cloudflare Live Route Repair

Este paquete corrige el caso donde la app móvil responde localmente en `http://127.0.0.1:3140/prisma-app`, pero `https://prisma.hitechrts.com/prisma-app` devuelve `404`.

## Diagnóstico que cubre

- origen móvil local sano;
- ruta DNS del túnel `engine` para `prisma.hitechrts.com`;
- bloque ingress en `C:\Users\alanh\.cloudflared\config.yml` antes del fallback `http_status:404`;
- reinicio de servicio `cloudflared`;
- smoke público de:
  - `/prisma-app`
  - `/prisma-app/install`
  - `/.well-known/pwa-domain-check.json`

## Comando recomendado

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\repair_prisma_mobile_cloudflare_live_route.ps1" -Apply
```

Si Windows pide UAC, acepta. Sin reiniciar el servicio real, Cloudflare puede seguir sirviendo la config vieja como puestito que nunca actualiza los precios del pizarrón.
