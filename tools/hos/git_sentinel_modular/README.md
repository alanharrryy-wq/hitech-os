# Git Sentinel Modular Scaffold

Generated at: 2026-03-15T00:42:44-06:00

## Purpose

This workspace is a **non-destructive modularization scaffold** for Git Sentinel.
It does **not** rewrite the live runtime. It prepares a clean package layout so the team can refactor hard without losing safety.

## Legacy source

- Legacy package: `tools/hos/git_sentinel`
- Backup ZIP: `F:\OneDrive\Descargas\sentinel_legacy_backup_20260315_004243.zip`
- Scaffold ZIP: `F:\OneDrive\Descargas\sentinel_modular_scaffold_20260315_004244.zip`

## Why this exists

The current Sentinel codebase already has meaningful separation of concerns, but the live package still mixes orchestration, dashboard, scanning, remediation and shared helpers in one flat folder.
This scaffold creates a safe parallel package so migration can happen in phases.

## High level stats from the legacy package

- Modules discovered: **26**
- Code-like lines (excluding comments/blank lines): **5857**
- Functions: **171**
- Classes: **9**

## Package layout

- `app/`: CLI, dashboard y capa de presentacion.
- `analysis/`: Prediccion, scoring y diagnostico.
- `core/`: Orquestacion principal del sistema.
- `learning/`: Memoria, telemetria historica y aprendizaje.
- `legacy/`: Puentes y referencias al layout viejo. No ejecutar en vivo.
- `operations/`: Scheduler, locks y gates operativos.
- `remediation/`: Repair y cleanup, siempre opt-in.
- `reporting/`: Reportes, alertas y visualizaciones serializadas.
- `scanning/`: Escaneo del repo y deteccion de artefactos.
- `security/`: Seguridad, secretos, reglas y calidad de scanner.
- `shared/`: Config, utilidades, git helpers y contratos compartidos.
- `docs/`: Documentacion viva del rediseño modular.
- `tests/`: Espacio preparado para contratos y pruebas futuras.

## Safety rules

- Legacy package remains untouched.
- No import rewiring is done by this generator.
- Cleanup and repair stay opt-in during migration.
- Dashboard work should happen after core contracts are isolated.
- Every moved module should preserve a legacy compatibility shim until tests pass.
