
# Inter-Chat Communication Policy

## Default rule
Workers do **not** communicate directly with other workers.

Direct worker-to-worker messaging creates shadow governance, conflicting instructions, and unverifiable oral history.

## Allowed channels only

| Sender | Receiver | Allowed medium | Canonical? |
|---|---|---|---|
| governance | package chat | frozen docs, work packet, generated prompt, acceptance decision, retry prompt | yes if backed by higher-order artifact |
| package chat | governance | bundle, package report, escalation note, decision request | yes when stored as artifact |
| governance | all package chats | freeze notice, supersession notice, regenerated packet or prompt | yes if stored and referenced |
| package chat | package chat | none by default | no |

## Required routing behavior
- Cross-package questions go to governance, not to a peer worker.
- Frozen updates flow through a decision record and regenerated packets or prompts.
- Acceptance reports and retry prompts always come from governance or delegated mission control.
- A worker may reference another package's frozen artifact, but may not ask that package to change it directly.

## Emergency path
When immediate corrective coordination is required:
1. governance records the exception or waiver
2. governance issues the corrected packet or instruction
3. governance marks the previous packet or prompt as superseded

## Forbidden behavior
- "Chat 3 told me to change this" as authority
- passing draft decisions sideways between workers
- backchannel ownership swaps
- using prompts as informal relay messages outside the artifact trail
