from __future__ import annotations

from pathlib import Path
from typing import Any

from .certification_handoffs import (
    assert_final_aggregation_invariants,
    enrich_global_result_with_handoffs,
    load_certification_registry,
    verify_all_certification_handoffs,
)
from .corpus_certification import (
    assert_completion_invariants,
    certify_registered_corpus,
    load_registry,
)


def build_final_aggregation(
    repo_root: Path,
    *,
    raw_registry_path: Path,
    certification_registry_path: Path,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    raw_registry = load_registry(raw_registry_path)
    independent = certify_registered_corpus(
        repo_root, registry=raw_registry
    )
    assert_completion_invariants(independent)
    certification_registry = load_certification_registry(
        certification_registry_path
    )
    verification = verify_all_certification_handoffs(
        repo_root,
        certification_registry,
        independent_result=independent,
    )
    result = enrich_global_result_with_handoffs(
        independent, verification
    )
    assert_final_aggregation_invariants(result)
    return result
