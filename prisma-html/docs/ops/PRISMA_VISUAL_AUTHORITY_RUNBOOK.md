# PRISMA Visual Authority Operations Runbook

Status: `CURRENT`
Scope: VISCORE1, Identity Dictionary, RIFAT/prisma-ui, Atlasfin, deterministic projections and certification

## 1. Purpose

This runbook is the operator entrypoint for PRISMA visual authority. It explains what owns visual truth, what humans are allowed to edit, how generated product projections are validated, how readiness is computed, how to recover from drift without downgrading a legitimate runtime, and how to close a PR without fake green.

The architecture contract remains authoritative at:

`prisma-html/authority/rifat/identity/contract/PRISMA_VISUAL_CORE_CONTRACT.md`

This runbook explains how to operate that contract safely.

## 2. Canonical model

PRISMA uses one editable visual authority and multiple governed projections:

`neutral meaning -> identity profile -> surface adapter -> certified owner/route/region/slot/layer binding -> compiled projection -> governed product projection -> static gates -> runtime visual evidence -> READY`

Authority roles:

| Layer | Canonical owner | Operator rule |
|---|---|---|
| Neutral visual meaning | `authority/rifat/identity/` | Editable authority for profiles, semantic tokens, recipes, assets and adapters. |
| Surface location truth | `authority/rifat/prisma-ui/` | Owns surfaces, routes, owners, regions, editable slots and layers. |
| Source-to-product projection declarations | `authority/rifat/visual-source-manifest.json` | Declares source, output, projection mode and integrity hashes. |
| Human cockpit | `extras/atlasfin/` | Inspect, preview, search, export requests and display status. It is not a second authority. |
| Product/runtime files | `apps/terminal-de-venta-system/**` | Consumers or generated projections when declared by the projection manifest. Do not hand-edit generated outputs. |
| Readiness orchestration | `tools/visual_core.py` | Computes status and blockers. It does not mutate product runtime or certify browser visuals. |
| Deterministic repository inventory | `FILES_MANIFEST.json` | Generated mechanically with `tools/refresh_files_manifest.py`. Never maintain hashes by hand. |

The goal is not zero copies. The goal is zero competing editable copies.

## 3. What is complete and what is not

VISCORE1 source/governance consolidation is complete. That means the repository has a single editable authority model, deterministic projection declarations, Atlasfin as the human cockpit, VISCORE status/readiness tooling, deterministic file inventory and CI certification gates.

This does **not** mean every product surface is runtime visual `READY`.

`READY` remains fail-closed and requires runtime/browser visual evidence, rollback/evidence and the full governed chain. A surface may legitimately remain source-ready, binding-ready or blocked while VISCORE1 itself is correctly installed.

## 4. Daily operator commands

From `prisma-html/`:

```powershell
python tools/visual_core.py status
python tools/visual_core.py status --json
python tools/visual_core.py check
python tools/visual_core.py ready tablet
python tools/visual_core.py write
python tools/visual_core.py write --atlas-export
python tools/visual_core.py tree
```

Important exit semantics:

- `status`: returns `0` and reports current state.
- `check`: returns `1` only for hard architecture or Identity Dictionary validation failure; blocked surfaces can still be a truthful non-hard-fail state.
- `ready <surface>`: returns `0` only when that surface is actually `READY`; returns `2` when blockers remain.
- `write`: writes `VISUAL_CORE_STATUS.json` and `VISUAL_CORE_STATUS.md`; `--atlas-export` also refreshes Atlasfin status data.

Equivalent package scripts where declared:

```powershell
npm run visual:status
npm run visual:check
npm run visual:write
npm run manifest:refresh
npm run manifest:check
```

## 5. Required Authority Mesh before governed changes

Before a visual/runtime mutation, or before changing authority/governance documentation that changes operating truth, generate a fresh task-scoped Authority Mesh for the exact task.

From `apps/terminal-de-venta-system/`:

```powershell
python tools/prisma-governance/authority_mesh_run.py --task "<exact task>" --full --output .governance/current
```

For governed work, review at minimum:

- `AUTHORITY_READSET.lock.json`
- `APP_IMPACT_MATRIX.md`
- `CONTRACT_AND_GATE_MATRIX.json`
- `MISSING_OR_UNMAPPED_RISK.md`
- `AGENT_PROMPT_ENVELOPE.md`
- `AUTHORITY_MESH_REPORT.md`
- `LAYERS_MAP.json`
- `LAYERS_MAP.md`
- `LAYERS_MAP_SOURCE.json`

The canonical runner cleans stale governance output before generation. `--keep-output` is debug-only and must not be used as governed evidence.

## 6. Normal edit flow

### 6.1 Change visual meaning

Edit the canonical Identity Dictionary source under:

`authority/rifat/identity/`

Then validate and compile:

```powershell
python tools/validate_identity_dictionary.py
python tools/compile_identity_dictionary.py --check
python tools/identity_binding_resolver.py coverage
python tools/visual_core.py check
```

Selecting or activating an identity profile changes authority only. It does not project live runtime by itself.

### 6.2 Change route/owner/slot/layer truth

Change only the governed RIFAT/prisma-ui sources authorized by the fresh Mesh. Do not infer owners from screenshots or filenames.

Validate the authority chain before any product projection.

### 6.3 Project to product runtime

Product application is a separate authorization step. Atlasfin does not write product files directly. Generated outputs declared by `visual-source-manifest.json` must be deterministic and must not be manually patched to make a gate green.

If a product runtime is already newer because of a legitimate independently certified change, do not overwrite it with an older RIFAT snapshot merely because RIFAT is labelled authority. First reconcile history and current intent as described below.

## 7. RIFAT projection integrity and drift recovery

Run:

```powershell
python tools/validate_rifat_authority.py
```

The validator computes SHA-256 from actual file bytes for both canonical source and product output. For `exact-byte-copy` entries it also verifies that source and output bytes are identical.

### Case A: source/output hash mismatch and `exact-copy visual projection drift`

Source and product output are actually different.

Do not immediately copy one side over the other.

1. Inspect the exact source and output paths reported by the validator.
2. Inspect Git history for both paths and the current target branch.
3. Determine which side represents the legitimate newer governed change.
4. Respect the fresh Authority Mesh and no-downgrade rule.
5. If product runtime is the legitimate newer state, promote those exact bytes into the matching RIFAT runtime source before refreshing manifest hashes.
6. If RIFAT is the intentionally newer authorized authority, project it to runtime only through the separately authorized exact-target application flow.
7. Re-run `validate_rifat_authority.py`.

A validator is not a license to downgrade current product truth.

### Case B: source/output hash mismatch but **no** `exact-copy visual projection drift`

The source and output bytes already match. Only `sourceSha256` and/or `outputSha256` in `visual-source-manifest.json` are stale.

Update only those manifest hash fields from the actual current bytes. Never guess a digest.

Reference computation:

```python
import hashlib
from pathlib import Path

digest = hashlib.sha256(Path("path/to/file").read_bytes()).hexdigest()
print(digest)
```

For an exact-byte-copy pair whose bytes are equal, the source and output digest must be the same.

After updating the manifest:

```powershell
python tools/validate_rifat_authority.py
```

The correct final state is `problems: []`.

## 8. Deterministic `FILES_MANIFEST.json`

`FILES_MANIFEST.json` is generated output. Do not hand-edit it.

After **all** `prisma-html` changes are final, run:

```powershell
python tools/refresh_files_manifest.py --write
python tools/refresh_files_manifest.py --check
```

Order matters. If documentation, authority files, Atlasfin data or any other file under `prisma-html/` changes after the manifest is generated, the committed manifest is stale again.

The certification workflow intentionally generates a candidate and then proves the committed file already matches. If CI uploads a newer candidate, commit the generator-produced candidate byte-for-byte and rerun certification.

## 9. Full focused validation set

For VISCORE authority work, the current focused static set is:

```powershell
python tools/visual_core.py check
python tools/validate_rifat_authority.py
python tools/validate_identity_dictionary.py
python tools/compile_identity_dictionary.py --check
python extras/atlasfin/generator/validate_atlas.py extras/atlasfin
python tools/validate_project.py --root . --report reports/source-validator-current.json
python tools/refresh_files_manifest.py --check
```

When the change includes runtime visual application, static PASS is not enough. Add runtime/browser visual evidence and the surface-specific governed gates required by the Mesh.

## 10. Atlasfin operator boundary

Atlasfin is the canonical human visual cockpit.

Atlasfin may:

- inspect authority and status;
- search/catalog visual components;
- preview governed recipes;
- display VISCORE readiness and evidence;
- prepare/export a governed change request.

Atlasfin may not:

- invent route, owner, slot or layer bindings;
- override Identity Dictionary meaning;
- mutate generated product runtime directly;
- claim runtime `READY` from static validation or a functional smoke.

Refresh the VISCORE status feed with:

```powershell
python tools/visual_core.py write --atlas-export
```

## 11. CI certification and PR closure

The canonical workflow is `.github/workflows/viscore1-cert.yml`.

A healthy VISCORE certification proves, among other gates:

1. canonical Authority Mesh runner self-test;
2. fresh task-scoped Mesh with Layer Map;
3. deterministic file-manifest generation;
4. PRISMA HTML source validation;
5. VISCORE architecture check;
6. Identity Dictionary validation and compile check;
7. RIFAT authority validation;
8. Atlasfin static validation;
9. no fake `READY`;
10. committed `FILES_MANIFEST.json` equals the generated candidate.

Closure discipline:

1. Merge/reconcile the current target branch before final certification if `main` moved.
2. Re-run all required gates on the reconciled tree.
3. Record the exact green head SHA.
4. Verify CI, VISCORE1, ForgeOS and navigation/guardrail checks on that same SHA when they apply.
5. Merge with an expected-head guard so a moved PR head cannot be merged accidentally.
6. Do not add a cosmetic "closing" commit after the final green run. Any commit creates a new SHA and invalidates the certification claim until gates rerun.

The green SHA is the evidence object. Treat it like a sealed container, not a whiteboard.

## 12. No-fake-green rules

Never claim runtime visual `READY` because:

- code compiled;
- a functional smoke passed;
- `visual_core.py check` returned `0`;
- RIFAT static validation passed;
- Atlasfin static validation passed;
- the page returned HTTP 200;
- a screenshot exists without governed route/owner/layer provenance.

Runtime/browser visual evidence is a separate certification boundary.

## 13. Troubleshooting quick map

| Symptom | Meaning | Correct response |
|---|---|---|
| `visual source hash mismatch` | Manifest source digest does not match current source bytes. | Compute the real digest; inspect whether source/output bytes also drift. |
| `visual output hash mismatch` | Manifest output digest does not match current output bytes. | Compute the real digest; do not overwrite runtime just to silence the gate. |
| `exact-copy visual projection drift` | Source and output bytes differ. | Inspect history and authority; reconcile without downgrade. |
| Hash mismatches with no exact-copy drift | Source and output bytes already match; manifest metadata is stale. | Update only manifest hashes from actual bytes. |
| `FILES_MANIFEST.json` differs in CI | A file changed after the committed inventory was generated. | Commit the official generated candidate, then rerun. |
| `ready <surface>` exits `2` | Surface is truthfully not runtime READY. | Read blockers; do not convert the exit code into success. |
| `check` is green but visual appearance is wrong | Static architecture is healthy; visual evidence is a different gate. | Run the surface-specific visual/runtime evidence flow. |
| Main moved after a green PR run | Certified tree is no longer the merge target tree. | Reconcile current main, regenerate derived manifests if needed and certify a new head SHA. |

## 14. Reference closure learned from PR #475

On 2026-08-30, VISCORE1 certification exposed stale RIFAT authority projections after legitimate Mobile and PC runtime changes had landed independently.

The safe recovery was:

1. prove the product runtime changes were legitimate and newer;
2. promote the current Mobile and PC bytes into their matching RIFAT runtime sources instead of downgrading product runtime;
3. observe that `exact-copy visual projection drift` disappeared;
4. refresh the four stale source/output hash fields in `visual-source-manifest.json` from actual bytes;
5. regenerate and verify `FILES_MANIFEST.json` deterministically;
6. reconcile current `main` before final certification;
7. certify one exact head SHA across all required checks;
8. merge that certified head without changing it again.

That sequence is the canonical troubleshooting precedent for this class of drift. The historical commit SHAs are evidence, not permanent configuration values.

## 15. Stable references

- Root operator entrypoint: `prisma-html/README.md`
- Continuation/handoff: `prisma-html/CONTINUATION.md`
- Authority topology: `prisma-html/TREE.md`
- Visual Core contract: `prisma-html/authority/rifat/identity/contract/PRISMA_VISUAL_CORE_CONTRACT.md`
- Identity Dictionary guide: `prisma-html/authority/rifat/identity/README.md`
- Atlasfin guide: `prisma-html/extras/atlasfin/README.md`
- Governance runner guide: `apps/terminal-de-venta-system/tools/prisma-governance/README.md`
- Operational learning: `prisma-html/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`

When these references disagree with machine-readable registries, manifests or validators, the machine-readable authority and current validator output win. Fix the prose afterward rather than forcing the code to match stale prose.
