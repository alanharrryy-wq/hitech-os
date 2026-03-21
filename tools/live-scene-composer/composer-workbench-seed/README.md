# Composer Workbench Seed (Live Scene Composer)

This folder contains a **surgical extraction** of generic plugin-kernel ideas from Repo Analyzer and translates them into a TypeScript/React-oriented module workbench seed for Live Scene Composer.

## What Was Extracted

The seed keeps only reusable kernel concepts:

- module manifest contract and validation
- module base lifecycle contract (`initialize` / `shutdown`)
- dependency-aware module loading
- lightweight service registry
- event bus primitive
- command dispatcher primitive

The original Python kernel files were copied verbatim into:

- `reference/repo-analyzer-plugin-kernel/`

These reference files are snapshots for architecture traceability only.

## What Was Intentionally NOT Extracted

The following Repo Analyzer patterns were intentionally excluded:

- dock contribution model
- toolbar contribution model
- menu contribution model
- main-window integration model
- contribution bridge and shell routing
- Repo Analyzer-specific plugins and demos

This seed does not assume "everything is a panel" and does not bring host-specific Qt shell conventions into Live Scene Composer.

## How This Differs From Repo Analyzer

Repo Analyzer plugin runtime:

- dynamic discovery through plugin files/manifests
- host-coupled UI contribution paths (dock/menu/toolbar)
- plugin context exposing host UI registration APIs

Composer workbench seed runtime:

- explicit module registration only
- bounded module ownership in manifest (`owner` required)
- no dock/menu/toolbar abstractions
- module context exposes only core runtime primitives and controlled mutation request seam

## Why This Is a Generic Composer Workbench Seed

This seed is a **host seam** for future Composer modules, not a full editor.

It provides:

- a minimal module runtime and lifecycle surface
- a simple three-column workbench model
- safe-mode and bridge-route status strip
- adapter-only mutation gateway stub (`runtime-mutation-bridge-adapter`)

It intentionally defers:

- concrete runtime bridge implementation
- real editor surfaces and inspectors
- production persistence / write execution flows

## Included Source Layout

- `src/core/*` primitives
- `src/modules/*` module contracts and loader
- `src/providers/*` workbench providers (selection, mutation, orchestration)
- `src/adapters/*` strict bridge adapter stub
- `src/workbench/*` simple workbench layout + module board
- `src/contracts.ts` shared contracts
- `src/index.ts` seed exports
