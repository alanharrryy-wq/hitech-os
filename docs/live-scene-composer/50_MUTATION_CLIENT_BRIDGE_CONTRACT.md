# 50_MUTATION_CLIENT_BRIDGE_CONTRACT

## Status
- Status: Proposed Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Mutation client role and its disciplined relationship to runtime-mutation-bridge

## Purpose

This document defines the mutation-client layer inside Live Scene Composer.

The mutation client exists because the composer needs a place to:
- turn surface actions into typed mutation requests
- preserve target / source / mode / scope explicitly
- coordinate preview versus commit semantics
- remain bridge-safe without importing runtime detail everywhere
- collect diagnostics and failure reasons in one legible path

The mutation client is **not** the bridge itself.
It is the bounded client-side seam that speaks to the bridge.

## Core principles

### Principle 1: The client builds typed requests
The client must produce explicit mutation envelopes, not vague "update anything" blobs.

### Principle 2: The client never bypasses the bridge
The client may stage preview sessions or local diagnostics, but every runtime-facing write-capable effect still crosses the bridge boundary.

### Principle 3: Preview is first-class
Preview is not a throwaway visual side effect.
It is a distinct and testable state of the authoring workflow.

### Principle 4: Commit is deliberate
Commit must be a separate transition from preview.
It must not happen just because something became visible.

### Principle 5: Revert and discard stay explicit
The client should make reset, revert, and discard flows readable in code and diagnostics.

## Required concepts

The mutation client contract must keep these fields explicit:
- mutation id
- source
- type
- mode
- scope
- target
- payload
- preview session id when relevant
- reversibility metadata
- request timestamp

## Allowed responsibilities
- build mutation intents from surface actions
- perform shallow validation before bridge round-trip
- keep preview-session bookkeeping
- orchestrate commit/discard/revert flows
- normalize adapter-facing envelopes
- collect diagnostics and history
- expose hook-friendly state to UI surfaces

## Forbidden responsibilities
- direct runtime writes
- owning the scene model
- inventing target ids from DOM-only state
- silently promoting preview into commit
- bypassing safe-mode policy
- hiding rejection paths
