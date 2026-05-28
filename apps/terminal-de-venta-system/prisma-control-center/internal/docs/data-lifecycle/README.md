# PRISMA Data Lifecycle Control Center 05.3 Visibility Hotfix

Esta versión corrige que la pestaña no aparezca visualmente en Control Center aunque la instalación v5.2 haya pasado.

- Target: `<REPO_ROOT>\apps\terminal-de-venta-system\prisma-control-center`
- No toca puertos.
- No mata procesos.
- Patch offline.
- Conserva payload/API/motores/ledger/Clear/PIN de v5.2.

# PRISMA Data Lifecycle Control Center v5.2 Golden Pathfix

> Objetivo directo: `<REPO_ROOT>\apps\terminal-de-venta-system\prisma-control-center`.
> Instalación offline: no libera puertos, no arranca servicios y no toca superficies fuera de Control Center.

# PRISMA Data Lifecycle Control Center 05 GOLDEN

Versión trabajada sobre **04 EXCELSIOR** como release candidate de cierre. Esta pasada no intenta meter otra montaña de features: consolida instalación, no-downgrade, docs, verificación cruzada, evidencia final, fail-fast y safety polish para que el paquete llegue menos frágil y más instalable.

## Contrato congelado

| Área | Decisión |
|---|---|
| Pestaña | PRISMA Data Lifecycle |
| UI principal | Inyectar + Clear + dashboard por dominio |
| Modos | Ligera, Pesada, Pasada de longaniza |
| Email dueño | alanharrryy@gmail.com |
| PIN default | 030303 |
| Clear default | generated-only por ledger |
| Mutaciones públicas | bloqueadas |
| Backup | obligatorio antes de Clear/rollback |
| V5 | cierre, no feature creep |

## Qué hace v5

| Área | Objetivo cubierto |
|---|---|
| No-downgrade audit | Confirma que v5 conserva el contrato v4 |
| Installer final | Más idempotente, defensivo y con rollback claro |
| Docs finales | README, notas, safety, checklist |
| Verificación cruzada | Config/API/UI/ledger/Clear/PIN/dashboard |
| Prueba de paquete | Smoke test en Control Center extraído |
| Limpieza del ZIP | Sin caches ni basura temporal |
| Evidence final | JSON + MD con qué trae y qué se probó |
| Fail-fast | Aborta si falta payload, markers o compile |
| Checklist | Antes, durante, después y rollback |
| Safety polish | Clear no queda como botón nuclear accidental |

## Estructura

```txt
engine.py
RUN_PRISMA_DATA_LIFECYCLE_INSTALL.ps1
RUN_ONE_PASTE_COMMAND.txt
payload/
  lifecycle_api.py
  lifecycle_console.js
  lifecycle_console.css
  lifecycle_config.json
  lifecycle_domain_map.json
  lifecycle_seed_profiles.json
  lifecycle_clear_policy.json
  lifecycle_guardrails.json
  lifecycle_data_pools.json
  lifecycle_safety_contract.json
  lifecycle_improvement_catalog.json
  lifecycle_observability_policy.json
  lifecycle_export_policy.json
  lifecycle_retention_policy.json
  lifecycle_release_contract.json
  lifecycle_install_checklist.json
  lifecycle_failfast_policy.json
  lifecycle_final_evidence_schema.json
verifiers/
reports/
```

## Instalación

Pega el contenido de `RUN_ONE_PASTE_COMMAND.txt` cuando decidas instalar. El instalador genera evidencia en `<OUTPUT_DIR>`.

## Importante

No se ejecutó contra tu repo real Windows desde este entorno. Sí se validó el paquete, el módulo Python, configs, temp DB, rutas V5 y smoke test estático contra Control Center extraído.


## V5.1 hotfix

Se corrigió el orden del bloque `param(...)` en `RUN_PRISMA_DATA_LIFECYCLE_INSTALL.ps1`. PowerShell requiere `param(...)` antes de cualquier statement ejecutable.
