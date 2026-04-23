
"""Checks around canonical index naming and the legacy shim."""

from __future__ import annotations

from core.index_compat import canonical_index_name


class IndexShimError(ValueError):
    """Raised when legacy index compatibility is misused."""


LEGACY_ALLOWED_CONTEXTS = {"reader_compat", "import_compat"}


def assert_index_shim_context(requested_name: str, context: str) -> None:
    canonical = canonical_index_name(requested_name)
    if requested_name == 'query_index.json' and context not in LEGACY_ALLOWED_CONTEXTS:
        raise IndexShimError('query_index.json may only be used at explicit compatibility boundaries')
    if canonical != 'registry_index.json':
        raise IndexShimError('Canonical index name mismatch')
