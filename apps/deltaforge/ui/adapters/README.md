# DeltaForge UI Adapters

This folder contains app-specific adapters that consume the shared framework.

## Boundary

- `forgeos/shared/pyside6_glass/*` is framework core.
- `apps/deltaforge/ui/adapters/*` is DeltaForge-only wiring.

## Current adapter

- `glass_framework_adapter.py`
  - registers DeltaForge icon pack from `apps/deltaforge/assets/icons`
  - sets DeltaForge default icon pack at app startup
  - defines DeltaForge-specific template defaults without changing shared core contracts
