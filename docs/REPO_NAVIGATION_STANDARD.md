# Repo Navigation Standard

This document defines the minimum navigation support expected in the repository.

## Goal

Make important areas discoverable without flattening the architecture or replacing law with summaries.

## High-value areas that should have local README coverage

At minimum, these areas should have a `README.md`:

- `docs/`
- `apps/keystone`
- `apps/demo-engine`
- `services/core-api`
- `services/ai-agent`
- `packages/contracts`
- `packages/ui-kit`
- `packages/tooling`
- `tools/health`
- `tools/scripts`
- `tools/codex`
- `tools/snapshot`
- `.github/workflows`

## What a local README should do

A local README should answer four things quickly:

1. What is this directory for?
2. What are the key files or sub-areas?
3. How is it normally used?
4. What boundaries or cautions apply here?

It does **not** need to become a duplicate of every detailed document under that directory.

## Why this is a guardrail and not just documentation style

In a large repo, missing local README coverage increases onboarding drag and encourages incorrect assumptions about intent or ownership. A minimal navigation standard reduces that cost.

## Relationship to repo law

This standard supports discoverability. It does not override:
- `docs/CONTRACT.md`
- `docs/CONSTITUTION.md`
- `docs/MASTER_MAP.md`

## Automation

This remediation adds a narrow checker:

```text
tools/scripts/check_repo_navigation.py
```

and a workflow:

```text
.github/workflows/repo-navigation-guard.yml
```

The checker intentionally focuses on critical navigation files rather than attempting to police every folder in the repo.
