# Artifact Registry

This document defines the documentary contract for artifact registration in the `control_tower` phase.

## Purpose

Artifacts are how the system remembers what happened.
Without a registry contract, bundles and reports become a swamp of filenames and vibes.

## Artifact registry responsibilities

The registry layer must be able to represent:

- what artifact exists
- what kind it is
- what domain produced it
- what lifecycle state it supports
- where it lives
- what evidence role it serves
- whether it is authoritative, auxiliary, or provisional

## Canonical artifact kinds

The initial canonical kinds are:

- `zip_bundle`
- `manifest`
- `validation_report`
- `activation_report`
- `snapshot`
- `audit_record`
- `evidence`

## Required fields for a registry entry

Every registry entry should be able to express at least:

- `artifact_id`
- `artifact_kind`
- `producer_domain`
- `subject_domain`
- `lifecycle_state`
- `path`
- `created_at` or comparable time marker if available
- `authoritative` boolean or equivalent flag
- `evidence_role`
- `notes`

## Producer domain examples

Valid examples:
- `git_sentinel_modular`
- `engine_guardian`
- `control_tower`

## Subject domain examples

The artifact may describe:
- the same domain that produced it
- a sibling domain under read-only observation
- a multi-domain snapshot

## Authority classification

### authoritative
Use when the artifact is the main accepted record for a decision.

### auxiliary
Use when the artifact supports interpretation but is not the decisive record.

### provisional
Use when the artifact exists but should not yet drive promotion.

## Evidence role examples

- activation proof
- validation proof
- runtime observation
- placement manifest
- snapshot capture
- audit comparison
- governance decision trace

## Forbidden registry behavior

The registry must not:
- mutate protected runtime paths
- delete evidence for convenience
- infer ownership from artifact presence alone
- pretend an artifact is authoritative without documentary basis

## Current high-value evidence examples from the handoff baseline

The following are known evidence paths of high importance:

- `F:\OneDrive\Descargas\engine_guardian\install\privileged_activation_20260327_005820\activation_summary.json`
- `F:\OneDrive\Descargas\engine_guardian\install\privileged_activation_20260327_005820\activation.log`
- `F:\OneDrive\Descargas\engine_guardian\install\privileged_activation_20260327_005820\legacy_cloudflare_task_cutover_latest.json`
- `F:\OneDrive\Descargas\engine_guardian\install\multi_retry_attempts_20260327_005555.json`

These should be modeled as evidence, not excuses for control takeover.

## Registry design discipline

The registry is a memory and evidence index.
It is not:
- a remediation queue
- a scheduler
- a service operator
- a mutation controller

## Cross-chat rule

Chat A may define the policy language for artifacts in governance docs.
Chat B may implement the read-side representation and registry logic.
Neither may violate the other’s file boundaries.
