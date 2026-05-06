"""Homologation decisions that remove legacy divergence."""

from __future__ import annotations

DIVERGENCES_REMOVED = [
    "legacy mixed top-level payload layout replaced with one canonical root directory",
    "installer no longer requires external payload zip argument",
    "install root normalized to <root>/bundles/switch_engine_bundle",
    "state root normalized to <root>/.ark_install/switch_engine_bundle",
    "rollback file normalized to <root>/.ark_install/switch_engine_bundle/last_apply.json",
    "backup root normalized to <root>/.ark_install/switch_engine_bundle/backups/<timestamp>/",
    "log basename normalized to Ar-k_switch_engine_int_YYMMDD_HHMM.log",
    "canonical portable index renamed to registry_index.json with Python shim for query_index.json",
    "bundle composition shifted to Python-first assets so non-directory entries are overwhelmingly .py",
]


def summarize_homologation() -> list[str]:
    return list(DIVERGENCES_REMOVED)
