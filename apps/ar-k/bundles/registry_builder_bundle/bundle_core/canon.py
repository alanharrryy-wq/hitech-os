from __future__ import annotations

"""Shared canon constants for the homologated registry builder bundle."""

from payload_manifest import (
    BACKUPS_REL,
    BUILDER_LOCAL_OUTPUTS,
    CANONICAL_OUTPUTS,
    CANONICAL_PORTABLE_INDEX_NAME,
    DEFAULT_INSTALL_REL,
    DEFAULT_LOG_DIR,
    EXCLUSION_PATH_MARKERS,
    FORBIDDEN_WRITES,
    LEGACY_INDEX_NAME,
    ROLLBACK_STATE_REL,
    STAGE_ORDER,
    STATE_REL,
    STATUS_READY,
    WRITER_OWNERSHIP,
)

SHARED_REPORT_SECTIONS = [
    "1. STATUS",
    "2. ASSUMPTIONS",
    "3. SYSTEM MAP",
    "4. FILES INCLUDED",
    "5. HOMOLOGATION DECISIONS",
    "6. TOOL CONTRACT",
    "7. WRITE LIMITS",
    "8. PYTHON MIX PROOF",
    "9. ZIP SIZE PROOF",
    "10. VALIDATION RESULTS",
    "11. RISKS",
    "12. NEXT STEPS",
]
