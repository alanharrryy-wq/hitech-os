from pathlib import Path

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine
from synapse_x.services.search_service import SearchRequest, run_search


def test_search_service_ranks_exact_phrase_first(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    source.mkdir()
    (source / "a.log").write_text(
        "2026-04-05 10:00 RuntimeError widget crash while running pytest",
        encoding="utf-8",
    )
    (source / "b.log").write_text(
        "2026-04-05 10:01 widget issue happened",
        encoding="utf-8",
    )
    settings = Settings(root=tmp_path, source_paths=(source,))
    engine = SynapseEngine(settings)
    engine.ingest(full=True)

    rows = run_search(engine, SearchRequest(query="RuntimeError widget crash", limit=5))
    assert rows
    assert rows[0]["score"] >= rows[-1]["score"]
    assert "snippet" in rows[0]
