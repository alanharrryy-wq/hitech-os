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
9. This universal gate does not replace stricter domain gates. Change Intelligence technical work must pass both the universal gate and the Change Intelligence capability gate below.

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

## Mandatory PRISMA Change Intelligence anti-rework gate

For **every PRISMA Change Intelligence technical proposal, prompt/plan that authorizes technical work, or repository mutation**, before proposing BUILD/FIX or touching files:

1. Read `PRISMA Factory Ledger/PRISMA_CHANGE_INTELLIGENCE_CAPABILITY_MAP.json`.
2. Validate it with `python "PRISMA Factory Ledger/tools/verify_change_intelligence_capability_gate.py" --validate-map`.
3. Name the exact affected **capability IDs**.
4. Resolve every capability through `DONE / VERIFY / FIX / BUILD / EXTERNAL` and obey its `nextGate`, `doNotRebuild`, evidence, proposal rule, and protected existing owners.
5. If a capability ID is absent, evidence is contradictory/stale, or classification cannot be resolved, stop with `BLOCKED_ANTI_REWORK`. Do not guess a missing capability into existence.
6. `DONE + doNotRebuild=true` means reuse or advance to the recorded next gate. It never authorizes a rebuild.
7. `EXTERNAL` means collect/await the external evidence or dependency. It never authorizes an internal source fix by itself.
8. `BUILD` is allowed only for a declared genuinely new owner/adapter and must list the protected existing owners it is forbidden to duplicate.
9. Before any repository mutation, obtain a **fresh task-exact Authority Mesh** against the current repo HEAD with 100% required authority coverage, zero blockers, and a Layer Map for visual mutation.
10. At closure, update the Change Intelligence capability map/Factory Ledger evidence only when evidence actually changes maturity or next-gate truth. Never promote status from code existence alone.

Pure business/commercial analysis may remain read-only under the existing Change Intelligence commercial governance rule. The moment a proposal authorizes Git-tree/source/config/workflow/runtime work, this gate becomes mandatory.
