# Naming Conventions

## Package IDs
Use the exact folder names as stable package IDs.

## Document ID stems
- `GOV` for governance
- `IAT` for identity, access, and trust
- `DDP` for domain, data, and persistence
- `SCO` for service contracts and orchestration
- `ECI` for experience, clients, and interactions
- `PID` for platform, infrastructure, and delivery
- `QRO` for quality, release, and operations

## File naming
- lowercase
- hyphen-separated
- responsibility-driven names
- no vague names like `misc.md`, `notes.md`, or `stuff.md`

## Identifier naming
- project IDs start with `prj-`
- run IDs start with `run-`
- round IDs start with `rd-`
- decision IDs start with `dec-`
- bundle IDs embed run, round, package, and version

## Path families
- constitutional rules: `00-governance-core/**`
- package-local docs: `01-.../**` through `06-.../**`
- tactical subsystem docs: `docs/parallel_execution/**`
- operational configs: `configs/execution_framework/**`
- prompts: `prompts/execution_framework/**`
- schemas: `schemas/execution_framework/**`
- tools: `tools/execution_framework/**`
- tests: `tests/execution_framework/**`
- templates: `templates/execution_framework/**`
- run artifacts: `ops/runs/**`
