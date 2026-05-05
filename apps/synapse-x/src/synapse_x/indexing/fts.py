from pathlib import Path

from synapse_x.storage import connect, has_fts, init_db


def fts_enabled(db_path: str | Path) -> bool:
    path = Path(db_path)
    init_db(path)
    conn = connect(path)
    try:
        return has_fts(conn)
    finally:
        conn.close()
