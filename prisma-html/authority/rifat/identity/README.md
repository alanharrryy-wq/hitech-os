# PRISMA Identity Dictionary

Canonical chain:

`neutral meaning -> identity profile -> surface adapter -> owner/slot binding -> compiled projection -> separately authorized runtime projection`

This directory is the source authority for PRISMA visual identity. It is not a theme folder and it must not be treated as a CSS override layer.

## Iteration 1 status

- Identity profiles, semantic tokens and adapters are source-ready.
- Tablet has certified detailed owner/region/slot evidence and is binding-ready at source level.
- PC, Mobile, Web, Chart Lab and Control Center are intentionally blocked from runtime projection until each surface has certified Visual Control owners, layers and editable slots.
- Selecting a profile changes authority only. It does not mutate live application runtime.

## Commands

```powershell
python tools/identity_dictionary.py status
python tools/identity_dictionary.py list
python tools/identity_dictionary.py activate prisma.pearl-premium.v1
python tools/compile_identity_dictionary.py --check
python tools/validate_identity_dictionary.py
```

Activation creates a reversible backup and never projects runtime. Runtime projection requires a fresh task-scoped Authority Mesh.
