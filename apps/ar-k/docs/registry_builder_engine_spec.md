# Registry Builder Engine Spec

Iteration-1 behavior:
- build module registry
- build boundary registry
- publish contract registry baseline
- generate switch registry defaults
- write query index
- emit one registry snapshot and one delta

Current promotion policy:
- promote only canonical product/runtime module candidates
- reject non-product candidates (`docs`, `reports`, `tests`, `tooling`, `scripts`, `fixtures`, `examples`, rollback/history/artifact classes)
- record skipped candidates with reasons in `artifacts/metrics/registry_build_summary.json`
