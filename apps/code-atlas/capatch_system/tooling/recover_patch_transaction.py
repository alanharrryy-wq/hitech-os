#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from pathlib import Path

from capatch_engine.transaction import list_recoverable_transactions, load_transaction


def main() -> int:
    parser = argparse.ArgumentParser(description='List recoverable CAPATCH patch transactions')
    parser.add_argument('--root-dir', required=True)
    parser.add_argument('--transaction-id', default=None)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    root = Path(args.root_dir).expanduser().resolve()
    if args.transaction_id:
        record = load_transaction(root, transaction_id=args.transaction_id)
        rows = [record.to_dict()] if record is not None else []
    else:
        rows = list_recoverable_transactions(root)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if not rows:
        print('no recoverable transactions found')
        return 0
    for item in rows:
        print(f"- {item.get('transaction_id')} phase={item.get('phase')} status={item.get('transaction_status')} updated={item.get('updated_at')}")
        hint = item.get('recovery_hint')
        if hint:
            print(f"  hint: {hint}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
