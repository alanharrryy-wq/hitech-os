# 70_MUTATION_INTEGRATION_HARDENING_OVERVIEW

## Purpose

This document defines the hardening layer around the mutation integration path for Live Scene Composer.

The goal is not to invent a second mutation model.
The goal is to make the intended mutation model installable, reviewable, and verifiable inside the repo.

## Focus areas

- reliable packaging and installation
- explicit staging vs mirroring decisions
- post-install verification evidence
- smoke checks for mutation path boundaries
- operator-friendly diagnostics
- preservation of preview vs commit semantics

## Hardening principle

A mutation seam that exists only as a zip artifact but cannot be verified in the repo is not yet trustworthy.

## Required outputs

Every installation should emit evidence for:

- docs copied
- staged seam files copied
- mirrored seam files copied or intentionally skipped
- guard status
- smoke status
- verification status
- operator next commands
