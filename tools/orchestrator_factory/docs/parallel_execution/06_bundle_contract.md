
# Bundle Contract

Minimum bundle shape:

```text
<bundle>.zip
├── bundle_manifest.json
├── package_report.json
├── notes/
│   └── summary.md
└── payload/
    └── <repo-relative files>
```

## Rules
- `payload/` uses repo-relative paths
- every payload file appears in the manifest
- deletes are disallowed by default
- checksums are per file
- bundle ID includes run, round, package, and version
- report and manifest must agree on package and bundle identity

## Recommended additive fields
When applicable, add:
- `work_packet_ref`
- `contract_refs`
- `waiver_refs`

These fields improve traceability without changing the minimum valid bundle shape.
