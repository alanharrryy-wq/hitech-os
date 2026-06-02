# PRISMO · Adaptive Intelligence Theater

PRISMO Theater is the local intelligence console inside PRISMA Control Center. It keeps free text as the primary interaction, uses exactly three optional guidance dropdowns, and lets the adapter infer missing intent/area/lens values as editable chips.

Runtime shape:

- UI entry: `/prismo` or `http://127.0.0.1:3150/prismo`
- UI: `internal/web/index.html`, `prismo_console.*`, `prismo_renderers.js`, `prismo_ai_theater.*`
- API: `GET /api/prismo/status`
- API: `POST /api/prismo/theater/query`
- Legacy API retained: `POST /api/prismo/query`
- Backend bridge: `internal/py/prismo_ai_bridge.py`
- Safety firewall: `internal/py/prismo_safety.py`
- Learning Core: `internal/py/prismo_learning/*`
- Providers: `GeminiLiveProvider` and deterministic fallback

Interaction contract:

- The composer has one free-text question box.
- Optional guidance has exactly three dropdowns: `intent`, `area`, `lens`.
- Missing guidance is inferred and shown as editable chips.
- Theater Query returns `interpretation`, `render_plan`, `blocks`, `memory_used`, `response_memory_chain`, `technical_trace`, and `feedback`.
- The memory chain order is `question -> interpretation -> protocol -> evidence -> result -> feedback`.
- Auto Render Ensemble chooses render blocks automatically. There is no manual scene/format/output selector.
- Feedback uses `/api/prismo/learning/feedback` from the dock when the operator clicks a feedback action.

Security and visual contract:

- Gemini is backend-only.
- The server reads the API key only from the process environment variable named `GEMINI_API_KEY`.
- PRISMO Theater never executes commands, mutates DBs, commits, pushes, deploys, seeds, clears, or installs dependencies.
- Theater integration does not read `.env` files.
- Raw HTML/script/iframe render paths are not part of the renderer contract.
- Unknown render blocks are replaced with a safe blocked card.
- Cloudglass/Refrigerant transparency tokens stay explicit: panel alpha, border alpha, z-index layers, reduced motion, and portal layer variables are kept in CSS.
- The Task 2 pass deliberately avoids Playwright, browser automation, screenshots, deploy, DB writes, and git push.

Verification:

```powershell
pnpm -C <REPO_ROOT>\apps\terminal-de-venta-system run prismo:verify
python <REPO_ROOT>\apps\terminal-de-venta-system\prisma-control-center\internal\prismo\08_verifiers\verify_prismo_theater_task2.py
```

`prismo:verify` writes reports to `apps\terminal-de-venta-system\tools\_local\evidence\prismo` unless `PRISMO_VERIFY_OUT_DIR` is set.
