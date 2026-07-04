# Prisma Cloud Ctr Security

## Secret Policy

Prisma Cloud Ctr may detect that an admin token file exists. It may read the token value only inside the local backend LICFLOW4 bridge immediately before a confirmed server-side outbound admin call. It must never expose the token value.

Allowed UI shape:

```json
{ "adminTokenPresent": true }
```

Forbidden:

- Token value in frontend JavaScript.
- Token value in diagnostics.
- Token value in logs.
- Token value in JSON config.
- Token value in SQLite.
- Token value in evidence ZIPs.
- Copying the local admin token file.
- Copying the local secret-only folder.

## LICFLOW4 Admin Bridge

Frontend JavaScript can know only sanitized bridge state:

- `bridgeAvailable`
- `adminTokenPresent`
- `actionAllowed`
- sanitized result code/status/request id
- sanitized audit summary

The frontend must not receive token value, token length, token prefix/suffix, raw request headers, secret file path, Cloudflare account details, D1 dumps, or production database contents.

Backend mutating routes:

- `POST /api/licflow4/bridge/activate`
- `POST /api/licflow4/bridge/refresh`
- `POST /api/licflow4/bridge/revoke`

All require `confirmAdminLicenseAction: true`. Revoke also requires `confirmRevoke: "REVOKE_LICENSE"`.

## Mutating Actions

The following are admin/mutating and must only run through LICFLOW4 Admin Bridge:

- activate
- refresh if it modifies server state
- revoke
- create license
- update tenant
- register device
- receipt smoke if it writes

## Cloud Safety

This folder must not deploy Cloudflare, change DNS, change Tunnel state, or run D1 dump/export/copy/execute.

## Diagnostics Safety

Diagnostics are sanitized and should contain only status, route metadata, health summaries, file presence, and redacted payloads.

Diagnostics may include LICFLOW4 bridge status, route map, config metadata, validation summary, and sanitized audit summary. Diagnostics must not include token values, token file contents, raw secret paths, request headers, D1 exports, DB copies, or Cloudflare deploy output.

## Local Server Safety

The local server binds to `127.0.0.1`. It does not kill processes or free ports.
