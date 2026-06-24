# PRISMA Cloud SaaS Integration Report

## Scope

Target editable:

`prisma-control-center-unified-shell-lab-v3`

Read-only source:

`prisma-control-center`

Cloud API target:

`https://app.hitechrts.com`

## Implemented

- Added `PRISMA Cloud` as a native module inside the existing unified shell.
- Added a `Cloud SaaS` side tab and a `Licencias` side tab without replacing the shell layout.
- Added server-side Cloud SaaS bridge under `/api/cloud-saas/*`.
- Added read-only license ops adapter under `/api/license-ops/*`, based on the 3150 license module behavior.
- Added native JS/CSS cockpit views for Cloud SaaS, Licencias, Tenants, Devices, Snapshots, Notes, Receipts, Health and Commercial.
- Kept admin token handling server-side only.
- Changed launcher behavior so opening the lab does not kill an existing `3160` process.

## Not Modified

- Production Control Center `3150`.
- Cloudflare Tunnel.
- DNS.
- `app.hitechrts.com` Worker or D1.
- Tablet, PC, Mobile, Chart Lab, EIT or engine.
- Live processes or ports.

## Validation

Run syntax and smoke evidence are recorded in the `cclabcloud1` result package generated in `F:/descargasf`.
