# 72_POST_INSTALL_VERIFICATION_MODEL

The post-install verifier checks three layers:

## Layer 1: package-to-repo copy results
- required docs exist in `docs/live-scene-composer`
- staging root exists under `tools/live-scene-composer`
- summary artifacts exist in downloads

## Layer 2: optional mirror results
- composer source root was uniquely found, ambiguous, or missing
- mirror status is explicit
- required mirrored files are checked only when mirror was requested and possible

## Layer 3: optional environment checks
- architecture guard invocation
- smoke checks
- toolchain probes when available

The verifier should emit both text and JSON so operator and future tooling can read the same result.
