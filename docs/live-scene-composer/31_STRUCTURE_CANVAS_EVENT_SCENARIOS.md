
# 31_STRUCTURE_CANVAS_EVENT_SCENARIOS

## Scenario families

### 1. Scene-root selection
- tree click selects scene
- canvas shows scene frame
- inspector gets scene-target context

### 2. Layout-node focus
- tree keyboard navigation focuses layout node
- Enter selects it
- canvas shows layout guides and handles

### 3. Slot insertion path
- canvas click selects slot boundary
- tree highlights slot under its parent layout node
- insert-widget intent becomes available

### 4. Widget removal drift
- selected widget is removed by a valid draft update
- selection becomes stale
- overlays clear
- tree clears active node and may show recovery diagnostics

### 5. Revision refresh with surviving target
- target still resolves
- revision token updates
- selection remains active
- overlays and tree highlight remain consistent

### 6. Background clear
- canvas background click clears selection when no modal affordance is active
- tree active highlight clears
- inspector shows empty state

### 7. Pointer ambiguity
- hit-test returns widget and slot candidate
- coordinator applies target priority rule
- widget wins unless mode overrides

### 8. Keyboard stale ghost
- keyboard focus lands near stale ghost node
- stale ghost may open recovery affordance
- it does not silently become active selection
