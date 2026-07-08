
from __future__ import annotations
import argparse, json
from .runner import run_tablet_map

def main(argv=None):
    ap = argparse.ArgumentParser(prog='code-atlas-tablet-map')
    ap.add_argument('--repo', default='.')
    ap.add_argument('--out', required=True)
    ns = ap.parse_args(argv)
    print(json.dumps(run_tablet_map(ns.repo, ns.out), ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
