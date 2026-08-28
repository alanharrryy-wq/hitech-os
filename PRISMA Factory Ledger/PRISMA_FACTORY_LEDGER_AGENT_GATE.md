# PRISMA Factory Ledger Agent Gate

Paste this at the top of future Codex prompts.

```text
Before touching files, read F:\repos\hitech-os\PRISMA Factory Ledger\PRISMA_FACTORY_LEDGER.json.
Classify the task as DONE, VERIFY, FIX, BUILD, or EXTERNAL.
If the relevant capability has doNotRebuild=true, do not rebuild it.
If it is SOURCE_READY or LOCAL_VERIFIED, advance only to the next allowed gate.
If it is FROZEN, do not touch it.
If it is EXTERNAL_BLOCKED, do not invent internal work; request/prepare the external ceremony.
Do not claim PASS without evidence.
Do not mix forbidden surfaces.
At the end, update PRISMA_FACTORY_LEDGER.json and PRISMA_EVIDENCE_INDEX.json or explain exactly why no update was appropriate.
```

## Mandatory universal PRISMA anti-rework gate

For **every PRISMA technical proposal, prompt/plan that authorizes technical work, package/injector that can change the repository, or repository mutation**, run the universal Factory Ledger gate before authorizing BUILD/FIX or touching files.

1. Treat `PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json` as the single canonical capability truth. The do-not-rebuild map and registration index are supplemental reconciliation evidence only; they never create capability authority by themselves.
2. Name every affected canonical capability ID and its requested action: `REUSE`, `VERIFY`, `ADVANCE`, `FIX`, `BUILD`, `REBUILD`, or `EXTERNAL`.
3. If the needed capability ID is absent from the canonical Ledger, stop with `BLOCKED_ANTI_REWORK`. Register/classify the capability in a separate governed task before proposing source work. Do not promote a supplemental/shadow record into authority by inference.
4. Run `python "PRISMA Factory Ledger/tools/verify_prisma_anti_rework_gate.py" --request <request.json>` in `PROPOSAL` mode. Only `PASS_ANTI_REWORK_GATE` authorizes the technical proposal. The decision is bound to the current repo HEAD and exact live authority digests.
5. `DONE + doNotRebuild=true` means reuse or advance to `nextGate`; it never authorizes BUILD/REBUILD. `SOURCE_READY` and `LOCAL_VERIFIED` are not `NOT_STARTED`. `EXTERNAL_BLOCKED` never authorizes an internal source substitute.
6. Contradictory overlapping Ledger/DNR/registration state, duplicate IDs, missing evidence/`doesNotProve`, dirty authority files, stale HEAD, unknown capability, or shadow-only capability state must remain `BLOCKED_ANTI_REWORK`.
7. Before any repository mutation, obtain a fresh task-exact Authority Mesh on the exact current HEAD, then rerun the same gate in `MUTATION` mode with `authorityMesh.status=PASS_COMPOSED_AUTHORITY_MESH`, 100% required authority coverage, zero blockers, request/artifact digests, and the exact Mesh HEAD. Visual mutation additionally requires `layerMapPresent=true`.
8. A previous decision is not reusable after repo HEAD or Factory Ledger authority changes. Generate a new decision.
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
11. Before any repository mutation, obtain a **fresh task-exact Authority Mesh** against the current repo HEAD with 100% required authority coverage, zero blockers, request/artifact digests, and a Layer Map for visual mutation.
12. At closure, update Change Assurance registry/Factory Ledger evidence only when evidence actually changes maturity or next-gate truth. Never promote status from code existence, retrieval, or a partial scan alone.

Pure business/commercial analysis may remain read-only under the existing commercial governance rule. The moment a proposal authorizes Git-tree/source/config/workflow/runtime work, both the universal Factory Ledger gate and this stricter Change Assurance gate become mandatory.
