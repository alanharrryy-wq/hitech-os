# Hydration Sentinel PRO - ZIP 1 Core Engine

This package provides the scanning core for Hydration Sentinel PRO.

Highlights:

- discovers relevant source files while filtering compiled and generated artifacts
- indexes explicit client boundaries using `use client`
- resolves local imports for cross-file boundary hints
- supports baseline ignore files
- supports diff-based targeted scans through git
- emits stable finding fingerprints for downstream reporting

Quick start:

```bash
python -m tools.hydration_sentinel.cli.sentinel_cli --repo-root F:\repos\hitech-os --config tools/hydration_sentinel/config.json --print-summary
```

Generate machine readable outputs:

```bash
python -m tools.hydration_sentinel.cli.sentinel_cli \
  --repo-root F:\repos\hitech-os \
  --config tools/hydration_sentinel/config.json \
  --write-json _reports/hydration_sentinel/latest/findings.json \
  --write-summary _reports/hydration_sentinel/latest/summary.json
```

Notes:

- ZIP 1 intentionally keeps reporting simple. Rich reporting lands in ZIP 2.
- ZIP 1 already establishes stable contracts for rules, risk scoring, and graph analysis to plug in later.
