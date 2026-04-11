# Switch Engine Spec

Iteration-1 behavior:
- load switch targets
- apply default, switch-id override, then target-id override
- ignore invalid override types with a warning event
- publish deterministic decision trace
