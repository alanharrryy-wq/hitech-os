# PRISMA Operational Safety Rules

Status: active
Scope: F:\repos\hitech-os\apps\terminal-de-venta-system

## Leyes no negociables

Tablet vende sola; PC y Mobile potencian.

Sync reconcilia. Eventos cuentan la verdad operacional. Chart Lab disena, valida y promueve, pero Chart Lab no lee DB cruda.

## Do Not Touch

- No tocar F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\data\tablet-pos.db sin backup previo verificable.
- No convertir PC en requisito para cerrar una venta Tablet.
- No convertir Mobile en POS ni fuente transaccional autoritativa.
- No romper OutboxEvent ni su semantica de puente operacional.
- No activar Promotion Bridge apply por default.
- No conectar componentes visuales a Prisma, SQLite, fs o archivos .db.
- No llamar live-real a datos mock, fixture o fallback.
- No actualizar baselines visuales automaticamente.

## Allowed Changes

- Verifiers read-only.
- Scripts de backup que copian DBs, schemas y migrations sin modificar origen.
- Documentos de reglas, runbooks e indices.
- Adapters/server-side que devuelven ViewModels con metadata honesta.
- Chart Lab contracts/registries que declaran sourceMode y readiness sin tocar DB cruda.

## Blocked Changes

- Mega-migraciones.
- Cambios de schema sobre DB real sin backup, reporte y prueba sobre copia.
- UI o Chart Lab importando @prisma/client, sqlite3, better-sqlite3, @libsql/client o abriendo .db.
- Fixtures usados como sustituto de fuente real cuando ya existe DB/adaptador real.
- Promotion Bridge apply sin aprobacion explicita del operador.

## Source Modes

Toda grafica o adapter debe declarar:

- sourceMode: mock, fixture, recorded-real o live-real.
- sourceLabel.
- confidence.
- freshness o freshnessStatus.
- generatedAt.
- source.

live-real requiere adapter real, lectura server-side o endpoint gobernado, metadata de freshness/confidence y prueba de que no toca DB cruda desde UI.

## Required Verification Before Merge

- pnpm verify:outbox-integrity
- pnpm verify:sync-health
- pnpm verify:no-direct-db-in-ui
- pnpm -C products/tablet/app verify:tablet-sale-flow
- pnpm -C products/chart-lab/app verify:chart-source-modes
- pnpm -C products/chart-lab/app verify:promotion-readiness
- pnpm -C products/mobile/app verify:mobile-snapshot-quality

Si una migracion entra en scope, primero ejecutar backup y validar el ZIP:

- pnpm backup:prisma
- pnpm backup:prisma:verify

## Rollback Expectation

Toda migracion o write path debe poder explicar:

- backup path.
- manifest con sha256.
- DB origen.
- DB temporal o copia usada para prueba.
- comando de verificacion.
- comando o procedimiento de rollback.

## Codex Checklist

- [ ] Confirme si el cambio toca runtime, DB, schema, UI o solo verifiers/docs.
- [ ] Si toca DB/schema, genero backup verificable antes.
- [ ] Si toca Chart Lab, sourceMode sigue honesto.
- [ ] Si toca Tablet, venta local sigue sin PC.
- [ ] Si toca Mobile, sigue siendo supervision/read-only.
- [ ] Reporte PASS/WARN/FAIL/SKIP sin esconder simulacros.
