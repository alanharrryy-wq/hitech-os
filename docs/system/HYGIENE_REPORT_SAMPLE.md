# HYGIENE_REPORT_SAMPLE

Example high-level report shape emitted by `tools/hos/hygiene/cli_hygiene.py`.

```json
{
  "ok": true,
  "issues": 0,
  "strict": false,
  "checks": {
    "rootArtifacts": {
      "ok": true,
      "suspiciousFileCount": 0,
      "suspiciousDirCount": 0
    },
    "worktreeContamination": {
      "ok": true,
      "entryCount": 0
    },
    "largeFiles": null
  }
}
```

When `--include-large-files` is enabled, `checks.largeFiles.files` includes path + byte size rows.

