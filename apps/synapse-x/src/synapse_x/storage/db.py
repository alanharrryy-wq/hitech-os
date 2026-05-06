from pathlib import Path

from synapse_x.storage import connect as _connect
from synapse_x.storage import init_db as _init_db


def connect(db_path: str | Path):
    return _connect(Path(db_path))


def init_db(db_path: str | Path) -> None:
    _init_db(Path(db_path))
