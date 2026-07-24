# RIFAT visual authority

This directory is the single editable visual authority for PRISMA Tablet.

- `prisma-ui/` preserves the existing UI Certainty and Visual Control identifiers, owners, regions, slots, layers, and gates.
- `tablet/runtime.contract.json` governs tokens, materials, states, layers, responsive intent, and accessibility fallbacks.
- `tablet/routes.json` binds every real Tablet route to an owner and route family.
- `tablet/css-source-manifest.json` maps canonical CSS sources to generated Tablet adapters.
- `tablet/runtime-sources/` contains the only editable Tablet visual sources.
- `governance/current/` contains the fresh RIFAT Authority Mesh.
- `ledgers/` records migration and retirement decisions.

Files generated into `apps/terminal-de-venta-system` must never be edited by hand. Run:

```powershell
python prisma-html/tools/generate_tablet_visual_runtime.py --authority-commit <40-char-commit>
python prisma-html/tools/generate_tablet_visual_runtime.py --check
python prisma-html/tools/validate_rifat_authority.py
```

The generated runtime is self-contained. It does not read `prisma-html` at application runtime.
