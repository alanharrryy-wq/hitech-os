from synapse_x.engine import SynapseEngine


def search_rows(
    engine: SynapseEngine,
    query: str,
    *,
    record_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 50,
) -> list[dict]:
    return engine.search(
        query,
        record_type=record_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )
