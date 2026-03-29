# 108_PACKAGE_OWNERSHIP_AND_DELETE_RULES

This package uses ownership rules to decide what may be deleted.

Owned by v3 cleanup-safe package:
- staging root contents under tools/live-scene-composer/end-to-end-mutation-ui-wiring-v3-cleanup-safe
- optional canonical docs 106-112 if explicitly installed there
- summary directory under Downloads for this package

Delete rules:
- cleanup mode may remove owned staging content
- cleanup mode may remove owned canonical docs 106-112 if they were installed
- cleanup mode may remove legacy v1/v2 UI wiring docs 90-105 from canonical docs root
- cleanup mode may remove legacy v1/v2 UI wiring staging roots
- cleanup mode must leave canonical architecture docs untouched

Why this matters:
The product architecture expects local cleanup and controlled replacement, not repo-wide teardown.
