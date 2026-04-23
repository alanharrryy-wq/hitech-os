# Canonical Promotion Policy

This policy defines how Ar-k promotes scanner observations into `module_registry`.

## Promotion categories

1. `product/runtime canonical`
- paths that are canonical sources and emit promotable module candidates
- examples: `app/**`, `components/**`, `src/**`, runtime entrypoints, UI modules, python runtime modules

2. `non-canonical observed`
- paths that stay visible in scanner inventory/signals but are not promoted
- classes: `docs`, `reports`, `graphs`, `tests`, `tooling`, `scripts`, `fixtures`, `examples`, hidden paths, history/rollback artifacts, backups

3. `unsupported surface observed`
- scanner may observe non-promotable surface kinds
- registry builder filters them from canonical promotion

## Deterministic enforcement

- scanner annotates each observed file with:
  - `canonical_source`
  - `non_product_class` when applicable
- registry_builder applies the same path policy and rejects non-product candidates even if a candidate signal exists.
- `registry_build_summary.json` records:
  - `skipped_module_candidate_paths`
  - `skipped_module_candidates`
  - `skipped_module_candidate_reasons`

## Real-target validation command

```powershell
$root = "F:\repos\hitech-os\apps\Ar-k"
$target = "F:\repos\hitech-os\apps\external_interaction_template"
$out = "$root\reports_real"
$env:PYTHONPATH = $root

python -m pya.tools.pya run --root $root --target $target --out $out
```
