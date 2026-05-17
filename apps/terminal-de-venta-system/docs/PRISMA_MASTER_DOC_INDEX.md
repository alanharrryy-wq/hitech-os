# PRISMA Master Doc Index

Status: active
Scope: F:\repos\hitech-os\apps\terminal-de-venta-system

## Source Of Truth

| Area | Active doc | Status | Use when |
|---|---|---|---|
| Operational safety | F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_OPERATIONAL_SAFETY_RULES.md | active | Any Codex/runtime/schema/chart work. |
| Backup ritual | F:\repos\hitech-os\apps\terminal-de-venta-system\docs\DB_BACKUP_RITUAL.md | active | Before migrations or DB writes. |
| Product law | F:\repos\hitech-os\apps\terminal-de-venta-system\README.md | active | Surface roles and Tablet-first boundaries. |
| Tablet data model | F:\repos\hitech-os\apps\terminal-de-venta-system\docs\architecture\DATA_MODEL_TABLET_LOCAL.md | active | Tablet local POS model context. |
| PC/Tablet contract | F:\repos\hitech-os\apps\terminal-de-venta-system\docs\architecture\PC_TABLET_OPERATIONAL_CONTRACT.md | active | PC must not block Tablet local sales. |
| Event contract | F:\repos\hitech-os\apps\terminal-de-venta-system\shared\contracts\sync-event-contract.v1.json | active | Event topics, outbox states and conflict codes. |
| Chart Lab README | F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\README.md | active | Chart Lab operation and validation. |
| Chart source modes | F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\docs\CHART_SOURCE_MODES.md | active | Chart data honesty and readiness. |
| Promotion readiness | F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\docs\PROMOTION_READINESS.md | active | Promotion Bridge safety checks. |
| Mobile data plane | F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\docs\prisma-app\PRISMA_APP_MOBILE_28_DATA_READINESS.md | active | Mobile readiness/source states. |

## External Planning Inputs

| Doc | Status | Authority |
|---|---|---|
| F:\descargasf\PRISMA_Blueprint_Pendientes_Tablas_y_Tareas_20260512.md | planning input | Reference for T00-T10; execute only against real repo inventory. |
| F:\descargasf\PRISMA_Tareas_Faltantes_Operativas_Verifiers_Deploy_Codex_20260512.md | planning input | Reference for O00-O14; safety/verifiers are actionable first. |

## Do Not Use These Docs As Authority

Older maturity audits, mock license docs and visual reference notes are useful context only when an active doc links to them. They must not override:

- Tablet-first law.
- Operational safety rules.
- Current Prisma schemas.
- Current package.json scripts.
- Current DB inspection.
