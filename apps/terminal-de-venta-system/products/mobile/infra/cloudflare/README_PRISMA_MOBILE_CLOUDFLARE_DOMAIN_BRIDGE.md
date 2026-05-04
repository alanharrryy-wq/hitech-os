# PRISMA_APP_MOBILE_10_CLOUDFLARE_PWA_DOMAIN_BRIDGE

Publica PRISMA App Mobile como PWA instalable sin pagar Play Store todavía.

- Dominio público: `https://prisma.hitechrts.com/prisma-app`
- Instalación PWA: `https://prisma.hitechrts.com/prisma-app/install`
- Túnel Cloudflare existente: `engine`
- Origen local Mobile: `http://127.0.0.1:3140`
- App local: `products/mobile/app`

## Comandos

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\start_prisma_mobile_origin.ps1"
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\ensure_prisma_mobile_cloudflare_bridge.ps1" -Apply
pwsh -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\infra\cloudflare\smoke_prisma_mobile_public.ps1"
```
