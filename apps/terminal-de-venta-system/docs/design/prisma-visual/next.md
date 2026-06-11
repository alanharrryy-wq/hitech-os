# Next

## Phase one: apply curation map

Create these repo files, with clear names:

- `docs/design/prisma-visual/README.md`
- `docs/design/prisma-visual/authority.md`
- `docs/design/prisma-visual/recipes.md`
- `docs/design/prisma-visual/library.md`
- `docs/design/prisma-visual/layer-map.md`
- `docs/design/prisma-visual/cleanup.md`
- `docs/design/prisma-visual/archive.md`
- `docs/design/prisma-visual/next.md`
- `config/prisma-visual/authority-map.json`
- `config/prisma-visual/recipe-map.json`
- `config/prisma-visual/library-map.json`
- `config/prisma-visual/layer-budget.json`
- `config/prisma-visual/cleanup-map.json`
- `config/prisma-visual/archive-map.json`

## Compatibility

Keep existing `prisma-visual-system` paths working until validators and imports are migrated. Do not rename live paths in the same move unless there is rollback and proof.

## Phase two: Tablet layer diet

Start with `/pos` and `/checkout`, using `layer-budget.json` and `cleanup-map.json`. No PC/Mobile/Chart Lab changes.

## Definition of done

- Authority map created.
- Deprecated sources blocked from new work.
- Recipes distilled.
- Layer budget validator planned or implemented.
- Visual QA evidence linked.
- No runtime UI changed in audit phase.
