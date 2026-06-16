#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from capatch_audit.bootstrap_baseline import bootstrap_readiness_baseline
print(json.dumps(bootstrap_readiness_baseline(ROOT),indent=2,ensure_ascii=False))
