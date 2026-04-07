
from __future__ import annotations

import sys
from pathlib import Path

# The entrypoint is at .synapse_hidden/entrypoints/run_ui_real.py
# We need to go up 3 levels to get to the project root (apps/synapse-x/)
ENTRYPOINT = Path(__file__).resolve()
PROJECT_ROOT = ENTRYPOINT.parent.parent.parent  # -> apps/synapse-x/
SRC = PROJECT_ROOT / "src"

# Add both src and project root to path so imports work
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from synapse_x.ui.app import main


if __name__ == "__main__":
    raise SystemExit(main())
