from __future__ import annotations

import argparse
import json
from pathlib import Path

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SYNAPSE-X backend engine CLI")
    parser.add_argument("--root", default=None, help="Project root for data directories and defaults")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Initialize SQLite storage")

    ingest = sub.add_parser("ingest", help="Run incremental ingest")
    ingest.add_argument("--path", action="append", default=[], help="Source path to scan, can be repeated")

    full = sub.add_parser("full-ingest", help="Run full ingest")
    full.add_argument("--path", action="append", default=[], help="Source path to scan, can be repeated")

    search = sub.add_parser("search", help="Search indexed content")
    search.add_argument("--query", required=True)
    search.add_argument("--type", dest="record_type", default=None)
    search.add_argument("--date-from", default=None)
    search.add_argument("--date-to", default=None)
    search.add_argument("--limit", type=int, default=20)

    detail = sub.add_parser("session-detail", help="Get session detail")
    detail.add_argument("--session-id", required=True)

    metrics = sub.add_parser("metrics", help="Get metrics")
    metrics.add_argument("--days", type=int, default=7)

    sub.add_parser("repair", help="Rebuild search index and run integrity check")
    return parser


def _make_engine(root: str | None) -> SynapseEngine:
    settings = Settings(root=Path(root).resolve()) if root else Settings()
    return SynapseEngine(settings=settings)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    engine = _make_engine(args.root)

    if args.command == "init-db":
        engine.init_storage()
        print("OK: database initialized")
        return 0

    if args.command == "ingest":
        result = engine.ingest(paths=args.path or None, full=False)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "full-ingest":
        result = engine.ingest(paths=args.path or None, full=True)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "search":
        result = engine.search(
            args.query,
            record_type=args.record_type,
            date_from=args.date_from,
            date_to=args.date_to,
            limit=args.limit,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "session-detail":
        result = engine.get_session_detail(args.session_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "metrics":
        result = engine.get_metrics(days=args.days)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "repair":
        result = engine.repair()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    parser.error("Unknown command")
    return 2
