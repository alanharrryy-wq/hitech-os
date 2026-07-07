# PRISMA Factory Prompt Base

## Required first response from any agent

```text
FACTORY_LEDGER_CLASSIFICATION
capability: <id>
currentStatus: <status>
classification: DONE | VERIFY | FIX | BUILD | EXTERNAL
allowedNextGate: <gate>
forbiddenSurfaces: <list>
doNotRebuild: true|false
```

## Forbidden behavior

- Saying "missing" without checking the ledger.
- Rebuilding a capability marked `doNotRebuild`.
- Treating source-ready as not started.
- Treating local/static PASS as runtime/live/distribution PASS.
- Hiding external blockers behind unrelated internal work.
- Touching surfaces not listed in the task scope.
