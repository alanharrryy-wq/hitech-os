# AutoGit 98 Upgrade

Este upgrade agrega capa AG98 a AutoGit Flight Control.

## Capacidades instaladas

- Policy engine configurable en `autogit/config/autogit_98_policy.json`.
- Allowlist declarativa para evidencia `docs/ops/licscope` con escaneo de contenido todavía activo.
- Detector de ruido runtime/generated: `*.db-wal`, `*.db-shm`, `.wrangler`, caches y `generatedAt`-only.
- Self-healing seguro de líneas vacías sobrantes al EOF para docs/evidencia.
- Dashboard `HUMAN_SUMMARY.md`, `MACHINE_STATE.json`, `AG98_DASHBOARD.md`.
- `CI_DECISION.md/json` para checks de PR.
- Commit splitter más fino: AutoGit, licscope evidence, ops manual, Code Atlas, deps, app surfaces.
- Merge con opción `--sync-local-main`.

## Seguridad

- No force push por defecto.
- No `git reset --hard`.
- No `git clean`.
- No borrado permanente.
- No sanitizer de source.
- Plan viejo con HEAD drift sigue bloqueado.
