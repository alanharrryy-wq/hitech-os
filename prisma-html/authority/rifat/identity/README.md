# PRISMA Identity Dictionary

Canonical chain:

`neutral meaning -> identity profile -> surface adapter -> owner/slot/layer binding -> compiled projection -> separately authorized runtime projection -> runtime visual evidence -> READY`

This directory is the **single editable source authority for PRISMA visual identity**. It is not a theme folder and it must not be treated as a CSS override layer.

Authority ownership and anti-duplication policy are declared in:

- `registries/visual-authority.registry.json`
- `contract/PRISMA_VISUAL_CORE_CONTRACT.md`

Operator flow and troubleshooting live in:

- `../../../docs/ops/PRISMA_VISUAL_AUTHORITY_RUNBOOK.md`

## Current status

- Identity profiles, semantic tokens and adapters are source-ready.
- Tablet has certified detailed owner/region/slot/layer evidence and is binding-ready at source level.
- PC, Mobile, Web, Chart Lab and Control Center remain blocked from runtime projection until each surface has certified Visual Control owners, layers and editable slots.
- Shared UI remains neutral source authority rather than a surface-specific runtime binding.
- Selecting a profile changes authority only. It does not mutate live application runtime.
- Atlasfin is the canonical human cockpit, but it is not a second editable authority.
- VISCORE1 source/governance consolidation being merged does not mean every surface is runtime visual `READY`.

## Commands

```powershell
python tools/visual_core.py status
python tools/visual_core.py check
python tools/visual_core.py ready tablet
python tools/identity_dictionary.py status
python tools/identity_dictionary.py list
python tools/identity_dictionary.py activate prisma.pearl-premium.v1
python tools/compile_identity_dictionary.py --check
python tools/validate_identity_dictionary.py
```

Activation creates a reversible backup and never projects runtime. Runtime projection requires a fresh task-scoped Authority Mesh. `READY` additionally requires runtime/browser visual evidence; compiled/source-ready is not enough.

## Safe edit rule

Edit visual meaning here only when the requested change is actually semantic/identity authority. Exact route, owner, region, editable-slot and layer location belongs to `../prisma-ui/`, not to Identity Dictionary.

Generated product files declared by `../visual-source-manifest.json` must not be hand-edited as a second authority. If a legitimate product runtime change is newer than the RIFAT snapshot, reconcile history and current intent first; do not downgrade the runtime simply to satisfy a static gate.
