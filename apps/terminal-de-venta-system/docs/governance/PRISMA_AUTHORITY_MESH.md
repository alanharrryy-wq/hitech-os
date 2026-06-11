# PRISMA Authority Mesh

## Purpose

PRISMA Authority Mesh is the global preflight layer for PRISMA/hitech-os work. It does **not** replace Atlas, Governor, Visual OS, catalogs, contracts, manuals, or app-specific documentation. It resolves which of those authorities apply to a requested task and creates a readset lock before any patch, prompt, ZIP, visual change, database change, or automation is produced.

The rule is simple:

```text
NO AUTHORITY_READSET.lock.json = NO WORK
NO APP_IMPACT_MATRIX.md = NO PATCH
NO CONTRACT_AND_GATE_MATRIX.json = NO GREEN
NO MISSING_OR_UNMAPPED_RISK.md REVIEW = NO PREMIUM/VISUAL/APP-WIDE CHANGE
```

## Why this exists

PRISMA already has multiple valid government layers: Atlas, Governor, Visual Catalog, Visual OS, Liquid/Cloudglass recipes, background manifests, app adapters, quality contracts, operational manual, and runtime docs. The failure mode is not lack of documentation. The failure mode is partial consultation.

Authority Mesh turns consultation into an auditable step:

1. Classify the user task.
2. Detect affected apps/surfaces.
3. Resolve required authorities from the live repository.
4. Hash all matched authority files.
5. Report missing, excluded, or unmapped risks.
6. Generate an agent prompt envelope.
7. Block downstream work if critical authority is absent.

## Scope

Authority Mesh covers all apps and surfaces:

- Tablet
- PC
- Mobile
- Chart Lab
- Web/EIT
- Control Center / Prismo Learning
- Shared UI
- Backgrounds
- Quality OS
- Prisma DB / Sync
- Productization
- Shared Kernel
- reserved or future surfaces through contractual review

## Required outputs

A successful preflight writes these files to `.governance/current/`:

- `AUTHORITY_READSET.lock.json`
- `APP_IMPACT_MATRIX.md`
- `CONTRACT_AND_GATE_MATRIX.json`
- `MISSING_OR_UNMAPPED_RISK.md`
- `AGENT_PROMPT_ENVELOPE.md`
- `AUTHORITY_MESH_REPORT.md`

## Operational rule

For future agents, Codex prompts, scripts, and ZIP packages: include `AGENT_PROMPT_ENVELOPE.md` at the top of the work request and include the full `.governance/current` folder in result/diagnostic evidence.

## Safety

The mesh tool is read-mostly. It writes only governance output files. It must not kill processes, free ports, start dev servers, regenerate Prisma, or modify product code.
