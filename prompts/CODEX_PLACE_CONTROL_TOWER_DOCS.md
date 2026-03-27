You are receiving a document-only seed bundle for placement into the repository.

Your job is strictly to place the files from this bundle into their intended repository locations and preserve them exactly unless placement-specific normalization is absolutely required.

## Repository root
F:\repos\hitech-os

## Intended documentary destination
F:\repos\hitech-os\docs\orchestration

## Placement rules
1. Treat these docs as canonical baseline documents for the `control_tower` phase.
2. Do not weaken, summarize, or compress them.
3. Do not rename canonical vocabulary.
4. Do not create shadow copies in alternate folders.
5. Preserve file names and numbering order.
6. If a destination file already exists, compare before replacing and surface a clear conflict report instead of improvising semantic edits.
7. Do not introduce code files in this step. This is a docs-only placement step.
8. Preserve the distinction between protected operational domains and the new governance layer.

## Files intended for placement
All files under:
docs/orchestration/

## Support files
- meta/control_tower_docs_manifest.json
- prompts/CODEX_PLACE_CONTROL_TOWER_DOCS.md

These support files may remain outside the repo if desired, but the docs themselves must land in the canonical orchestration folder.

## Non-goals
- no reopening of `git_sentinel_modular`
- no reopening of `engine_guardian`
- no scheduler changes
- no Cloudflare healing
- no control_tower code generation in this step

## Deliverable expectation
Produce a clean placement result or a conflict report, not a reinterpretation.
