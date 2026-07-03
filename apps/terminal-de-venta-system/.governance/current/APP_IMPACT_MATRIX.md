# PRISMA App Impact Matrix

- Task: `Corregir LICFLOW3 Cloudflare licensing routes para que POST /api/licenses/activate, /refresh y /revoke funcionen contra app.hitechrts.com sin downgrades, sin duplicar LICFLOW2, sin tocar secretos, sin copiar DB, sin deploy automático no autorizado y preservando Worker real prisma-cloud-semilla y D1 real prisma_cloud_semilla.`
- Status: `PASS`
- Generated: `2026-07-03T12:19:43-06:00`

| App / surface | Applies | Authority files found | Mutation allowed | Exclusion / notes |
|---|---:|---:|---:|---|
| tablet | yes | 33 | yes | Selected by task. |
| pc | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| mobile | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| chart-lab | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| web | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| control-center | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| shared-ui | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| backgrounds | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| quality | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| database-sync | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
| productization | yes | 116 | yes | Selected by task. |
| shared-kernel | no | 0 | no | Not directly selected by task classifier; still can be promoted by shared/runtime impact. |
