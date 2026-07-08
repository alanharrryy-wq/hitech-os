# PRISMA Support Resolution Action Matrix

La fuente machine-readable es:

`prisma-support-resolver/catalogs/resolver-actions.json`

## Acciones permitidas

- `diagnose`: solo lectura.
- `simulate_runtime_alignment`: dry-run local, no muta.
- `apply_runtime_alignment`: muta solo si simulate fue seguro y hay rollback.
- `setup_claim`: reclama slot mediante Customer Setup cuando el gateway esta disponible.
- `license_refresh`: refresca licencia si endpoint/config existe.
- `export_evidence`: exporta evidencia sanitizada.
- `send_to_chatgpt`: prepara contexto sanitizado.
- `send_to_codex`: prepara contexto sanitizado y ruta de cambio.
- `mark_onsite`: marca accion presencial.

## Gate de Resolver problema

El boton de aplicar solo aparece si:

- hay evidencia suficiente;
- la accion esta permitida;
- existe rollback cuando toca archivos locales;
- no expone secretos;
- no requiere deploy;
- no requiere D1 migration;
- no rompe licencia firmada;
- no requiere presencial.

## Cross-source identity split

When two or more identity worlds are detected, `Resolver problema` must remain blocked. The operator must choose one authority path: setup claim/license refresh, POS local seed, or signed activation package. Signed license files must never be edited manually.


## recon4: ruta guiada Setup Code / License Refresh

Cuando `selectedAuthority=setup_claim_or_refresh`, el resolver debe devolver `guidedResolution` con inputs requeridos, checks previos, autoridad candidata, licencia instalada, runtime local, POS local y acciones bloqueadas. No debe mutar hasta contar con setup code/refresh source, licencia firmada verificada, backup, rollback y validaciones posteriores.


## setup_claim_or_refresh_apply_with_backup_rollback

Status: `PREFLIGHT_ONLY`

Allowed now:
- diagnose
- simulate
- export evidence
- collect setup code as operator input
- build non-mutating apply plan

Blocked until signed refresh exists:
- replacing `license.json`
- aligning runtime/device identity
- enabling Tablet POS operation

Hard gates before mutation:
1. Setup Code belongs to selected customer.
2. Claim/refresh returns signed replacement license.
3. Signature verifies against public key.
4. Local backup and rollback manifest exist.
5. POS store/terminal/device alignment validates.
6. Surface status recompute clears `CROSS_SOURCE_IDENTITY_SPLIT`.
