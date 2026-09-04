# GVAE V1 mandatory registered-target gate closure — 2026-09-04

Status: `PASS_GVAE_V1_MANDATORY_REGISTERED_TARGET_GATE`

Canonical enforcement merge:
- PR #527
- merge commit `292565cb23ceb22afb6a52bacaeffc4cdcd881d8`

## What is now mandatory

For every visual target already represented by the generated GVAE Visual Target Index, GVAE is the mandatory repository mutation path.

A registered canonical visual source or its governed generated projection cannot be changed in a mergeable change without a valid same-change `prisma.visual.application.receipt.v1` chain connecting the base bytes to the head bytes.

The rule is enforced in both:
- primary `CI`
- `PRISMA VISCORE1 Certification`

GVAE APPLY emits the receipt transactionally. Rollback includes the receipt itself, so source/projection/manifest/receipt evidence moves as one governed transaction.

## Exact PR evidence

Final PR #527 head `c96ebd33ae857734b07f66904cc639b8a36a67a8` passed:
- CI `33862113990`
- PRISMA VISCORE1 Certification `33862114141`
- ForgeOS Quality Gate `33862114007`
- PRISMA Sync Sentinel Watch `33862114070`
- repo-navigation-guard `33862114010`

The deterministic/adversarial GVAE suite is now 101/101 PASS with zero skips.

The deterministic `prisma-html/FILES_MANIFEST.json` now contains 683 files excluding the manifest itself.

## Authority

Pre-merge task-exact Authority Mesh:
- run `33861041711`
- artifact `9932158016`
- artifact sha256 `304710384a5cc3ec557d7293abe15cdf7da0722ab7167cd846c6f781e7433e3f`
- composed sha256 `d485a4a43664ff68de4f718cd7a28d16cb9c819ea2b164c09835cfec468a5b18`
- requestDigest `4b0087f0249b17528a32b67cc7550f1b5ec44c715ab9ca04ae251a244c399d0d`
- two lanes, each 7/7 required authorities, 100% coverage, zero missing authority, Layer Maps present
- bounded Factory Ledger MUTATION decision: `PASS_ANTI_REWORK_GATE`, requestedAction `ADVANCE`, decisionDigest `450118730d17b192117356288761438ebe204f100a2678beb79064cc48f67d98`

A bounded post-merge revalidation attempt correctly failed closed because the older revalidation reader expected an object-form task Layer Map while the valid prior artifact contained the current array-form Layer Map. That failed revalidation was not reused as authority.

A fresh full post-merge Authority Mesh therefore replaced it:
- run `33862352306`
- artifact `9932638245`
- artifact sha256 `89b53c2a5cca2b8b05f1d6c4c1975fc9ef7bdfd3b9f03abfdc70c4444310c100`
- composed sha256 `c3c89d10218ae034e4348e1dad3966636ae504cb60a10229a5f0adb749483b6d`
- requestDigest `4ed037acf0b4800b682d3f3ba323e40f18921ae6f39cd8aced926cdb1bfbff8b`
- exact repoHead `292565cb23ceb22afb6a52bacaeffc4cdcd881d8`
- status `PASS_COMPOSED_AUTHORITY_MESH`
- two lanes, each 7/7 required authorities, 100% coverage, zero missing authority
- read-only, repository drift stable, productionCertified=false

## Whole-surface boundary

GVAE V1 still does not provide wildcard whole-surface APPLY.

The current generated Target Index does not prove complete visual target coverage for an entire surface. Therefore a statement such as "change all Tablet visual code" is not yet a governed exact-target operation.

Today a surface redesign can be executed as multiple exact-target waves. A future Surface Batch Orchestrator may coordinate those targets only after complete surface target coverage exists. It must preserve per-target Authority Mesh + Layer Map, Factory Ledger MUTATION PASS, reviewed Code Atlas plan/diff, APPLY_READY target state, receipts, rollback, projection/manifest integrity and separate runtime/browser visual certification.

## What this does not prove

- browser-render equivalence;
- runtime visual certification;
- that any current target is APPLY_READY;
- complete whole-surface Target Index coverage;
- production/distribution/customer readiness.

This is a repository source/static enforcement closure, not runtime visual certification.
