# 106_CLEANUP_SAFE_INSTALL_MODEL

This package installs the end-to-end mutation UI wiring wave in a cleanup-safe way.

Principles:
- one main script owns install, verify, cleanup, and report
- package docs default to staging only
- canonical docs remain protected unless explicitly opted in
- legacy wave clutter is removed by owned filename and owned staging root only
- cleanup writes evidence instead of silently deleting paths

Default install behavior:
1. validate repo and downloads roots
2. create summary directory
3. remove legacy wave staging roots for end-to-end mutation UI wiring v1 and v2 fixed
4. remove legacy wave docs 90-105 from canonical docs root if present
5. stage the package under tools/live-scene-composer/end-to-end-mutation-ui-wiring-v3-cleanup-safe
6. keep package docs in staging by default
7. write install and verify reports into Downloads
