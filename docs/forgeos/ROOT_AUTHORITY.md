# ForgeOS Root Authority Integration

## Purpose

Promote ForgeOS from an internal workspace into the official repository execution authority without collapsing the internal platform boundaries.

## Decision

- The repository root becomes the public control surface.
- `forgeos/` stays as the internal implementation boundary.
- The initial critical cutover is `repo_analyzer`.

## What is official

### Root entrypoints

- `Run-ForgeOS.ps1`
- `forgeos_entrypoint.py`

### Official actions

- `quality-gate`
- `validate-boundaries`
- `package-dry-run`
- `repo-analyzer`

## What is not official

- Direct ad-hoc execution of `forgeos/scripts/*` as the repository-wide public interface.
- New wrappers that bypass the root entrypoints.
- Imports from external repo areas into internal `forge_kernel`, `forge_commons`, or product internals without approved public surfaces.

## Integration rule

The root wrapper may delegate into `forgeos/`, but it must not reimplement kernel, commons, lifecycle, contracts, or packaging behavior.

## First cutover

`repo_analyzer` is the first route that must be treated as a ForgeOS-governed execution path.

Success criteria:

1. The repository root can execute `repo_analyzer` through `Run-ForgeOS.ps1 repo-analyzer`.
2. The root path boots Forge Kernel and Forge Commons before product execution.
3. The result is emitted as evidence from the root authority path.
4. Internal product execution remains encapsulated inside `forgeos/`.

## Quality gate rule

Repository automation should call the root authority entrypoint, not internal scripts directly.

Preferred examples:

```bash
python forgeos_entrypoint.py quality-gate
python forgeos_entrypoint.py repo-analyzer --target-root . --output tools/_local/evidence/repo_analyzer_summary.json
```
