# tools/prisma-governance

Run:

```powershell
python tools/prisma-governance/authority_mesh.py --task "describe the requested PRISMA change" --output .governance/current
```

For a full cross-surface scan:

```powershell
python tools/prisma-governance/authority_mesh.py --task "GLOBAL ALL APPS ALL SURFACES AUTHORITY PREFLIGHT" --full --output .governance/current
```

The tool is read-mostly and only writes `.governance/current` outputs.
