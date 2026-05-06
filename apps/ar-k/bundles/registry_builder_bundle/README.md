# Ar-k Registry Builder Bundle

This governed handoff bundle packages the homologated stage_02 Registry Builder contract in Python-first form.

## Core canon
- Status wording: `READY FOR HANDOFF`
- Top-level archive root: `ark_registry_builder_bundle/`
- Canonical portable index name: `registry_index.json`
- Legacy `query_index.json` support: explicit shim only via `compat/query_index_alias.py`
- Default install root: `<root>/bundles/registry_builder_bundle`
- State root: `<root>/.ark_install/registry_builder_bundle/`
- Rollback state file: `<root>/.ark_install/registry_builder_bundle/last_apply.json`

## Installer
The installer is self-contained after unzip and intentionally requires an explicit `--root` so it never guesses the installation target from the current directory.

```bash
python registry_builder_installer.py --apply --root F:\repos\hitech-os\apps\Ar-k
```

Supported flags are limited to `--dry-run`, `--apply`, `--verify`, `--rollback`, `--root`, `--log-dir`, and `--install-rel`.
