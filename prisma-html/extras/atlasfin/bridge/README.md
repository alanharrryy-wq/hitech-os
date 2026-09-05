# Atlasfin Visual Promotion Bridge

Status: `CHAT5_READ_ONLY_BRIDGE`

This directory is the bounded implementation owned by **Chat 5 — Atlasfin Bridge** from
`prisma-html/docs/ops/visual-promotion-parallel/PRISMA_VISUAL_PROMOTION_PARALLEL_CHAT_PROMPTS.md`.

## Role

Atlasfin remains the priority human cockpit/reference for visual promotion. This bridge reads
current Atlasfin catalog/registry authority and optional surface-worker candidate shards, then
projects a read-only interoperability view.

It does **not** become a second editable visual authority and it does **not** write product
runtime, Identity/RIFAT authority, generated product projections, Target Index, Factory Ledger,
or another chat's candidate directory.

## Hard boundaries

- Existing 418-element Atlasfin catalog is reused, never rebuilt.
- `DISCOVERY_ONLY` is not treated as undiscovered.
- Broad rediscovery is forbidden.
- Atlasfin-first is mandatory.
- Surface Visual Governor Materiality Catalog remains
  `STANDBY_USER_INVOKED_ONLY`. The bridge contains a fail-closed path guard and never inspects,
  imports, promotes, or falls back to that catalog.
- Unknown remains unknown.
- Missing Chat 1–4 candidate directories become `PENDING_NOT_PRESENT`; the bridge does not
  fabricate worker data.
- Existing authority IDs remain immutable. The bridge never mints canonical `BND.*`,
  `TGT.*`, `LYR.*`, Identity recipe IDs, NDC IDs, or adapters.
- Cross-authority IDs use `{ "authorityDomain": "...", "id": "..." }`.
- Atlasfin recipe IDs and Identity recipe IDs stay in separate fields/domains.
- Static/source evidence never becomes runtime visual certification.

## Sources

The bridge consumes only current repository truth required by Chat 5:

- `extras/atlasfin/assets/data/atlas.manifest.json`
- structured Atlasfin property/family/preset/recipe/state/variant/adapter/asset registries
- current Cobrar pilot and application evidence
- optional current VISCORE JSON feed, when materialized
- optional candidate shards under
  `prisma-html/governance/visual-promotion/candidates/{tablet,pc,mobile,shared-ui}/`

The VISCORE Atlasfin feed is currently allowed to be absent. Absence is rendered as
`PENDING_NOT_PRESENT`, not as a synthetic PASS/FAIL.

## Commands

From repository root:

```bash
python prisma-html/extras/atlasfin/bridge/atlasfin_bridge.py check
python prisma-html/extras/atlasfin/bridge/atlasfin_bridge.py snapshot
python prisma-html/extras/atlasfin/bridge/atlasfin_bridge.py snapshot \
  --out prisma-html/extras/atlasfin/bridge/out/bridge.snapshot.json
python prisma-html/extras/atlasfin/bridge/test_atlasfin_bridge.py
```

For lane evidence tied to a known source base, pass the exact base explicitly **before** the
subcommand:

```bash
python prisma-html/extras/atlasfin/bridge/atlasfin_bridge.py \
  --base-head <40-char-git-sha> check
```

Snapshot file writes are fail-closed outside `prisma-html/extras/atlasfin/bridge/**`.
Normal `check` and stdout `snapshot` are read-only.

## Output semantics

The bridge can represent:

- Atlasfin catalog elements;
- properties, families, presets, recipes, states and variants;
- Atlasfin adapters;
- authority-qualified references;
- NDC refs and canonical visual meaning when supplied by current authority/candidates;
- exact RIFAT coordinates when current evidence proves them;
- projection, binding and promotion state;
- blockers and evidence;
- Work Entry decisions when present.

Worker data is consumed only as candidate evidence. Candidate is not authority, binding is not
authorization, authorization is not mutation, and mutation is not runtime certification.
