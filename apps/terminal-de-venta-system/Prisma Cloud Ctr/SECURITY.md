# Prisma Cloud Center Security

## Secret Policy

Prisma Cloud Center may detect that an admin token file exists. It may read the token value only inside the local backend License Admin Bridge immediately before a confirmed server-side outbound admin call. It must never expose the token value.

Allowed UI shape:

```json
{ "adminTokenPresent": true, "tokenMode": "presence-only" }
```

Forbidden:

- Token value in frontend JavaScript.
- Token value, length, prefix, suffix, or secret path in diagnostics.
- Token value in logs, JSON config, SQLite, docs, screenshots, reports, or evidence ZIPs.
- Copying the local admin token file.
- Copying the local secret-only folder.

## License Admin Bridge

Frontend JavaScript can know only sanitized bridge state:

- `displayName: License Admin Bridge`
- `bridgeAvailable`
- `adminTokenPresent`
- `tokenMode: presence-only`
- `mutationMode`
- sanitized result code/status/request id
- `operatorMessage`
- `nextStep`
- sanitized License Operation Audit summary

The frontend must not receive token value, token length, token prefix/suffix, raw request headers, secret file path, Cloudflare account details, D1 dumps, or production database contents.

Backend confirmed-operation routes:

- `POST /api/licflow4/bridge/activate`
- `POST /api/licflow4/bridge/refresh`
- `POST /api/licflow4/bridge/revoke`

Simulation validates fields and never requires the admin token. Confirmed activate and refresh require `confirmAdminLicenseAction: true`. Confirmed revoke also requires `confirmRevoke: "REVOKE_LICENSE"` and `reason`.

## Confirmed License Operations

The following are admin operations and must only run through the License Admin Bridge:

- activate
- refresh if it modifies server state
- revoke

Device registration, customer setup, receipt writes, tenant updates, and license creation are separate flows and must not be hidden inside a confirmed license operation.

## Customer Setup Safety

Prisma Customer Setup is customer onboarding. Setup Link, Setup Code, Setup QR, and Device Claim never use or ask for `ADMIN_TOKEN`.

The customer-safe Cloud License Gateway endpoints require Setup Code, not admin token:

- `GET /api/customer/setup/:setupCode`
- `POST /api/customer/devices/claim`
- `GET /api/customer/license/status?setupCode=...&deviceId=...`

## Cloud Safety

This folder must not deploy Cloudflare, change DNS, change Tunnel state, or run D1 dump/export/copy/execute.

## Diagnostics Safety

License Diagnostics may include License Admin Bridge status, License Route Map, config metadata, validation summary, and sanitized License Operation Audit summary. Diagnostics must not include token values, token file contents, raw secret paths, request headers, D1 exports, DB copies, or Cloudflare deploy output.

## Local Server Safety

The local server binds to `127.0.0.1`. It does not kill processes or free ports.
