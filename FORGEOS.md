# ForgeOS Root Authority

This repository exposes ForgeOS from the repository root.

## Official entrypoints

### PowerShell

```powershell
.\Run-ForgeOS.ps1 quality-gate
.\Run-ForgeOS.ps1 repo-analyzer -TargetRoot F:\repos\hitech-os -OutputPath tools\_local\evidence\repo_analyzer_summary.json
```

### Python

```bash
python forgeos_entrypoint.py quality-gate
python forgeos_entrypoint.py repo-analyzer --target-root . --output tools/_local/evidence/repo_analyzer_summary.json
```

## Authority rule

- The repository root is the only official public entrypoint for ForgeOS execution.
- `forgeos/` remains the implementation boundary for kernel, commons, products, contracts, and packaging.
- Direct execution of internal ForgeOS scripts is implementation-level behavior, not the official repository entrypoint.

## Initial cutover

The first critical cutover is `repo_analyzer`.
It must be executed through the root authority path and not treated as a parallel legacy runtime.
