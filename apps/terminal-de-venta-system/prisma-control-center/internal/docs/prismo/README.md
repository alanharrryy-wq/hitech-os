# PRISMO · Gemini Command Nexus

PRISMO v1 is the read-only intelligence console inside PRISMA Control Center.

Runtime shape:

- UI: `internal/web/prismo_console.*` plus `prismo_renderers.js`
- API: `GET /api/prismo/status`
- API: `POST /api/prismo/query`
- Backend bridge: `internal/py/prismo_ai_bridge.py`
- Safety firewall: `internal/py/prismo_safety.py`
- Providers: `GeminiLiveProvider` and deterministic demo fallback

Security contract:

- Gemini is backend-only.
- The server reads the API key only from the process environment variable named `GEMINI_API_KEY`.
- No frontend file contains the key name or a key value.
- PRISMO v1 never executes commands, mutates DBs, commits, pushes, deploys, seeds, clears, or installs dependencies.
- HTML preview is off by default through `PRISMO_AI_ALLOW_HTML_PREVIEW=false`.
- Unknown render blocks are replaced with a safe blocked card.

Verification:

```powershell
pnpm -C <REPO_ROOT>\apps\terminal-de-venta-system run prismo:verify
```

Reports are written to `<OUTPUT_DIR>`.
