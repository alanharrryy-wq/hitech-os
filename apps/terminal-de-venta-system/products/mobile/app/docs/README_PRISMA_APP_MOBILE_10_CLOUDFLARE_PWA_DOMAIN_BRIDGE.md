# PRISMA_APP_MOBILE_10_CLOUDFLARE_PWA_DOMAIN_BRIDGE

Deja PRISMA App Mobile lista como PWA instalable por dominio.

- Público: `https://prisma.hitechrts.com/prisma-app`
- Instalar: `https://prisma.hitechrts.com/prisma-app/install`
- Local: `http://127.0.0.1:3140`
- Túnel: `engine`

## Instalar paquete

```powershell
python F:\descargasf\install_prisma_app_mobile_10_cloudflare_pwa_domain_bridge.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --apply
```

## Publicar por Cloudflare

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\start_prisma_mobile_origin.ps1"
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\ensure_prisma_mobile_cloudflare_bridge.ps1" -Apply
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\smoke_prisma_mobile_public.ps1"
```
