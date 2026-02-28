---
doc_id: FACTORY_RUNTIME_EXPLAINED_POINTER
title: Factory Runtime Explained (Canonical Pointer)
doc_type: pointer
status: read-only
canonical_source: docs/factory/CONTRACT.md
last_updated: 2026-02-26
---

# FACTORY_RUNTIME_EXPLAINED

This file is a canonical pointer.

Canonical runtime explanation:

- [docs/factory/CONTRACT.md](./CONTRACT.md)

Status: READ-ONLY  
Do not duplicate or extend runtime governance text here.

## Runtime Flags

- `HITECH_FACTORY_VSCODE_CLEAN` (default: `1`): before `worktrees open`, closes only VS Code processes recorded in prior factory session registries.
- `HITECH_FACTORY_VSCODE_NUKE` (default: `0`): extends cleanup to include registry entries from the current run id as well; never kills non-registered VS Code processes.
