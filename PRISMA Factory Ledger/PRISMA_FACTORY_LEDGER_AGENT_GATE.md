# PRISMA Factory Ledger Agent Gate

Paste this at the top of future Codex prompts.

```text
Before touching files, read PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json.
Read apps/terminal-de-venta-system/docs/ops/PRISMA_AUTHORITY_MESH_AUTOMESH_V2_RUNBOOK.md for the current Authority Mesh / AutoMesh operator flow.
Classify the task as DONE, VERIFY, FIX, BUILD, or EXTERNAL.
If the relevant capability has doNotRebuild=true, do not rebuild it.
If it is SOURCE_READY or LOCAL_VERIFIED, advance only to the next allowed gate.
If it is FROZEN, do not touch it.
If it is EXTERNAL_BLOCKED, do not invent internal work; request/prepare the external ceremony.
Do not claim PASS without evidence.
Do not mix forbidden surfaces.
If main moves, revalidate task authority against current HEAD; do not blindly keep or blindly discard it.
At the end, update PRISMA_FACTORY_LEDGER.json and PRISMA_EVIDENCE_INDEX.json only when capability/evidence truth changed, or explain exactly why no update was appropriate.
```

## Mandatory universal PRISMA anti-rework gate

For **every PRISMA technical proposal, prompt/plan that authorizes technical work, package/injector that can change the repository, or repository mutation**, run the universal Factory Ledger gate before authorizing BUILD/FIX or touching files.

1. Treat `PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json` as the single canonical capability truth. The do-not-rebuild map and registration index are supplemental reconciliation evidence only; they never create capability authority by themselves.
2. Name every affected canonical capability ID and its requested action: `REUSE`, `VERIFY`, `ADVANCE`, `FIX`, `BUILD`, `REBUILD`, or `EXTERNAL`.
3. If the needed capability ID is absent from the canonical Ledger, stop with `BLOCKED_ANTI_REWORK`. Register/classify the capability in a separate governed task before proposing source work. Do not promote a supplemental/shadow record into authority by inference.
4. Run `python "PRISMA Factory Ledger/tools/verify_prisma_anti_rework_gate.py" --request <request.json>` in `PROPOSAL` mode. Only `PASS_ANTI_REWORK_GATE` authorizes the technical proposal. The decision is bound to the current repo HEAD and exact live authority digests.
5. `DONE + doNotRebuild=true` means reuse or advance to `nextGate`; it never authorizes BUILD/REBUILD. `SOURCE_READY` and `LOCAL_VERIFIED` are not `NOT_STARTED`. `EXTERNAL_BLOCKED` never authorizes an internal source substitute.
6. Contradictory overlapping Ledger/DNR/registration state, duplicate IDs, missing evidence/`doesNotProve`, dirty authority files, stale/unprovable authority, unknown capability, or shadow-only capability state must remain `BLOCKED_ANTI_REWORK`.
7. Before repository mutation, obtain a fresh task-exact Authority Mesh on the canonical HEAD, then rerun the same gate in `MUTATION` mode with `authorityMesh.status=PASS_COMPOSED_AUTHORITY_MESH`, 100% required authority coverage, zero blockers, request/artifact digests, and authority bound to the current HEAD. Visual mutation additionally requires `layerMapPresent=true`.
8. If `main` moves after a valid Mesh, do **not** apply the old blanket rule "new HEAD means destroy everything" and do not silently reuse stale evidence. Run AutoMesh v2 revalidation. `PASS_ALREADY_CURRENT` may reuse validated authority bytes. `PASS_NO_RELEVANT_DRIFT` may continue only with the rebound attestation bound to current HEAD. Relevant or non-ancestor drift requires a full fresh Mesh. Invalid/unprovable prior evidence fails closed. Factory Ledger authority changes are governance-sensitive and normally force the relevant/full-refresh path.
9. This universal gate does not replace stricter domain gates. PRISMA Change Assurance technical work must pass both the universal gate and the Change Assurance capability gate below.

Minimal proposal request shape:

```json
{
  "schemaVersion": "prisma.factory-ledger.anti-rework-gate.v1",
  "mode": "PROPOSAL",
  "expectedHead": "<git rev-parse HEAD>",
  "task": "<exact technical proposal>",
  "capabilities": [
    {"id": "<canonical capability id>", "requestedAction": "VERIFY"}
  ],
  "visualMutation": false
}
```

A `MUTATION` request uses the same fields plus the reviewed Authority Mesh summary. If the machine decision is not `PASS_ANTI_REWORK_GATE`, stop. No prose override is allowed.

## Mandatory Authority Mesh / AutoMesh v2 revalidation gate

Canonical operator documentation: `apps/terminal-de-venta-system/docs/ops/PRISMA_AUTHORITY_MESH_AUTOMESH_V2_RUNBOOK.md`.

When `main` changes after task authority was composed, treat the movement as a **drift event**. The decision must be based on overlap with task-bound authority, not on fear of a different SHA.

GitHub-only commands:

```text
/prisma-automesh task <urlsafe-base64-request-without-padding>
/prisma-automesh revalidate <artifact-id> sha256:<artifact-digest>
```

Current revalidation decisions:

| Decision | Meaning | Gate consequence |
|---|---|---|
| `PASS_ALREADY_CURRENT` | authority already targets current HEAD | validated bytes may be reused; no repack/full Mesh |
| `PASS_NO_RELEVANT_DRIFT` | canonical HEAD advanced without intersecting task authority | use only the new rebound attestation tied to current HEAD |
| `BLOCKED_RELEVANT_DRIFT` | affected authority/protected scope/trust anchor/Layer Map/pin changed | full fresh task-exact Mesh required |
| `BLOCKED_NON_ANCESTOR_DRIFT` | prior base unavailable or not ancestor | full fresh task-exact Mesh required |
| `BLOCKED_INVALID_PRIOR_AUTHORITY` | digest/manifest/chain/evidence invalid or unprovable | fail closed; no trusted fallback from the invalid artifact |

Additional invariants:

- semantic `CANDIDATE` retrieval is not authority;
- the revalidation workflow itself is a trust anchor;
- visual tasks require governed surface Mesh + `LAYERS_MAP.json` evidence;
- cross-platform selected-file pins are bound to certified repository-inventory Git blob identity so CRLF checkout differences do not become false drift;
- contradictory inventory/hash/blob relationships are evidence failure, not a normalization opportunity;
- artifact traversal, absolute/backslash paths, duplicate/colliding members, symlinks, unmanifested files, manifest mismatch, excessive size/compression and invalid revalidation chains must fail closed;
- a revalidated GitHub artifact may be revalidated again only when its digest/report/HEAD chain verifies;
- independent read-only revalidations may run concurrently when isolated by request/task; current authority still governs mutation/merge;
- AutoMesh/Revalidation/CI success does not imply `productionCertified=true`.

## Mandatory PRISMA Change Assurance anti-rework and V1 gate

Permanent product identity: **PRISMA Change Assurance**. Engine: **Code Atlas**. Principle: **No evidence. No green.**

The stable compatibility path `PRISMA Factory Ledger/PRISMA_CHANGE_INTELLIGENCE_CAPABILITY_MAP.json` remains the **single** Change Assurance anti-rework/V1 registry. Its legacy filename is `COMPAT_ALIAS_KEEP`; creating a second registry is forbidden. The deprecated product name `PRISMA Change Intelligence` may remain only in explicitly classified compatibility or historical evidence contexts.

For **every PRISMA Change Assurance technical proposal, prompt/plan that authorizes technical work, or repository mutation**, before proposing BUILD/FIX or touching files:

1. Read `PRISMA Factory Ledger/PRISMA_CHANGE_INTELLIGENCE_CAPABILITY_MAP.json` and `tools/code-atlas/CODE_ATLAS_CHANGE_ASSURANCE_CONTRACT.json`.
2. Validate them with `python "PRISMA Factory Ledger/tools/verify_change_intelligence_capability_gate.py" --validate-map`.
3. Name the exact affected **capability IDs** and the affected V1 stage(s): `UNDERSTAND`, `RESOLVE`, `AUTHORIZE`, `OBSERVE`, `VERIFY`, or `PROVE`.
4. Resolve every capability through its existing `DONE / VERIFY / FIX / BUILD / EXTERNAL` anti-rework classification and obey `nextGate`, `doNotRebuild`, evidence, proposal rule, and protected owners.
5. Resolve every affected A-J Definition-of-Done item through `DONE / PARTIAL / MISSING / BLOCKED / NOT_REQUIRED_V1 / EXPERIMENTAL`. `DONE` requires evidence, positive tests, and native negative tests.
6. Enforce the invariants: `Candidate != Authority`, `Impact Radius != Authorization`, `Retrieval != proof`, `UNKNOWN != PASS_WITH_WARNING`, snapshot/provenance lock for proof-bearing claims, and agent-neutral verification.
7. If a capability ID is absent, evidence is contradictory/stale, a required V1 item is unresolved, or classification cannot be proven, stop with `BLOCKED_ANTI_REWORK`. Do not guess a missing capability or owner into existence.
8. `DONE + doNotRebuild=true` means reuse or advance to the recorded next gate. It never authorizes a rebuild. In particular, mature Universal Intelligence / Customer Wow foundations are reuse/advance work, not a fresh implementation backlog.
9. `EXTERNAL` or a V1 `BLOCKED` item caused by missing external evidence never authorizes an internal source substitute. Real human usefulness and independent-agent replication must remain unclaimed until measured.
10. New public use of the deprecated product name is forbidden. Compatibility filenames/symbols and immutable historical evidence may remain only under `COMPAT_ALIAS_KEEP` or `HISTORICAL_EVIDENCE_KEEP`. Never break imports, persisted schemas, or stable automation paths for cosmetic renaming.
11. Before repository mutation, obtain task-exact Authority Mesh evidence valid for the current canonical HEAD, using AutoMesh v2 revalidation if `main` moved. Require 100% required authority coverage, zero blockers, request/artifact digests, and a Layer Map for visual mutation.
12. At closure, update Change Assurance registry/Factory Ledger evidence only when evidence actually changes maturity or next-gate truth. Never promote status from code existence, retrieval, a successful revalidation or a partial scan alone.

Pure business/commercial analysis may remain read-only under the existing commercial governance rule. The moment a proposal authorizes Git-tree/source/config/workflow/runtime work, both the universal Factory Ledger gate and this stricter Change Assurance gate become mandatory.
