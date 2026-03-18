# 91 Surface Action to Mutation Map

## Canvas
- drag layout node -> layout-move preview
- resize layout node -> layout-resize preview
- select widget -> selection-only, no mutation

## Structure Tree
- reorder layout node -> layout-reorder style path through layout-move payload
- move widget between slots -> slot-insert-widget + widget-remove sequence
- select slot -> selection-only, no mutation

## Inspector
- change widget props -> widget-props-update preview
- change widget style -> widget-style-update preview
- change scene look -> scene-look-update preview

## Toolbar / Hotkeys
- apply / commit -> draft-commit
- discard -> draft-discard
- reset selected -> selected-element-reset
