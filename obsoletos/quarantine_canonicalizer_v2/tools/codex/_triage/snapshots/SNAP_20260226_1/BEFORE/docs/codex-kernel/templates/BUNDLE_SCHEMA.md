# BUNDLE_SCHEMA — Standard Run Bundle Layout

STATUS: TEMPLATE

## Recommended directory layout

tools/codex/runs/<RUN*ID>/
A_core/
STATUS.json
SUMMARY.md
FILES_CHANGED.json
DIFF.patch
LOGS/
typecheck.log.txt
build.log.txt
tests.log.txt
SUGGESTIONS.md
B_surface/
...
C_tooling/
...
D_validation/
...
Z_integrator/
STATUS.json
FINAL_REPORT.txt
MERGE_PLAN.md
FILES_CHANGED.json
DIFF.patch
LOGS/
validate*\*.log.txt

## Minimal required files

- STATUS.json (machine readable)
- DIFF.patch
- At least one LOGS/ file or COMMAND LOGS in report
