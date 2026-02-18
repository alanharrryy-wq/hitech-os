# Guard: no_js_src_imports
STATUS: ACTIVE

Purpose: prevent regressions where TypeScript source under `src/**` imports relative `.js` paths that do not exist at runtime in strip-types mode.

## Command

```bash
python tools/codex/guards/no_js_src_imports.py --repo . --config tools/codex/guards/no_js_src_imports.allowlist.json
```

## Policy
- Fails on relative import/export specifiers ending with `.js` in `src/**/*.ts|tsx|mts|cts`.
- Allows explicit exceptions through `tools/codex/guards/no_js_src_imports.allowlist.json`.
- Output is deterministic and sorted.

## Allowlist Format

```json
{
  "allow": [
    { "file_glob": "packages/contracts/src/**/*.ts", "specifier_glob": "*.js" }
  ]
}
```

Use exceptions only when a package intentionally compiles TS source to JS with `.js` specifiers.
