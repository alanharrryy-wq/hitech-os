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
