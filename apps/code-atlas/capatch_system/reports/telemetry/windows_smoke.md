# windows_smoke

- status: passed
- platform: Windows

## steps

- `smoke-test` => rc=0
- `plugin-health` => rc=0
- `apply` => rc=0
- `list-checkpoints` => rc=0
- `rollback-last` => rc=0
