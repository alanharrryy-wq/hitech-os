# 71_INSTALLER_HARDENING_RULES

## Rules

1. All path handling must normalize to string safely.
2. The installer must fail early on missing package contents.
3. The installer must write readable summaries to the downloads root.
4. Post-install verification must run unless explicitly skipped.
5. Optional checks must be recorded as skipped rather than silently omitted.
6. The installer must not depend on `ProcessStartInfo.ArgumentList`.
7. Progress must remain visible throughout the run.

## Anti-patterns

- assuming every path-like value has `.Path`
- relying on one exact repo layout only
- claiming success after only extracting the zip
- swallowing failures inside helper tools
