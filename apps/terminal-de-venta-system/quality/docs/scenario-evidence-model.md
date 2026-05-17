# Scenario Evidence Model

Every scenario declares:

- id
- title
- owner
- vertical
- layer
- preconditions
- expectedEvidence
- checks
- mutates:false
- startsServices:false
- requiresCloudflare:false

Status:

- READY: all checks passed and actual evidence exists.
- PARTIAL: some evidence exists but the scenario is not fully proven.
- MISSING: no usable evidence exists.

Fake green is forbidden.
