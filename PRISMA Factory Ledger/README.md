# PRISMA Factory Ledger

This folder is the root-level anti-rework control plane for PRISMA.

Canonical location:

```text
F:\repos\hitech-os\PRISMA Factory Ledger
```

It does not modify product code by itself. It tells agents and operators what already exists, what is certified, what is only source-ready, what requires verification, and what must not be rebuilt.

## Mandatory use

Before any Codex prompt, patch, diagnostic, visual pass, release package, installer work, or certification task:

1. Read `PRISMA_FACTORY_LEDGER.json`.
2. Classify the requested work as `DONE`, `VERIFY`, `FIX`, `BUILD`, or `EXTERNAL`.
3. If `doNotRebuild` is true, do not rebuild that capability.
4. If status is `SOURCE_READY` or `LOCAL_VERIFIED`, move to the next allowed gate instead of recreating architecture.
5. If status is `EXTERNAL_BLOCKED`, do not invent internal work as filler.
6. After any real work, update ledger + evidence index.

No teatro, no incienso, no retrabajo ornamental.
