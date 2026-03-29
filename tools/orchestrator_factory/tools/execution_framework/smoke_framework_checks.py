
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from pathlib import Path
from lib.common import discover_repo_root
from lib.readiness import build_readiness_report


def main() -> int:
    repo_root = discover_repo_root(Path(__file__).resolve())
    report = build_readiness_report(repo_root)
    install = report['stages']['install']
    if install['status'] == 'ready':
        print('[OK] Framework install readiness is ready.')
        return 0
    print('[WARN] Framework install readiness is not ready:')
    for item in install['checks']:
        if not item['ok']:
            print(f" - {item['name']}: {item['details']}")
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
