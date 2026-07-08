# Duplicate Map

Fecha: 2026-07-08

| Pieza | Tipo | Decision | Base canonica elegida | Fuentes duplicadas | Razon |
|---|---|---|---|---|---|
| Cloud Center folder | Duplicado fisico legacy | DEPRECATE_DUPLICATE | `Prisma Cloud Ctr` | `prisma-control-center` | El ledger y verifiers actuales usan `Prisma Cloud Ctr`; el legacy queda como referencia/compatibilidad, no autoridad. |
| License ops console | Duplicado fisico | DEPRECATE_DUPLICATE | `Prisma Cloud Ctr/internal/web/license_ops_console.js` | `prisma-control-center/internal/web/license_ops_console.js` | Mantener una sola superficie viva en 3160. |
| License ops API | Duplicado fisico | DEPRECATE_DUPLICATE | `Prisma Cloud Ctr/internal/py/license_ops_api.py` | `prisma-control-center/internal/py/license_ops_api.py` | El backend vivo importa desde `Prisma Cloud Ctr`. |
| Support ticket vs SupportIssue | Duplicado conceptual | MERGE_INTO_CANONICAL | `prisma-support-resolver/schemas/support-issue.schema.json` | `tooling/productization/schemas/support-ticket.schema.json` | Ticket describe seguimiento; SupportIssue describe diagnostico resolutivo tri-surface. |
| Runtime config schemas | Duplicado conceptual | USE_AND_CONNECT | `tooling/productization/schemas/runtime-config.schema.json` | `prisma-support-resolver/schemas/runtime-config.schema.json` | El root canonico referencia/wrappea el schema existente para soporte, no lo reemplaza. |
| Device identity schemas | Duplicado conceptual | USE_AND_CONNECT | `tooling/productization/schemas/device-identity.schema.json` | `prisma-support-resolver/schemas/device-identity.schema.json` | El root canonico necesita contrato de soporte, pero conserva la autoridad productization. |
| Support bundle specs | Duplicado conceptual | MERGE_INTO_CANONICAL | `prisma-support-resolver/contracts/PRISMA_SUPPORT_BUNDLE_STANDARD.md` | productization support bundle docs + quality support-pack | Se fusionan reglas de redaccion y contenido esperado en un punto de soporte. |
| Customer setup docs | Duplicado conceptual | USE_AND_CONNECT | `shared/licensing/customer-setup-contract.ts` | productization docs/matrices | El contrato TypeScript es vivo; docs se citan como soporte. |
| Feature gates | Duplicado conceptual | USE_AND_CONNECT | `shared/licensing/feature-keys.ts` + `feature-resolver.ts` | productization feature key catalog | El catalogo JSON aqui apunta a fuentes vivas. |

## Duplicados peligrosos

No se copiaron secretos, private keys, `.env`, dumps, headers Authorization ni
tokens. La private key externa detectada queda bajo `BLOCK_SECRET_RISK` en
`AUTHORITY_MAP.md` y `MIGRATION_REPORT.md`.
