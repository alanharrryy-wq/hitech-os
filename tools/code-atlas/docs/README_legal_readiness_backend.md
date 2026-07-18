# Code Atlas Legal / Investor Readiness backend

This backend coordinates legal-evidence collectors sequentially.

## Execution model

- external stages: one at a time;
- active stage: controlled internal workers and shards;
- artifact matching: before/after snapshot, expected prefix, ZIP manifest and SHA-256;
- coordinator result: one ZIP containing references and hashes, not nested stage ZIPs.

## Profiles

- `plan`: authority and stage planning only;
- `static`: CTX static/source/database metadata;
- `full`: static followed by Mamastrophic legal runtime;
- `runtime-only`: Mamastrophic legal runtime only.

## Future UI

`qt_controller.py` exposes signals for the next `legui1` package. This package does not add a button or alter the existing Motor Hub UI.

## Non-claims

This backend does not certify legal compliance, IP ownership, OSS obligations, privacy compliance or production readiness.
