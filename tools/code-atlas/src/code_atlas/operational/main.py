from __future__ import annotations
import argparse
from pathlib import Path
from .suite50 import run_operational_evidence

def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description='Run Operational Evidence Atlas 50 src-only readiness scan.')
    p.add_argument('--project-root',default='.')
    p.add_argument('--out',default='reports/operational_evidence')
    p.add_argument('--max-sample-rows',type=int,default=5)
    p.add_argument('--strict-production',action='store_true')
    p.add_argument('--no-placeholders',action='store_true')
    a=p.parse_args(argv)
    r=run_operational_evidence(Path(a.project_root),Path(a.out),max_sample_rows=max(0,int(a.max_sample_rows)),strict_production=bool(a.strict_production),include_placeholders=not bool(a.no_placeholders))
    print(f"Operational Evidence Atlas 50: {r.get('production_readiness')} -> {r.get('output_dir')}")
    print(f"features={r.get('feature_count')} placeholders={r.get('placeholder_count')} monolith_touched={r.get('monolith_touched')}")
    return 0
if __name__=='__main__': raise SystemExit(main())
