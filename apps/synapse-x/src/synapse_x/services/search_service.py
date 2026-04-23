from __future__ import annotations

from dataclasses import dataclass

from synapse_x.engine import SynapseEngine


@dataclass(slots=True)
class SearchRequest:
    query: str
    record_type: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    limit: int = 50


def run_search(engine: SynapseEngine, request: SearchRequest) -> list[dict]:
    return engine.search(
        request.query,
        record_type=request.record_type,
        date_from=request.date_from,
        date_to=request.date_to,
        limit=request.limit,
    )
