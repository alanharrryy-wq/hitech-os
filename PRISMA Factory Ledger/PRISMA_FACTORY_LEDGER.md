# PRISMA Factory Ledger

## Purpose

The PRISMA Factory Ledger prevents rework across the whole project by recording the official state of each capability.

## Classification

| Classification | Meaning | Allowed action |
|---|---|---|
| `DONE` | Already done for the requested level | cite evidence, do not touch |
| `VERIFY` | Built or designed, needs a gate | run the correct verifier/runtime/live/release gate |
| `FIX` | Real drift or defect exists | repair only the demonstrated drift |
| `BUILD` | Does not exist | build it |
| `EXTERNAL` | Requires token/deploy/permission/live infra | prepare ceremony, do not fake green |

## Current anchor states

- LICFLOW3 Cloudflare/D1/OAuth: `LIVE_CERTIFIED`.
- Licensing source contracts: `LOCAL_VERIFIED` with `PASS_SOURCE_LICENSE_CONTRACT_ALIGNMENT_COMPLETE`.
- Customer Setup plan-based onboarding: `LOCAL_VERIFIED` / `VERIFY_PLAN_BASED_PROVISIONING_READONLY`.
- Admin Bridge token E2E: `EXTERNAL_BLOCKED` until explicitly authorized.
- Productization release distribution: `VERIFY_REQUIRED`, not a rebuild task.
- PC visual Cloudglass: `VERIFY_REQUIRED`, runtime visual evidence still needed.

## Anti-rework law

If the ledger says `doNotRebuild: true`, the next agent must not rebuild that capability. The only legal moves are to verify, certify, package, cite evidence, or fix a real demonstrated drift.

<!-- PRISMA:LOCAL_FIRST_DATA_CUSTODY:BEGIN -->
## Local-first data custody

- Capability: `productization.local_first_data_custody`.
- Classification after this package: `DONE` for the canonical source contract.
- Status: `SOURCE_READY`.
- State: `PASS_LOCAL_FIRST_CUSTODY_CONTRACT_SOURCE_READY`.
- Do not rebuild the doctrine. Advance to runtime data-egress and support-bundle certification.
- This does not prove zero network egress or legal compliance.
<!-- PRISMA:LOCAL_FIRST_DATA_CUSTODY:END -->
