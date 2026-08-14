# Temporary governed payload

This directory contains a compressed, SHA-256 locked patch payload used only by `cloudcust-apply-once.yml` on the `cloudcust-governed-20260814` PR branch.

The one-shot workflow must verify exact preimage blob SHAs, patch digest, exact mutation scope, static checks, temporary-SQLite behavior and sandbox runtime UI before committing product files. These temporary files and the workflow are removed before merge.
