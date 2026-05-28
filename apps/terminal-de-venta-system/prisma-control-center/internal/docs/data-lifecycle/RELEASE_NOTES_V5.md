# RELEASE NOTES V5 GOLDEN

## Propósito

Cerrar la línea v4 Excelsior con una versión candidata a instalación. No agrega funcionalidades grandes. Refuerza seguridad, docs, verificadores, fail-fast, evidencia y consistencia.

## Cambios principales

1. API elevada a `PRISMA_DATA_LIFECYCLE_API_V5`.
2. Overlay V5 que preserva rutas V4 y agrega endpoints `/api/lifecycle/release/*`.
3. Fallback de directorio runtime escribible para evitar fallas de prueba en entornos read-only.
4. Contrato `lifecycle_release_contract.json`.
5. Checklist instalable `lifecycle_install_checklist.json`.
6. Política fail-fast `lifecycle_failfast_policy.json`.
7. Evidencia final `lifecycle_final_evidence_schema.json`.
8. Engine reescrito como instalador Golden con `--dry-run`, `--verify-only` y rollback más completo.
9. Verificadores V5 de no-downgrade, rutas, temp DB, docs, higiene ZIP y crosscheck.
10. UI V5 compacta de release readiness sin romper la UI de dos acciones.

## Qué se conserva

- Las 64 mejoras v4.
- Operation lock.
- Dry-run inject / clear.
- Evidence bundle.
- Schema inventory.
- Retention.
- Backup / rollback.
- Dashboard por dominio.
- PIN/email fallback.
- Pasada de longaniza.
