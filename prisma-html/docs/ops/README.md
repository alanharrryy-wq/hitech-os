# PRISMA HTML Operations Documentation

Use this directory for operator-facing runbooks and learned operational rules. Machine-readable manifests, registries and validators remain the source of truth when prose is stale.

## Start here

- [`PRISMA_VISUAL_CHANGE_MASTER_MAP.md`](PRISMA_VISUAL_CHANGE_MASTER_MAP.md): canonical architecture/lifecycle contract and mandatory visual-change operator map. Read this before proposing, planning, authorizing, applying, or validating a PRISMA visual change.
- [`PRISMA_VISUAL_CHANGE_MASTER_MAP_ULTRA_TECHNICAL_20260905.md`](PRISMA_VISUAL_CHANGE_MASTER_MAP_ULTRA_TECHNICAL_20260905.md): generated, non-authoritative ultra-technical companion with the expanded order of operations, Control Plane/current-truth/readiness overlay, Target Index and binding anatomy, GVAE transaction/rollback rules, runtime QA, drift behavior, golden examples and agent startup sequence. The canonical Master Map and machine-readable authorities always win if this snapshot becomes stale.\n- [`PRISMA_VISUAL_CHANGE_MASTER_MAP_ULTRA_TECHNICAL_20260905.pdf`](PRISMA_VISUAL_CHANGE_MASTER_MAP_ULTRA_TECHNICAL_20260905.pdf): ASCII-safe A3-style PDF export of the ultra-technical companion for visual reading in GitHub.
- [`PRISMA_VISUAL_AUTHORITY_RUNBOOK.md`](PRISMA_VISUAL_AUTHORITY_RUNBOOK.md): canonical operating guide for VISCORE1, Identity Dictionary, RIFAT/prisma-ui, Atlasfin, projection drift, `FILES_MANIFEST.json`, certification and PR closure.
- [`PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`](PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md): practical lessons and traps already paid for.
- [`visual-promotion-parallel/README.md`](visual-promotion-parallel/README.md): canonical startup for the Tablet/PC/Mobile/Shared UI parallel semantic-promotion cohort, Atlasfin-first policy, interoperability contract, vocabulary and six chat prompts.

## Authority rule for the ultra-technical companion

The ultra-technical companion is a visual/educational snapshot for humans and agents. It does **not** become a second maintained authority.

When there is disagreement, use this precedence:

1. current machine-readable authority in its domain;
2. `PRISMA_VISUAL_CHANGE_MASTER_MAP.md`;
3. current runbooks / Field Manual for operational detail;
4. the dated ultra-technical companion as explanatory context only.

## Deployment-specific references

- [`PRISMA_HTML_CLOUDFLARE_PAGES_RUNBOOK.md`](PRISMA_HTML_CLOUDFLARE_PAGES_RUNBOOK.md)
- [`PRISMA_HTML_CLOUDFLARE_PAGES_ROLLBACK.md`](PRISMA_HTML_CLOUDFLARE_PAGES_ROLLBACK.md)
- [`PRISMA_HTML_CLOUDFLARE_AUTHORITY_SOURCES.md`](PRISMA_HTML_CLOUDFLARE_AUTHORITY_SOURCES.md)

Cloudflare deployment is a separate concern from visual-source authority and does not imply runtime visual `READY`.
