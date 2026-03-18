# Implementation notes

This pack deliberately keeps UI wiring as a seam, not as a silent runtime shortcut.

The new source folder focuses on:

- surface action envelopes
- target resolution from selection context
- preview-vs-commit route choice
- compare/apply bar state
- evidence and diagnostics emitted from UI-facing orchestration

The source is intentionally package-local and staged through tools first so the repo can absorb it with reviewable evidence.
