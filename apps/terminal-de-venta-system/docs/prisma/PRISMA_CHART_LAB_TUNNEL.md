# PRISMA Chart Lab Cloudflare Tunnel

Tunnel mode is for live local preview of the Chart Lab running on port `3000`.

## Files

- Template: `F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\deploy\cloudflare-tunnel\prisma-chart-lab.tunnel.template.yml`
- Doctor: `F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\scripts\doctor-chart-lab-tunnel.ps1`
- Runner: `F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\scripts\run-chart-lab-tunnel.ps1`

## Doctor

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:tunnel:doctor
```

The doctor checks `cloudflared`, local port `3000`, HTTP content, token/config availability, ingress shape, and prints the exact run command.

## Token Mode

```powershell
$env:CLOUDFLARED_TOKEN = "<dashboard token>"
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:tunnel:run
```

## Config File Mode

```powershell
cloudflared tunnel login
cloudflared tunnel create prisma-chart-lab
cloudflared tunnel route dns prisma-chart-lab prisma-chart-lab-preview.example.com
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:tunnel:run -- -ConfigPath "<config.yml>" -TunnelName "prisma-chart-lab"
```

The ingress file must end with `http_status:404`. Do not reuse Mobile, Control, EIT, Tablet, or PC public origins.
