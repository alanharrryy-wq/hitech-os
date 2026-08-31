from __future__ import annotations

import json
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from code_atlas.core.runtime_context import RuntimeContext

from .authority import AuthorityRequest, discover_authorities, semantic_retrieve
from .common import sha256_file
from .edge_provenance import normalize_system_graph_edge_provenance
from .graphs import build_system_graphs
from .impact_enrichment import enrich_change_impact
from .index import build_derived_index
from .repository import discover_repository
from .snapshot import build_snapshot


@dataclass(frozen=True)
class IntelligenceRequest:
    intent: str = "DISCOVER"
    domain: str = ""
    required_authorities: tuple[str, ...] = ()
    required_directories: tuple[str, ...] = ()
    excluded_authorities: tuple[str, ...] = ()
    changed_paths: tuple[str, ...] = ()
    semantic_query: str = ""
    fail_on_missing_authority: bool = True
    workers: int = 18


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _zip_tree(source: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as bundle:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(source).as_posix())


def resolve_intelligence_context(
    repo_root: str | Path | None = None,
    output_root: str | Path | None = None,
    *,
    profile_path: str | Path | None = None,
    request: IntelligenceRequest | None = None,
) -> dict[str, Any]:
    """Resolve the canonical neutral intelligence context without packaging it.

    This is the structured consumer API for higher layers such as Change
    Assurance. It owns no customer/product semantics and performs no source
    mutation. The returned SQLite/search projections remain non-authoritative.
    """
    request = request or IntelligenceRequest()
    context = RuntimeContext.resolve(repo_root, output_root, output_root, profile_path=profile_path)
    repo = context.repo_root
    profile = context.profile

    inventory = discover_repository(repo, workers=request.workers)
    authority_request = AuthorityRequest(
        required_authorities=request.required_authorities,
        required_directories=request.required_directories,
        excluded_authorities=request.excluded_authorities,
        intent=request.intent,
        domain=request.domain,
        fail_on_missing=request.fail_on_missing_authority,
    )
    authorities = discover_authorities(
        repo, inventory, request=authority_request, profile_metadata=profile.metadata,
    )
    raw_graphs = build_system_graphs(repo, inventory, authorities, changed_paths=list(request.changed_paths))
    graphs = normalize_system_graph_edge_provenance(raw_graphs, authorities)
    graphs = enrich_change_impact(
        repo,
        inventory,
        graphs,
        changed_paths=request.changed_paths,
        semantic_query=request.semantic_query,
    )
    profile_version = profile.metadata.get("profileVersion") if isinstance(profile.metadata, dict) else None
    snapshot = build_snapshot(
        repo,
        inventory,
        authorities,
        profile_id=profile.profile_id,
        profile_version=str(profile_version) if profile_version is not None else None,
        request_digest=authorities["requestDigest"],
    )
    retrieval = semantic_retrieve(request.semantic_query, authorities) if request.semantic_query else None
    coverage = {
        "physical": inventory.get("physicalCoverage"),
        "semantic": inventory.get("semanticCoverage"),
        "authorityRequirements": authorities.get("coverage"),
        "unclassifiedArchitectureFiles": sum(
            1 for row in graphs["architectureLayerGraph"]["nodes"] if row["layer"] == "unclassified"
        ),
    }
    return {
        "schemaVersion": "code_atlas_intelligence_context.v1",
        "repoRoot": str(repo),
        "outputRoot": str(context.output_root),
        "profile": {
            "id": profile.profile_id,
            "version": str(profile_version) if profile_version is not None else None,
        },
        "inventory": inventory,
        "authorities": authorities,
        "graphs": graphs,
        "snapshot": snapshot,
        "retrieval": retrieval,
        "coverage": coverage,
        "readOnly": True,
        "derivedIndexAuthoritative": False,
        "semanticRetrievalIsProof": False,
        "profileMayInventTruth": False,
        "productionCertified": False,
    }


def run_intelligence(
    repo_root: str | Path | None = None,
    output_root: str | Path | None = None,
    *,
    profile_path: str | Path | None = None,
    request: IntelligenceRequest | None = None,
) -> dict[str, Any]:
    resolved = resolve_intelligence_context(
        repo_root,
        output_root,
        profile_path=profile_path,
        request=request,
    )
    inventory = resolved["inventory"]
    authorities = resolved["authorities"]
    graphs = resolved["graphs"]
    snapshot = resolved["snapshot"]
    retrieval = resolved["retrieval"]
    coverage = resolved["coverage"]
    out = Path(resolved["outputRoot"])
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="code-atlas-intelligence-") as tmp:
        stage = Path(tmp) / "intelligence"
        stage.mkdir()
        _write(stage / "repository_inventory.json", inventory)
        _write(stage / "authority_discovery.json", authorities)
        _write(stage / "system_graphs.json", graphs)
        _write(stage / "portable_snapshot.json", snapshot)
        if retrieval is not None:
            _write(stage / "semantic_retrieval.json", retrieval)
        index_path = stage / "query_index.sqlite"
        build_derived_index(index_path, inventory, authorities, graphs, snapshot)
        _write(stage / "coverage.json", coverage)
        manifest = {
            "schemaVersion": "code_atlas_universal_intelligence_bundle.v1",
            "status": "PASS_UNIVERSAL_INTELLIGENCE_SOURCE_READY",
            "repoHead": inventory.get("identity", {}).get("head"),
            "repoTree": inventory.get("identity", {}).get("tree"),
            "profileId": resolved["profile"]["id"],
            "requestDigest": authorities.get("requestDigest"),
            "snapshotDigest": snapshot.get("snapshotDigest"),
            "readOnly": True,
            "derivedIndexAuthoritative": False,
            "semanticRetrievalIsProof": False,
            "profileMayInventTruth": False,
            "productionCertified": False,
        }
        _write(stage / "manifest.json", manifest)
        files = []
        for path in sorted(stage.iterdir()):
            if path.is_file():
                files.append({"path": path.name, "sha256": sha256_file(path), "bytes": path.stat().st_size})
        manifest["files"] = files
        _write(stage / "manifest.json", manifest)
        final = out / "code-atlas-intelligence-result.zip"
        if final.exists():
            final.unlink()
        _zip_tree(stage, final)
    return {
        **manifest,
        "artifact": str(final),
        "artifactSha256": sha256_file(final),
        "coverage": coverage,
        "authorityStates": authorities.get("states"),
    }
