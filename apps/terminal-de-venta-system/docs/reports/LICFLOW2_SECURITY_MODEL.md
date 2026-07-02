# LICFLOW2 Security Model

Generated: 2026-07-02

## Secrets Boundary

- Private key remains outside repo at `F:\PRISMA_CTX\LICENSING\issuers\adlant4-local\private-key.pem`.
- Activation packages never include `.pem`, `.env`, DB files, cookies, tokens, or private keys.
- Public key metadata and public-key registry are safe to inspect.
- Result ZIP must include reports/evidence only, not runtime DBs or private key material.

## Signing Boundary

- LICFLOW2 reuses ADLANT4 signing.
- Allowed issuer key id: `adlant4_local_2026_0630`.
- Signature algorithm: `Ed25519`.
- Signed license is verified by `verifySignedLicenseEnvelope` before package evidence is accepted.

## Activation Package Boundary

Safe package files:

- `activation-package.json`
- `activation-receipt.json`
- `license.signed.json`
- `roles/*/runtime.json`
- `roles/*/device-identity.json`
- `README.md`

Forbidden package files:

- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `.env*`
- `*.pem`
- `*.pfx`
- `*.p12`
- private-key files
- logs with secrets

## Online Boundary

`ONLINE_ACTIVATION` is implemented as a local service contract:

- Endpoint label: `POST /licenses/activate`
- Hosted cloud claim: `false`
- Result: signed local license and receipt

Hosted cloud activation must remain `UNRESOLVED` until a real hosted endpoint, credentials policy, deployment evidence, and verifier exist.

## Demo Boundary

Customer truth is `PRISMA_ORIGINAL_CUSTOMER`. LICFLOW2 does not use demo customer/business IDs as productive truth and does not downgrade customer activation to `DEVELOPMENT`.
