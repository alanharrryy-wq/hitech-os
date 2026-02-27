# Add Workers

1. Add worker ID in `contracts_registry.json`.
2. Update defaults in `factory_config.json`.
3. Add scope rules in `file_ownership_rules.json`.
4. Regenerate templates if needed.
5. Validate contracts and run smoke.
6. Canonicalize runs root junctions:
   `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/scripts/Invoke-HitechRunsEnsure.ps1 --write`
7. Verify doctor returns `rc=0`:
   `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/scripts/Invoke-HitechRunsDoctor.ps1`
