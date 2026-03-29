
# Round Protocol

## Required inputs
- active run manifest
- round manifest
- project baseline under `ops/projects/<project_id>/`
- active path policies
- governance freeze state
- acceptance rubric

## Required outputs per package
- bundle zip
- `bundle_manifest.json`
- `package_report.json`
- `notes/summary.md`
- `payload/**`

## Round states
- `planned`
- `in_progress`
- `submitted`
- `validated`
- `accepted`
- `rejected`
- `integrated`
- `closed`

## Critical rule
One package never corrects another package directly. Governance or delegated mission control issues directed retry prompts when correction is required.

## Artifact flow
1. governance freezes the round inputs
2. governance generates one packet per package
3. governance generates prompts from packets
4. workers submit bundles to `incoming/`
5. mission control validates bundles
6. mission control emits overlap and acceptance reports
7. mission control generates retry prompts only from the acceptance result
