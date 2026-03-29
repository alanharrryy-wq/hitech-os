
# Project Baselines

This directory holds **homologated per-project truth**.

Use one folder per project:

```text
ops/projects/<project_id>/
├── README.md
├── project_manifest.json
├── idea_intake.md
├── homologation_record.md
├── canonical_source_register.md
└── contract_register.md
```

## Why this exists
The framework already had a constitutional layer and a run layer. This directory gives the missing home to the project baseline that sits between them.

## Rules
- project baselines live here, not inside `00-governance-core/`
- run evidence lives under `ops/runs/`, not here
- templates become canonical only after they are instantiated here and reviewed
