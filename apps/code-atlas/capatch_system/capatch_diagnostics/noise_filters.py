from __future__ import annotations

"""Canonical noise-filter surface for diagnostics runtime."""

from pathlib import Path

from .session import DiagnosticSession


def mark_session_noise(session: DiagnosticSession, *, base_dir: Path, target_path: Path) -> DiagnosticSession:
    # Intentional no-op baseline: dedicated module keeps ownership canonical.
    return session


__all__ = ['mark_session_noise']
