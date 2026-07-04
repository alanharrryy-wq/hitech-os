# Prisma Cloud Center Security

## Secret Policy

Prisma Cloud Center may detect that an admin token file exists, but it must never read or expose the token value.

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

## Mutating Actions

The following are admin/mutating and blocked until LICFLOW4 Admin Bridge:

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

## Local Server Safety

The local server binds to `127.0.0.1`. It does not kill processes or free ports.
