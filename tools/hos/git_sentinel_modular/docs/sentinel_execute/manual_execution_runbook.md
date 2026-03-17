# Manual Promotion Execution Runbook

## Objetivo

Convertir un shadow workspace ya revisado en un plan de promoción manual controlado.
Este paquete **no auto-promueve por default**. Primero construye el bundle y luego,
solo si se pide explícitamente, ejecuta la copia controlada al target root.

## Flujo recomendado

1. Verificar que el workspace tenga:
   - manifests/
   - review_bundle/
   - cutover_bundle/
2. Correr `plan` para generar:
   - target_snapshot.before.json
   - execution_plan.json
3. Revisar blockers y warnings
4. Si el plan está limpio, correr `execute --do-execute --confirm-token ...`
5. Revisar:
   - execution_result.json
   - post_smoke.json
   - rollback_instructions.json
   - execution_summary.md

## Defaults seguros

- `allow_delete = false`
- `protected_prefixes = ["legacy/"]`
- `require_confirm_token = true`
- `execution_mode = manual_only`

## Qué NO hace

- No toca el package `legacy` vivo fuera del scaffold modular.
- No ejecuta rollback automático.
- No promueve nada sin token explícito.
- No asume que `needs_attention` sea aceptable sin revisión humana.

## Artefactos generados

Dentro del workspace:

- execution_bundle/
  - target_snapshot.before.json
  - execution_plan.json
  - execution_result.json
  - post_smoke.json
  - rollback_instructions.json
  - execution_summary.md
  - target_snapshot.after.json
  - backup_manifest.copy.json (si hubo backup)

## Consejo operativo

En este proyecto, el target root **debe ser** el modular root:
`F:\repos\hitech-os\tools\hos\git_sentinel_modular`

No lo apuntes al repo completo ni a rutas inventadas.
