# 30_DEPLOYMENT_MODEL

## Document Status

- Status: Canonical
- Audience: Engineering, Tooling, Operations, Validation
- Scope: Deployment expectations, release safety, rollout discipline, and environment-aware risk management

---

## Purpose

This document defines the deployment model for Live Scene Composer and its related architecture. It exists because deployment is where architecture, safety, product behavior, and operational discipline all meet.

A bad deployment model can undo good architecture very quickly.

---

## Deployment Principles

Deployment should prioritize:

- safety over novelty
- bounded rollout over uncontrolled blast radius
- verification over optimism
- explicit enablement over accidental exposure
- rollback readiness
- boundary preservation during release

The Composer should not be deployed like an ungoverned front-end toy.
It has runtime-facing consequences and needs serious rollout discipline.

---

## Deployment Scope

The deployment model should consider:

- Composer shell changes
- module registration changes
- bridge contract changes
- dependency policy changes
- provider seam changes
- adapter changes
- runtime integration changes
- future custom widget or sandbox changes

Different changes have different deployment risk levels.

---

## Change Risk Tiers

### Tier 1: Low-risk deployment changes

Examples:

- doc-only updates
- isolated local UI polish
- non-semantic refactors in bounded private areas
- internal cleanup with strong unchanged behavior evidence

Expected handling:
Normal deployment flow.

### Tier 2: Medium-risk deployment changes

Examples:

- new safe module addition
- inspector contribution changes
- prefab library enhancements
- bounded widget editing improvements

Expected handling:
Targeted verification and clear release note context.

### Tier 3: High-risk deployment changes

Examples:

- mutation command changes
- provider seam changes
- dependency policy enforcement changes
- runtime adapter changes
- protected-node contract changes
- new capabilities in safe/advanced mode behavior

Expected handling:
Extra review, extra testing, explicit rollout caution, and strong rollback readiness.

---

## Deployment Readiness Checklist

Before deployment, confirm:

1. relevant tests pass
2. typecheck passes
3. architecture guard passes where applicable
4. protected-node changes are reviewed
5. dependency policy remains intact
6. no forbidden path or coupling regressions were introduced
7. docs remain consistent with system meaning
8. rollback approach is understood for risky changes

A release is not ready just because the app still renders.

---

## Rollout Strategy

The preferred rollout posture is gradual confidence, not broad assumption.

Good rollout behavior may include:

- bounded release scope
- targeted verification after deployment
- optional gating or feature flags for risky new capabilities
- staged enablement of new modules or mutation commands
- careful observation of bridge behavior and error signals

The exact rollout mechanics may vary, but the philosophy should remain conservative for protected seams.

---

## Feature Gating

Feature gating can be useful for:

- new modules
- new mutation commands
- advanced-mode capabilities
- early custom widget support
- risky runtime adapter changes

Gating is not a substitute for good design, but it is a valuable deployment safety mechanism when used deliberately.

---

## Bridge Deployment Considerations

Changes to `runtime-mutation-bridge` deserve extra caution because they directly affect what the Composer is allowed to do.

For bridge changes, deployment should consider:

- compatibility with existing callers
- rejection-path correctness
- target validation behavior
- mode policy behavior
- adapter routing correctness
- rollback implications if a command becomes too permissive or too restrictive

Bridge deployment mistakes can create either unsafe writes or broken authoring flows.

---

## Module Deployment Considerations

Module additions or changes should consider:

- registration correctness
- safe mode compatibility
- local failure containment
- impact on selection, inspector, and structure surfaces
- removal or disablement path if the module misbehaves

A module should be deployable without becoming irremovable.

---

## Provider and Adapter Deployment Considerations

Changes involving providers or adapters should be treated carefully because they often affect broad product behavior.

Key concerns:

- shell initialization
- runtime alignment
- scene mapping
- command routing
- boundary preservation

A provider or adapter deployment should never be treated as “just plumbing.”

---

## Rollback Philosophy

Rollback should be thought through before deployment for higher-risk changes.

Possible rollback strategies may include:

- revert the commit or release unit
- disable a module
- disable a new command path
- restore a prior provider seam
- re-enable stricter bridge validation

The important principle is:
rollback should not require introducing unsafe emergency architecture.

---

## Post-Deployment Verification

After deployment, verify at minimum:

- shell initialization
- selection and inspector coherence
- bridge behavior for critical commands
- no composer/debug boundary regressions
- no obvious performance collapse in key flows
- no abnormal rejection or failure spikes in critical seams where observability exists

The point is to confirm the important seams still hold in the deployed environment.

---

## Deployment Anti-Patterns

The deployment model must reject:

- releasing protected-node changes with no extra caution
- broad risky bundles with unclear blast radius
- skipping verification because the change “seemed minor”
- normalizing hotfixes that bypass architecture
- deploying new authority without updated policy or tests
- treating rollback as an afterthought

---

## Summary

The deployment model for Live Scene Composer should be conservative around protected seams, mutation behavior, provider and adapter changes, and new extension capabilities. Good deployment discipline preserves the same thing the architecture is trying to preserve: clarity, safety, and confidence as the product evolves.
