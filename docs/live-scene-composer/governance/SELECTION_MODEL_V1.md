# SELECTION_MODEL_V1

## Purpose
Provide a canonical focus model for editor interaction.

## Target Types
- Scene
- LayoutNode
- Slot
- Widget

## Selection State
- primaryTarget
- sourceSurface
- mode (safe | advanced)

## Rules
1. Selection represents editor focus only.
2. Selection does not mutate domain state.
3. Selection is synchronized across:
   - Canvas
   - Structure tree
   - Inspector
