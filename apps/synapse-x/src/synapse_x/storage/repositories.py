from pathlib import Path

from synapse_x.storage import connect, init_db


def recent_sessions(db_path: str | Path, *, limit: int = 20) -> list[dict]:
    path = Path(db_path)
    init_db(path)
    conn = connect(path)
    try:
        rows = conn.execute(
            """
            SELECT session_id, first_seen_at, last_seen_at, source_count, status
            FROM sessions
            ORDER BY last_seen_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
