import hashlib
from pathlib import Path

STATE_FILE = "drift_state"

def hash_directory(path):
    sha = hashlib.sha256()
    for p in sorted(Path(path).rglob("*")):
        if p.is_file():
            sha.update(p.read_bytes())
    return sha.hexdigest()

def detect_drift(runtime_root, target_dir):
    state = Path(runtime_root) / STATE_FILE

    current = hash_directory(target_dir)

    if not state.exists():
        state.write_text(current)
        return False

    previous = state.read_text()

    if previous != current:
        state.write_text(current)
        return True

    return False
