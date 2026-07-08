# PRISMA Support Bundle Standard

El bundle de soporte se exporta sanitizado y orientado a continuidad.

## Incluir

- support case
- issues
- surface status
- customer summary
- device summary
- resolution plan
- dry-run/apply result cuando existan
- logs sanitizados
- redaction report
- continuation instructions

## Nunca incluir

- tokens
- `.env`
- private-key.pem
- Authorization headers
- raw D1 dump
- DB completa
- Cloudflare secrets
- admin token
- private license signing key

Siempre reportar `secretsExposed:false`.
