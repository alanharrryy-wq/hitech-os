# PRISMA PQOS Runtime Layer

Phase 2 probes the PRISMA local runtime ports. It does not start services, mutate databases, change Cloudflare, or invent ports.

## PRISMA local ports

| Service | Port |
|---|---:|
| Engine / Core | 3100 |
| PRISMA Web / EIT | 3110 |
| Tablet | 3120 |
| PC / Backoffice | 3130 |
| Mobile / Prisma | 3140 |
| Control Center | 3150 |
| Forms | 3200 |

Chart Lab has no asserted port in Phase 2 V6. It stays disabled until discovered from project evidence.

## Rules

- Do not use generic Next.js ports 3000/3001/3002/3003.
- Do not change ports.
- Do not require Cloudflare in base profiles.
- A down optional service is evidence, not a blocker.
