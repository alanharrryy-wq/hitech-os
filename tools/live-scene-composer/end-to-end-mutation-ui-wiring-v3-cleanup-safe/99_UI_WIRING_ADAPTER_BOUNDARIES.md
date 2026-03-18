# 99 UI Wiring Adapter Boundaries

UI wiring may call:
- mutation-client helpers
- preview-session helpers
- bridge client helpers
- diagnostics / evidence emitters

UI wiring may not:
- write runtime state directly
- perform hidden adapter routing outside the bridge client
- replace scene model truth with UI-local snapshots
