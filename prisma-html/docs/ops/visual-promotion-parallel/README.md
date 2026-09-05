# PRISMA Visual Promotion Parallel Cohort

Status: `CANONICAL_PARALLEL_WORK_ENTRY`

This folder is the startup point for the bounded parallel visual-promotion cohort covering **Tablet, PC, Mobile, Shared UI and Atlasfin**.

## Mandatory read order

Before doing any work from the prompts in this folder, read in this order:

1. `/AGENTS.md`
2. `apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`
3. `PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md`
4. `prisma-html/docs/ops/PRISMA_VISUAL_CHANGE_MASTER_MAP.md`
5. `prisma-html/authority/rifat/identity/contract/PRISMA_VISUAL_CORE_CONTRACT.md`
6. `PRISMA_VISUAL_PROMOTION_INTEROPERABILITY_CONTRACT.md`
7. `PRISMA_VISUAL_PROMOTION_VOCABULARY.registry.json`
8. `PRISMA_VISUAL_PROMOTION_PARALLEL_CHAT_PROMPTS.md`, then execute only the assigned chat section.

## Cohort scope

Included product surfaces:

- `tablet`
- `pc`
- `mobile`
- `shared-ui`

Atlasfin is the priority visual reference/cockpit for this cohort and remains a consumer/operator of authority, not a second editable authority.

Explicitly excluded from semantic-promotion work in this cohort:

- `web`
- `chart-lab`
- `control-center`

Their existing source, authority, target-index records and evidence must remain unchanged unless a future task explicitly includes them.

## Critical hard truths

- The current Visual Control census and generated Target Index are reused. `DISCOVERY_ONLY` means **physically discovered but not application-authorized**. It does not mean unknown, unmapped or permission to recensus.
- Surface workers produce **candidate-only shards**. They do not write global Identity recipes, global element bindings, generated Target Index records, projection-manifest authority, Factory Ledger or `FILES_MANIFEST.json`.
- Atlasfin is the priority visual reference. A missing or ambiguous Atlasfin match stays missing or ambiguous.
- The Surface Visual Governor Materiality Catalog is **STANDBY / USER-INVOKED-ONLY**. There is no automatic fallback to it.
- Unknown stays unknown. Candidate is not authority. Discovery is not binding. Binding is not authorization. Authorization is not mutation. Mutation is not runtime certification.
- Every cross-authority ID reference must identify its authority domain. Never join two systems merely because their raw ID strings look alike.

## Six parallel chats

The only defined lanes are:

- Chat 1: Tablet Promotion
- Chat 2: PC Promotion
- Chat 3: Mobile Promotion
- Chat 4: Shared UI Promotion
- Chat 5: Atlasfin Bridge
- Chat 6: Visual Promotion Control Plane

All six lanes are designed to start independently from repository authority. None may require another lane to finish before beginning its own work.

## Shared status / blocker channel

All six chats publish progress, findings and blockers through `status-channel/`.

The static contract lives here, while writable mailboxes live at:

`apps/terminal-de-venta-system/docs/ops/visual-promotion-parallel-status/`

This split prevents routine status edits from invalidating the global `prisma-html/FILES_MANIFEST.json`. Each Chat has exactly one mailbox and one deterministic status branch, so authorship is unambiguous without conversational memory.


## Integration rule

Parallel workers must have disjoint write ownership. Global canonical registries are assembled only by deterministic integration after worker outputs exist. Workers may record their exact `baseHead`; mixed-base output is never silently merged. If inputs drift, the integration layer must revalidate or block.

The exact terms, ID rules, field names, statuses, relationship vocabulary, write ownership and anti-collision rules are normative in the interoperability contract and vocabulary registry in this folder.
