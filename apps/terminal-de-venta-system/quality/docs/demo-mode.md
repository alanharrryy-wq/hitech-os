# Demo Mode Safety

Customer demos must be useful without contaminating real customer operation.

Rules:

- Demo/training data stays isolated.
- Demo reset must never target a real DB.
- Demo sync must not call production endpoints.
- Demo output must not leak internal paths, secrets, tokens, or raw customer data.
- Demo must not generate production folios unless the operator explicitly chooses that mode.

Run:

```powershell
node quality/bin/prisma-quality.mjs --profile demo --repo-root . --out-dir F:\descargasf
```
