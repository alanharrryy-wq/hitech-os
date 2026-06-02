# CODEX PROMPT DELTA: PRISMO HUB

Before editing PRISMO, read:

- `internal/prismo/00_index/PRISMO_INDEX.md`
- `internal/prismo/00_index/PRISMO_FILE_MAP.json`
- `internal/prismo/00_index/PRISMO_RUNTIME_LAYERS.md`
- `internal/prismo/07_memory/MEMORY_TYPES.md`
- `internal/prismo/09_codex/CODEX_PROMPT_DELTA_PRISMO_HUB.md`

Use `internal/prismo` as trace hub and source map.

Do not treat `internal/prismo` as the production runtime root unless imports, launchers, references, verifiers, and docs are all intentionally updated.

Runtime source-of-truth remains wherever `PRISMO_FILE_MAP.json` says it is, especially:

- `internal/py/prismo_learning/`
- `internal/py/prismo_ai_bridge.py`
- `internal/py/prismo_context.py`
- `internal/py/prismo_render_contracts.py`
- `internal/config/prismo_*.json`
- `internal/web/prismo_*.js`
- `internal/web/prisma_cc_v*prismo*.js/css`

Final architecture:

- 3 dependent dropdowns;
- free text primary interaction;
- dynamic chips;
- Auto Render Ensemble;
- Theater Query adapter;
- contract-based render blocks;
- procedural memory visible as recommendation rationale;
- evidence/protocol/memory in polished UI;
- technical drawer;
- feedback loop;
- Cloudglass/Refrigerant visual layer.

Hard bans:

- no fourth scene dropdown;
- no `intent.scene`;
- no Playwright;
- no screenshots requirement;
- no visible `safe mode`, `preview only`, `coming soon`, `future`, `experimental`;
- no raw HTML/script/iframe rendering;
- no opaque glass downgrade;
- no DB writes;
- no `.env` reads;
- no deploy;
- no git push.

Visual requirement:

Audit CSS layers, z-index, opacity, blur, pointer events, portals, drawers, dropdowns, command palette, toasts, pseudo-elements, and overlays by source-level checks. Nothing decorative may cover text or block clicks.

Run:

`python internal/prismo/08_verifiers/verify_prismo_hub.py`

and keep semantic fix2 verifier checks alive if present.
