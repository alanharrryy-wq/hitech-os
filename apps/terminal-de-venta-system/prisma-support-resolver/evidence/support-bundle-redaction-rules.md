# Support Bundle Redaction Rules

Bloquear y redactar:

- valores de tokens;
- headers Authorization;
- private keys;
- `.env` reales;
- dumps D1 o DB completas;
- secretos Cloudflare;
- admin token;
- material de firma privado.

Permitir:

- nombres de variables;
- fingerprints truncados;
- rutas sanitizadas;
- codigos de error;
- summaries humanos;
- `secretsExposed:false`.
