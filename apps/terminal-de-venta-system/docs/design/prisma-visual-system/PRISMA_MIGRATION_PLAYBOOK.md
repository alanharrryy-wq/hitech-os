# PRISMA Visual System Migration Playbook

Status: living structural base
Source contract: visualcat final 1006 1701
Scope: planning and validation only

## Non-Goals For This Pass

This base does not redesign production screens, migrate Tablet/PC/Mobile CSS, change runtime background URLs, or start/stop dev servers. It creates the governed catalog, registries, adapters, templates, and validators needed before migration work begins.

## Migration Order

1. Confirm the surface adapter for the target route.
2. Register the component or recipe before touching source CSS or TSX.
3. Check `migration-candidates.registry.json` for the ranked source file and reason.
4. Apply the smallest route-owned change.
5. Run structural validators.
6. Add render evidence only if a server is already alive and safe to inspect.
7. Record skipped checks explicitly.

## Current Candidate Sources

The first candidate registry comes from ZIP evidence:

- `current_debt_map.json`
- `tablet_direct_visual_files_ranked.json`
- `pc_direct_visual_files_ranked.json`
- `mobile_direct_visual_files_ranked.json`
- `migration-candidates.target.json`

The registry intentionally stores candidates as evidence, not as instructions to bulk-edit files.

## No-Touch Rules

Do not touch these areas as part of a visual-system migration unless a later contract explicitly scopes them:

- POS checkout business logic.
- Sync/offline/license/release-gate behavior.
- Prisma generated clients.
- Live process lifecycle.
- Runtime background public copies outside governed public runtime roots.
- Global CSS background workarounds.

## Rollback

Prefer Git rollback for tracked changes. For local artifacts that must leave the repo, move them to `F:\Trash-old` with JSON and Markdown manifests instead of deleting them.

## Evidence Classification

| Classification | Meaning |
|---|---|
| `PASS_STRUCTURAL_ONLY` | Registries, schemas, templates, adapters, and scope checks passed; no render evidence was captured. |
| `SKIPPED_NO_LIVE_SERVER` | Visual QA was skipped because this pass did not start a server. |
| `FAIL_VISUAL` | Render evidence exists and shows breakage. |
| `PASS_VISUAL` | Render evidence exists and was inspected successfully. |
