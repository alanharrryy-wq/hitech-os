# Code Atlas Neutrality Policy

Code Atlas core must remain environment-neutral.

## Allowed in core

- Relative paths resolved from an explicit project root.
- Values loaded from `CODE_ATLAS_PROFILE`, `CODE_ATLAS_PROJECT_ROOT`, `CODE_ATLAS_OUTPUT_ROOT`, or a caller-provided profile.
- Generic app/profile abstractions.

## Not allowed in core

- Machine-specific paths such as a developer home or fixed drive root.
- Project-specific repo paths.
- Fixed local ports or domains as universal defaults.
- PRISMA-specific assumptions outside `profiles/prisma.example.json` or external local profiles.

## Migration rule

Do not sanitize source code by blind string replacement. Classify first, migrate to profile/env, then verify with the neutrality gate.
