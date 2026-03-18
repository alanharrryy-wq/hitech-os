# 94 Inspector Preview / Commit Controller

The inspector should preview while the user edits and should only commit when the user chooses an explicit accept action.

This controller owns:
- dirty state per inspector section
- staged field groups
- compare badges
- apply bar readiness
- mapping from focused section to mutation payloads
