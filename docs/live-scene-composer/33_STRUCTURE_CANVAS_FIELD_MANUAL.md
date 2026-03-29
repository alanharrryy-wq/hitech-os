
# 33_STRUCTURE_CANVAS_FIELD_MANUAL

## What this pack gives you today

- a synchronized tree/canvas reference seam
- deterministic event normalization
- clear stale/recovery behavior
- typed mutation-intent entrypoints
- fixtures and traces to review before touching runtime paths

## What to do first in the repo

- install it
- inspect the staging root
- map the closest real composer source path
- wire one surface at a time behind adapters

## What not to do

- do not let canvas become a secret state owner
- do not let tree auto-retarget selection invisibly
- do not call runtime-facing writes directly from overlays or tree actions
- do not flatten scene/layout/slot/widget semantics

## Definition of done for this layer

- tree and canvas respond from one selection truth
- stale state behaves consistently
- mutation-intent entrypoints expose correct availability
- diagnostics make surface drift visible instead of mysterious
