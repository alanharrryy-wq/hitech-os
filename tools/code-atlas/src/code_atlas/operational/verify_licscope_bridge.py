# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from pathlib import Path
try:
    from .licscope_bridge import verify_bridge, json_dumps
except Exception:
    from licscope_bridge import verify_bridge, json_dumps

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    ap.add_argument('--dbevid-zip', default='')
    ns = ap.parse_args(argv)
    result = verify_bridge(Path(ns.repo_root), Path(ns.dbevid_zip) if ns.dbevid_zip else None)
    print(json_dumps(result))
    return 0 if result.get('ok') else 1

if __name__ == '__main__':
    raise SystemExit(main())
