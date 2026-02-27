# Troubleshooting

## `AGENTS.md` missing

Use fallback: `docs/factory/AGENTS_FALLBACK.md`.

## Worktree create fails

- Confirm branch name is valid.
- Confirm local repo has git metadata.
- Retry with `--dry-run` first.

## Integration blocked by overlap

- Review `SCOPE_LOCK.json` per worker.
- Resolve ownership conflict.
- Re-run `bundle-validate` and `integrate`.
