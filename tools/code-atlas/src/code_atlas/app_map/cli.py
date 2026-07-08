from __future__ import annotations
import argparse
from .runner import run_app_map

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Generate read-only App Map atlas')
    parser.add_argument('path')
    parser.add_argument('--target-app', default='all')
    parser.add_argument('--output-root', default=None)
    args = parser.parse_args(argv)
    print(run_app_map(args.path, target_app=args.target_app, output_root=args.output_root))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
