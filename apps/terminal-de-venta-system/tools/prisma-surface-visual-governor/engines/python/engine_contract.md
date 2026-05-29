# Python Engine Contract

Every future Python engine should provide:

```txt
input:
  repo_root
  drop_root
  mode: audit | install | remediate
output:
  result_zip
  receipt.json
  install.log
  inventory json/csv
  protected_hashes.before/after
```

Never silently mutate POS, checkout, DB, dependencies, lockfiles or deploy config.
