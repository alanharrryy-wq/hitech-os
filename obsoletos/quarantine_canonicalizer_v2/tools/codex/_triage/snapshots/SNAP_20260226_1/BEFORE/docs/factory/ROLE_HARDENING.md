# Role Hardening

## A/B/C/D workers

- Must stay inside declared scope lock.
- Must emit required bundle artifacts.
- Must not write to another worker bundle.

## Z integrator

- Must never invent features.
- Must only merge, validate, report.
- Must block run on missing required artifacts.
