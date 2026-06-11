# PRISMA Visual Capability Resolver

## Purpose

The Visual Capability Resolver is a native Authority Mesh module. It detects visual libraries, PRISMA visual assets, recipes, Visual OS, backgrounds, layer budgets, surface adapters, and candidate target files before any premium or visual change.

It prevents two failure modes:

1. Under-exploitation: only blur/shadow/radius and fake premium.
2. Over-exploitation: using every library blindly and damaging performance, clarity, or governance.

## Generated files

- `.governance/current/VISUAL_CAPABILITY_MATRIX.json`
- `.governance/current/VISUAL_CAPABILITY_MATRIX.md`
- `.governance/current/VISUAL_STACK_DECISION.md`
- `.governance/current/APP_VISUAL_EXPLOITATION_MATRIX.md`

## Required interpretation

A capability being available does not mean it must be used. It means it must be considered and either used or rejected with a reason.

## Rule

No visual/premium work is valid unless the final result package includes:
- used capabilities;
- rejected capabilities with reasons;
- layer budget notes;
- performance risk notes;
- visual evidence or explicit pending visual verification.

## App-aware behavior

The resolver produces app/surface recommendations for Tablet, PC, Mobile, Chart Lab, Web, Shared UI, and Backgrounds. It should be used together with the Authority Readset, App Impact Matrix, Contract/Gate Matrix, and Missing/Unmapped Risk review.
