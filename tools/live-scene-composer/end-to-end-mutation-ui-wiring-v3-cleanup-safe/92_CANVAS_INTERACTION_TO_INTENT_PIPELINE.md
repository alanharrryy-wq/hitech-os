# 92 Canvas Interaction to Intent Pipeline

Canvas interactions should not mutate runtime-facing state directly.

Instead they produce:

- normalized pointer geometry
- current selection context
- bounded payload fields
- mutation source `canvas`
- preview-first scope unless the user explicitly commits

Canvas owns direct manipulation feel. It does not own mutation governance.
