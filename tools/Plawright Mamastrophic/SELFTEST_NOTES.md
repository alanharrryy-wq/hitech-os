# SELFTEST NOTES

Local validation performed in the packaging sandbox:

- `node --check tests/surf8.deep-capture.cjs`
- `node --check tests/surf8.all-surfaces.engine.cjs`
- `node --check tests/surf8.visualqa.engine.cjs`
- `python -m py_compile core/surf8_discovery.py core/visualqa_aggregate.py core/deep_capture.py`

PowerShell execution against the real repo/services must be validated on the user machine because the sandbox has no `F:\repos\hitech-os`, no Windows PowerShell runtime, and no live PRISMA ports.

arr13 changes included:

- `screenshots` mode;
- `screenshotsqa` mode;
- app-bundled max-six-ZIP policy for `all`;
- live `[MAM-PROGRESS]` events and `progress.jsonl`;
- `AllowPartial` respected for scroll partial coverage;
- no process kill/start/port cleanup behavior added.
