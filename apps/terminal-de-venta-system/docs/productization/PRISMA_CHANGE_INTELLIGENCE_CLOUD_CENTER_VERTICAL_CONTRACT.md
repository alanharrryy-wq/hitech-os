# PRISMA Change Intelligence — Cloud Center Vertical Contract V1

Status: `SOURCE_IMPLEMENTED / RUNTIME_VERIFIED / VISUAL_PARITY_FIX_GOVERNED / PRODUCTION_NOT_CERTIFIED`

## Purpose

PRISMA Change Intelligence is a read-only PRISMA vertical surfaced through Prisma Cloud Center. It commercializes the governed Change Intelligence product model while preserving Code Atlas as the internal repository-intelligence engine and preserving Prisma Cloud Center as the visual authority for Cloud Center-family surfaces.

The vertical exposes:

- Overview
- Repositories
- Analysis Runs
- Discover
- Guard
- Control
- Authority Packs
- Evidence
- ROI
- Entitlements

Repository, run, Authority Pack and evidence datasets remain `NOT_CONNECTED` until real adapters are separately governed and implemented.

## Authority chain

Initial implementation authority:

- base: `main@d14effee1a1223cc772247ea9d7ec8547dc15c78`
- run: `32156981312`
- artifact: `9332162633`
- profile: `ci-cloud-vertical-v3`
- composed result: `PASS_COMPOSED_AUTHORITY_MESH`
- Layer Map: present

Runtime closure authority was subsequently refreshed for the permanent Chromium gate.

Visual-parity maintenance authority:

- governed base: `main@42a533c0085aafdc32b27b854b14615d2b695070`
- profile: `ci-cloud-visual-parity-v1b`
- request id: `673778b7c29a4a85`
- first accepted Remote AutoMesh run: `32210004211`
- artifact: `9350436585`
- composed result: `PASS_COMPOSED_AUTHORITY_MESH`
- lanes: `2/2 PASS`
- required authority/directory coverage: `100%`
- missing authority: none
- Layer Map: present in both lanes

A mechanically duplicated run with the same request id grants no additional authority.

## Ownership and anti-rework matrix

| Capability | Decision | Rule |
|---|---|---|
| Customer registration | `REUSE_AS_IS` | Existing owner remains `doNotRebuild=true`. |
| Licensing / entitlements | `SHARED_OWNER` | Adapt later; do not rebuild licensing. |
| Customer Setup | `SHARED_OWNER` | Setup codes are not repository authorization. |
| Commercial Billing | `SHARED_OWNER` | Do not rebuild collections, CFDI or payment records. |
| Private repository rental hardening | `ADAPT` | Reuse bounded ephemeral workspace and egress controls from PR #299. |
| Change Intelligence / Code Atlas engine | `REUSE_AS_IS` | Internal engine remains authoritative and `doNotRebuild=true`. |
| Existing Cloud Center runtime and UI | `DO_NOT_TOUCH` | Existing Cloud Center HTML/CSS/JS remain owners. |
| Prisma Cloud Center visual system | `READ-ONLY visual authority` | Change Intelligence must inherit the current visual grammar; it must not fork a competing brand dialect. |
| Change Intelligence web console | `NEW_OWNER` | Own functional `pci-*` namespace and projection behavior only. |
| Change Intelligence browser authority gate | `NEW_OWNER` | Dedicated source + Chromium runtime verification and evidence artifact. |

## Visual contract

Visual contract id:

`PRISMA_CLOUD_CENTER_STORMGLASS_LITE_V1`

The canonical visual authority is read-only:

- `Prisma Cloud Ctr/internal/web/cloud_command_center.css`
- `Prisma Cloud Ctr/internal/web/cloud_command_center.html`

The Change Intelligence document loads the existing canonical stylesheet and then injects a narrowly scoped `pci-*` adapter. The adapter consumes canonical `--cc-*` tokens and reproduces Cloud Center geometry/material rules while preserving Change Intelligence functional ownership.

This means:

- Cloud Center owns visual meaning and current Stormglass Lite material.
- `pci-*` owns Change Intelligence functional location/projection.
- no `.cc-*` selector is authored in the Change Intelligence adapter.
- no canonical Cloud Center file is modified.
- no new standalone CSS file is created.
- no `!important` is allowed.

The adapter exists because Commercial Billing Authority intentionally rejects a changed `.css` path in this slice. Linking the already-existing canonical stylesheet does not mutate that owner.

## Layer Map

| Canonical visual layer | Change Intelligence projection | Contract |
|---|---|---|
| body photo + atmosphere | `body.pci-surface` + `.pci-atmosphere` | Same Cloud Center background photo, brighter Stormglass atmosphere, low overlay density. |
| floating topbar | `.pci-topbar` | 1360px bounded floating glass, 28px radius, low blur; never sticky/fixed. |
| crystal mark + PRISMA hierarchy | `.pci-brand-mark`, `.pci-logo-word`, `.pci-brand-*` | Unboxed 64px crystal mark, PRISMA wordmark hierarchy and Cloud Center typography rhythm. |
| status strip | `.pci-topbar-actions`, `.pci-status-chip` | Unboxed textual statuses with separators; only navigation/action link remains a pill. |
| horizontal pill navigation | `.pci-nav` | Horizontal flex pills; mobile is nowrap + horizontal scroll. No sidebar rail. |
| hero + seal | `.pci-hero`, `.pci-hero-seal` | One 24px Stormglass panel, large title, right-side seal desktop, one-column mobile. |
| 12-column surface | `.pci-content`, `.pci-grid`, `.pci-card` | 12-column grid, canonical span behavior and 24px low-blur panels. |
| metrics / key values | `.pci-kpi-grid`, `.pci-kpi` | Low-density nested metric surfaces, not opaque dashboard tiles. |
| tables / evidence / code | `.pci-table*`, `.pci-list*`, `.pci-code`, `.pci-formula` | Same light-line, low-opacity material family. |
| accessibility | `:focus-visible`, media queries | Keyboard focus, reduced motion, reduced transparency. |

The previous independent dark-dashboard language is explicitly not canonical. In particular, the visual contract rejects:

- the `#060b12` independent dark root;
- a fixed 250px sidebar/rail layout;
- sticky full-width topbar;
- boxed logo mark;
- 18–26px heavy blur as the base material;
- opaque `.82` panel fills as the default surface language.

## Browser/runtime authority gate

`.github/workflows/change-intelligence-cloud-authority.yml` remains the permanent vertical gate.

It must:

1. run `verify-cloud-center-change-intelligence-01.py`;
2. install isolated pinned Playwright/Chromium without repository lockfile mutation;
3. serve the checked-out Cloud Center tree on ephemeral localhost;
4. run desktop `1440×1000` and mobile `390×844`;
5. exercise all ten Change Intelligence views;
6. require governed config and conservative maturity;
7. require fail-closed vocabulary (`UNKNOWN`, `NOT_CONNECTED`, `BLOCKED`);
8. preserve the intentional disconnected `/api/health` 404 as explicit evidence;
9. fail on every unexpected console/page/HTTP error;
10. verify the visual contract in computed browser styles;
11. require the canonical Cloud Center stylesheet to be loaded;
12. require floating 28px topbar, unboxed crystal mark, horizontal nav, no legacy sidebar, 24px/2px-blur Stormglass Lite hero/cards, and responsive mobile navigation;
13. upload report and screenshots.

A successful browser gate proves this isolated surface is runtime-verified and visually aligned to the named contract. It does not make the product production-certified.

## Source verifier maintenance boundary

The source verifier keeps the original creation allowlist as an upper bound, but maintenance pull requests are evaluated as a non-empty subset of that allowlist rather than being forced to modify every file created by the original PR.

Every maintenance PR still fails closed when:

- any changed path falls outside the allowed owner set;
- canonical Cloud Center visual authority files are changed;
- any `.css` file is changed;
- a standalone Change Intelligence CSS file appears;
- `!important` or `.cc-*` selectors are introduced into the adapter;
- canonical visual markers disappear;
- visual contract markers or runtime computed-style checks disappear.

Historical Authority Mesh provenance and current PR diff boundaries remain separate concepts.

## No-fake-green ceiling

Current underlying Change Intelligence evidence remains:

- engine: `LOCAL_VERIFIED`
- `certifiable=false`
- `productionCertified=false`
- `humanUsefulness=NOT_MEASURED`
- human-study tooling: `HUMAN_USEFULNESS_STUDY_KIT_READY_NOT_MEASURED`
- independent evaluator: `BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR`

This vertical must not claim:

- hosted multi-tenant execution
- paid-pilot readiness
- enterprise IAM/security certification
- legal/privacy compliance
- production certification
- measured human usefulness
- successful independent-agent replication

## Runtime and mutation boundary

The V1 vertical is read-only. It must not:

- mutate repository source from the browser;
- accept repository credentials in the browser;
- persist secrets in local/session storage;
- call POST/PUT/PATCH/DELETE from the browser projection;
- start or kill product dev servers;
- free ports;
- mutate Prisma/DB/D1;
- deploy Cloudflare or other infrastructure;
- touch Tablet, PC, Mobile, Chart Lab or Shared UI;
- rebuild licensing, registration or billing;
- mutate Code Atlas UI Bridge/UIMAP or frozen evaluator lanes.

The CI browser test is an ephemeral test-only localhost server in GitHub Actions, not a product runtime or hosted environment.

## Commercial Billing Authority compatibility

Commercial Billing Authority remains unmodified. No `.css` path is changed by the Change Intelligence visual-parity maintenance work. The already-existing canonical Cloud Center CSS is loaded read-only, while the Change Intelligence adapter remains a JavaScript-injected scoped style owner.

Commercial billing and fiscal owners remain outside this vertical.

## Next implementation gates

After source, runtime and visual parity are green:

1. read-only repository registry adapter;
2. real Code Atlas analysis-run projection;
3. Authority Pack and Evidence Report reference adapter;
4. Change Intelligence entitlement projection from the existing licensing owner;
5. customer-input ROI instrumentation;
6. external manual accuracy/claim-support sample;
7. real external-human usefulness response and score;
8. external time-to-value / customer ROI baseline;
9. independent evaluator evidence;
10. separately governed hosted/enterprise productization.

## Governance closure

Factory Ledger and Evidence Index are not promoted by visual parity alone. Maturity registration must preserve the evidence ceiling above. Visual consistency is a product-quality requirement, not evidence of production readiness.
