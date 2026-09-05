# Chat 2 — PC Visual Promotion Candidate Shard

Base head: `57b01ad8bda043ec25763203354b686341bace09`

## Result

- Input PC census targets: **827**
- Candidate records: **186**
- Unresolved records: **640**
- Conflict records: **1**
- Output records: **827**
- Zero-loss accounting: **PASS**

## Physical truth

- `CURRENT`: 826
- `DRIFT`: 1
- `MISSING`: 0
- Existing route IDs resolved without rediscovery: 78
- Existing component IDs resolved without rediscovery: 107
- Existing CSS owner IDs resolved: 746

The one physical conflict is kept blocked rather than rediscovered or repaired:
- `TGT.CENSUS.PC.097AB2F857F353CA4288.V1`: Target Index selector `.supplier-readable-v07` vs expanded Visual Control selector `.supplier-readable-v07 *`.

## Atlasfin-first

- `MATCHED_RECIPE`: 186
- `NO_MATCH`: 641
- Atlasfin PC adapter reused: `atlasfin::ADP.PC.ADMIN.V2`
- Match promotion uses exact machine-classified `layerType == familyKind` with exactly one Atlasfin recipe for that kind.
- No Atlasfin family or preset was guessed.
- Atlasfin recipe IDs were **not** copied into canonical Identity recipe fields.

The Surface Visual Governor Materiality Catalog remained **STANDBY_USER_INVOKED_ONLY**. It was not inspected, consumed or used as fallback.

## NDC / Identity / binding

- NDC meaning: `UNRESOLVED` for 827 targets. No NDC ID was minted from selector names.
- Canonical Identity PC adapter reused: `identity::prisma.adapter.pc.v1`.
- Existing resolved PC element bindings found in the canonical Identity binding registry: **0**.
- Canonical PC-specific Identity recipes proven by the current recipe registry: **0**.
- `bindingStatus=BLOCKED`: 827
- New canonical `BND.*`, `TGT.*`, `LYR.*`, `VIS.*`, NDC IDs or Identity recipes minted: **0**.

## Projection classification

- `CURRENT`: 688
- `MISSING`: 139
- `DRIFT`: 0
- `NOT_REQUIRED`: 0
- `UNRESOLVED`: 0

The 139 `MISSING` rows are only the current Target Index records with null canonical source/output **and** an explicit `projection` blocker. This lane did not invent a source, copy bytes into RIFAT, or repair projection state.

## Boundaries held

- Broad rediscovery: **not run**
- Product/runtime mutation: **none**
- Global Identity/RIFAT/Target Index/projection-manifest mutation: **none**
- Factory Ledger / evidence index mutation: **none**
- Web / Chart Lab / Control Center / Tablet / Mobile / Shared UI candidate writes: **none**
- Materiality fallback: **none**
- Output ownership: only `prisma-html/governance/visual-promotion/candidates/pc/**`

`DISCOVERY_ONLY` was treated as current physical census evidence, never as undiscovered. Candidate remains candidate, not authority.
