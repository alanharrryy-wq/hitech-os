# AUTHORING_WORKBENCH_V1_WAVE1

This governance note records the bounded Wave 1 vertical slice for Authoring Workbench v1.

## Delivered seams
- explicit Selection model with Scene / Layout Node / Slot / Widget targets
- Inspector Target derived from Selection
- synchronized Canvas, Structure, and Inspector surfaces
- Scene Look editing surface using the existing scene-look-model contract
- typed mutation client that routes only through runtime-mutation-bridge/authoring-workbench-v1
- explicit draft commit, draft discard, and selected-element reset controls

## Boundary posture
- new code lives under `authoring-workbench-v1` subtrees
- no runtime-debug-console imports
- no direct pitch or scene-studio write shortcuts
- runtime-facing writes remain bridge-governed

## Safe Mode posture
Safe Mode remains the default authority posture. Every delivered command is typed and validated before draft changes are accepted.

## Known follow-up work
- real runtime adapters for pitch or scene-studio paths
- repo-native wiring into the existing product shell after source-root confirmation
- deeper widget-specific inspector sections and richer direct manipulation
