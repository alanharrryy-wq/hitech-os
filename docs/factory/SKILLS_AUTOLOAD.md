---
doc_id: FACTORY_SKILLS_AUTOLOAD
title: Factory Role Skills Auto-Load
doc_type: guide
status: active
last_updated: 2026-03-04
---

# Factory Role Skills Auto-Load

## Scope

This feature adds deterministic, repo-local skill discovery for factory workers:

- `A_core`
- `B_tooling`
- `C_features`
- `D_validation`
- `Z_aggregator`

Skills are discovered from:

- `.codex/skills/<role>/**/SKILL.md`

## Role Mapping

Direct role folders are preferred when present.

Legacy folder fallback is used only if the direct role folder is missing:

- `A_core <- A_worker`
- `B_tooling <- B_worker`
- `C_features <- C_worker`
- `D_validation <- D_worker`
- `Z_aggregator <- Z_integrator`

## Index Artifacts

Generated files:

- `tools/codex/_cache/skills_index.json`
- `tools/codex/_cache/skills_index.md`

Index shape:

```json
{
  "version": 1,
  "skills_root": ".codex/skills",
  "roles": {
    "A_core": [
      {
        "name": "openai-docs",
        "path": ".codex/skills/A_worker/openai-docs",
        "doc_path": ".codex/skills/A_worker/openai-docs/SKILL.md"
      }
    ]
  }
}
```

## Prompt Auto-Injection

During prompt materialization/validation, each worker prompt gets:

- `YOU ARE CODEX WORKER: <worker_id>`
- `Available Skills for this worker:` block
- skill list with `name` + `SKILL.md` path only
- rule: `Use only your role's skills; do not use other roles' skills.`

`Z_aggregator` also gets:

- `Do NOT modify code; only read bundles.`

## Commands

Generate and write skills index:

```bash
python -m tools.codex.factory skills:index
```

Print indexed skills:

```bash
python -m tools.codex.factory skills:print --role A_core
```

Run setup checks (includes skills checks):

```bash
python -m tools.codex.factory doctor
```

Validate a materialized prompt folder:

```bash
python tools/codex/dispatch/validator.py validate-prompts --run-id <RUN_ID>
```

## Troubleshooting

If doctor reports missing skills coverage:

1. Confirm `.codex/skills` exists.
2. Confirm at least one `SKILL.md` exists.
3. Confirm each expected role can be resolved directly or through legacy mapping.
4. Regenerate index:
   - `python -m tools.codex.factory skills:index`
5. Re-run doctor:
   - `python -m tools.codex.factory doctor`
