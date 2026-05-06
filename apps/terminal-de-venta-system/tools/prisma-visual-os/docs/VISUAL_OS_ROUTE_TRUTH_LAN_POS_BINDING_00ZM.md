# PRISMA Visual OS route truth + LAN POS binding 00ZM

Package marker: `PRISMA_VISUAL_OS_ROUTE_TRUTH_LAN_POS_BINDING_00ZM`

## Objective

Make `/visual-os/pro` tell the truth about the route it controls.

- Tablet app base: `/`
- Tablet POS runtime: `/pos`
- Visual OS Pro: `/visual-os/pro`
- Realtime API: `:4177`

When opened from LAN, for example:

`http://192.168.1.14:3120/visual-os/pro`

Visual OS must derive realtime from that same host:

- `http://192.168.1.14:4177/health`
- `http://192.168.1.14:4177/events`
- `http://192.168.1.14:4177/state`

## Safety

This patch does not touch checkout, cart, sales, stock, payment, PC business logic, Mobile business logic, shared contracts, or Cloudflare.
