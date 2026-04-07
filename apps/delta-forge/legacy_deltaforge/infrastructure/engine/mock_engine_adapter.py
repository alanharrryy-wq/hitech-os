from __future__ import annotations

from infrastructure.adapters.mock_engine import MockEngineAdapter as _LegacyMockEngineAdapter


class MockEngineAdapter(_LegacyMockEngineAdapter):
    """Fallback mock engine for tests and explicit non-production runs."""

    is_fallback = True


__all__ = ["MockEngineAdapter"]
