# PRISMA PQOS Phase 2: Runtime Gates & Operational Health

Phase 2 extends Phase 1 with runtime-aware gates. V6 final repair enforces PRISMA real local ports and fixes CLI behavior without top-level await.

## Ports

- Engine/Core: 3100
- PRISMA Web/EIT: 3110
- Tablet: 3120
- PC/Backoffice: 3130
- Mobile/Prisma: 3140
- Control Center: 3150
- Forms: 3200

## Non-goals

- Do not start services.
- Do not mutate DB.
- Do not change Cloudflare.
- Do not invent Chart Lab port.
- Do not use ports 3000/3001/3002/3003 as PRISMA defaults.
