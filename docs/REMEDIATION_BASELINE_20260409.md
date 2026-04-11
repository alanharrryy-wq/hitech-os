# Remediation Baseline (Evidence-Driven)

This file documents the conservative remediation scope used by the patch scripts that accompany this change set.

## What was observed in the bundled repo snapshot

The repository already had much more structure than a stale external report implied. For example:

- root README files already existed
- `apps/keystone`, `services/core-api`, `services/ai-agent`, `packages/contracts`, `packages/ui-kit`, and `packages/tooling` already had local README files
- `.github/workflows` already existed and contained many workflow files
- `packages/ui-kit` already had tests
- `packages/contracts` already had generated schemas and a `python-sync-map.json`

## What still needed a fix

The conservative gaps that remained obvious from the bundle:

- `tools/health` had no local README
- `tools/scripts` had no local README
- `tools/codex` had no local README
- `tools/snapshot` had no local README
- `.github/workflows` had no navigation README
- the root navigation layer was still uneven and stale in places
- the repo had no narrow contract-to-Python parity checker surfaced in a simple way
- the repo had no lightweight navigation guard for critical docs/README coverage

## What this patch set chooses to do

This patch set applies safe, additive, evidence-based changes:

- improve root and docs navigation
- add missing tool/workflow README coverage
- add explicit navigation and notebook templates
- add a contract/Python parity check script
- add a navigation guard script
- add a pair of narrow workflows for those checks
- add a couple of low-risk tests to strengthen package-side guardrails

## What this patch set intentionally does not do

It does **not**:
- delete `apps/demo-engine`
- rename top-level folders
- rewrite core law documents wholesale
- claim that summaries are more authoritative than law
- assume missing product intent where only human governance can decide

That constraint is deliberate. The goal is to improve clarity and guardrails without turning a repo cleanup into unreviewed architecture surgery.
