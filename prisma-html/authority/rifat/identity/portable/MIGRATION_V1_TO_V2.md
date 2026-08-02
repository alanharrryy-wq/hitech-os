# Portable visual artifact migration: V1 to V2

IDRECIPE1 is an additive extension.

- Existing `prisma.identity.portable-element-export.v1` files remain byte-for-byte
  unchanged.
- V2 introduces `kind=full-stack-recipe`, explicit independent statuses,
  concrete binding/layer trace and full visual-stack/state/variant coverage.
- V2 references the canonical V1 export through `sourceArtifact.exportId`.
- Legacy names are resolved only through
  `registries/legacy-aliases.registry.json`.
- Import remains read-only. No V2 artifact can apply product or runtime changes.

Run:

```text
python -B tools/migrate_portable_identity_v1_to_v2.py --check-only
```

The gate validates compatibility, integrity and deterministic export/import
round trip. It never rewrites V1.
