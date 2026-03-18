# 96 UI Wiring State Machine

States:
- idle
- selected
- editing-preview
- preview-ready
- commit-pending
- commit-applied
- discard-pending
- rejected

Transitions must remain explicit so preview cannot silently collapse into accepted state.
