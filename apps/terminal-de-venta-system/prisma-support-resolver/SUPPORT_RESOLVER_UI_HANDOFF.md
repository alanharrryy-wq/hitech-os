# Support Resolver UI Handoff

- Feed: `generated/ui/support-resolver-ui-feed.json`
- Schema: `generated/ui/support-resolver-ui-feed.schema.json`
- Types: `generated/ui/support-resolver-ui-types.ts`
- Decision: `VERIFY_AND_FIX_EXISTING_NOT_REBUILD`
- Runtime certified: **No**. The UI must surface gaps honestly.

## Screens

| Screen | Purpose | Data | Actions |
|---|---|---|---|
| support-overview | Mostrar salud, cobertura, bloqueadores y próximos pasos sin declarar green falso. | summary, capabilities, gaps | diagnose, export_evidence, copy_support_summary |
| support-diagnose | Convertir evidencia de identidad, licencia y runtime en issue codes y acciones seguras. | errorCodes, actions, surfaces | diagnose, simulate_runtime_alignment, choose_authority, simulate_identity_reconciliation |
| support-cases | Buscar, abrir y seguir casos con evidencia, estado y resolución. | schemas, routes, actions | export_evidence, send_to_chatgpt, send_to_codex, mark_onsite |
| support-error-catalog | Explorar los 68 códigos canónicos y su cobertura viva. | errorCodes | copy_support_summary |
| support-actions | Mostrar seguridad, dry-run, confirmación y cobertura de las 13 acciones. | actions, safety | diagnose, simulate_runtime_alignment, apply_runtime_alignment, choose_authority, simulate_identity_reconciliation, setup_claim, license_refresh, export_evidence, send_to_chatgpt, send_to_codex, mark_onsite, copy_support_summary, setup_claim_or_refresh_guided |
| support-surfaces | Comparar Tablet, PC y Mobile sin contradicciones visuales. | surfaces, featureGates, routes | diagnose, setup_claim, license_refresh |
| support-evidence | Mostrar fuentes, contratos, pruebas, gaps y exportación sanitizada. | authority, capabilities, gaps, safety | export_evidence, copy_support_summary |
