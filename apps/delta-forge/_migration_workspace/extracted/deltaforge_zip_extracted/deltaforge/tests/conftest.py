from __future__ import annotations

import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    # Keep imports stable when pytest is launched from repo root.
    sys.path.insert(0, str(APP_ROOT))
