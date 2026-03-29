#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
repo_map_build.py (stdlib-only)
Builds .repo_map/repo_map.sqlite + helper CSVs from a folder/repo.
Fast enough, deterministic, with real progress (2-pass count + ingest).
"""

from __future__ import annotations
import argparse, csv, fnmatch, hashlib, json, os, platform, sqlite3, sys, time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

DEFAULT_IGNORE_DIRS = {
    ".git",".hg",".svn",
    "node_modules","dist","build",".next",".turbo",".cache",
    ".pytest_cache",".mypy_cache",".venv","venv","__pycache__",
    ".idea",".vscode","coverage",".pnpm-store"
}
DEFAULT_IGNORE_GLOBS = ["*.log","*.tmp","*.temp","*.bak","*.swp","*.swo","*.dmp"]
BATCH_SIZE = 5000

SQL_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;

CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rel_path TEXT NOT NULL,
  dir_rel TEXT NOT NULL,
  name TEXT NOT NULL,
  ext TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  mtime_epoch INTEGER NOT NULL,
  mtime_iso TEXT NOT NULL,
  is_symlink INTEGER NOT NULL,
  depth INTEGER NOT NULL,
  sha1 TEXT
);

CREATE TABLE IF NOT EXISTS ext_stats (
  ext TEXT PRIMARY KEY,
  file_count INTEGER NOT NULL,
  total_size_bytes INTEGER NOT NULL,
  avg_size_bytes REAL NOT NULL,
  min_size_bytes INTEGER NOT NULL,
  max_size_bytes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dir_stats (
  dir_rel TEXT PRIMARY KEY,
  file_count INTEGER NOT NULL,
  total_size_bytes INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_files_ext ON files(ext);
CREATE INDEX IF NOT EXISTS idx_files_dir ON files(dir_rel);
CREATE INDEX IF NOT EXISTS idx_files_size ON files(size_bytes);
CREATE INDEX IF NOT EXISTS idx_files_mtime ON files(mtime_epoch);
CREATE INDEX IF NOT EXISTS idx_files_name ON files(name);

CREATE VIEW IF NOT EXISTS v_ext_summary AS
SELECT
  ext,
  file_count,
  total_size_bytes,
  ROUND(total_size_bytes / 1048576.0, 2) AS total_size_mb,
  ROUND(avg_size_bytes / 1024.0, 2) AS avg_size_kb,
  min_size_bytes,
  max_size_bytes
FROM ext_stats
ORDER BY total_size_bytes DESC;
"""

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def is_windows() -> bool:
    return platform.system().lower().startswith("win")

def safe_relpath(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root)).replace("\\", "/")
    except Exception:
        return os.path.relpath(str(p), str(root)).replace("\\", "/")

def should_ignore_dir(name: str, ignore_dirs: set[str], include_hidden: bool) -> bool:
    if not include_hidden and name.startswith(".") and name not in {".",".."}:
        return True
    return name in ignore_dirs

def should_ignore_file(name: str, ignore_globs: List[str], include_hidden: bool) -> bool:
    if not include_hidden and name.startswith("."):
        return True
    for pat in ignore_globs:
        if fnmatch.fnmatch(name, pat):
            return True
    return False

def sha1_file(path: Path, max_bytes: Optional[int] = None) -> str:
    h = hashlib.sha1()
    remaining = max_bytes
    with path.open("rb") as f:
        while True:
            chunk_size = 1024 * 1024
            if remaining is not None:
                if remaining <= 0:
                    break
                chunk_size = min(chunk_size, remaining)
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
            if remaining is not None:
                remaining -= len(b)
    return h.hexdigest()

def print_progress(prefix: str, done: int, total: int, start_ts: float) -> None:
    total = max(total, 1)
    pct = (done / total) * 100.0
    elapsed = max(time.time() - start_ts, 0.001)
    rate = done / elapsed
    sys.stdout.write(f"\r{prefix} {pct:6.2f}%  ({done:,}/{total:,})  {rate:,.0f} items/s")
    sys.stdout.flush()

def newline():
    sys.stdout.write("\n"); sys.stdout.flush()

@dataclass
class ScanConfig:
    root: Path
    out_dir: Path
    db_path: Path
    export_csv: bool
    csv_files: Path
    csv_ext: Path
    csv_dir: Path
    ignore_dirs: set[str]
    ignore_globs: List[str]
    include_hidden: bool
    follow_symlinks: bool
    hash_mode: str
    hash_head_bytes: int
    open_out_dir: bool

def count_files(cfg: ScanConfig) -> Tuple[int,int]:
    dir_count = 0
    file_count = 0
    for cur, dirs, files in os.walk(cfg.root, followlinks=cfg.follow_symlinks):
        kept = []
        for d in dirs:
            if should_ignore_dir(d, cfg.ignore_dirs, cfg.include_hidden): continue
            kept.append(d)
        dirs[:] = kept
        dir_count += 1
        for f in files:
            if should_ignore_file(f, cfg.ignore_globs, cfg.include_hidden): continue
            file_count += 1
    return dir_count, file_count

def iter_files(cfg: ScanConfig) -> Iterable[Path]:
    for cur, dirs, files in os.walk(cfg.root, followlinks=cfg.follow_symlinks):
        kept = []
        for d in dirs:
            if should_ignore_dir(d, cfg.ignore_dirs, cfg.include_hidden): continue
            kept.append(d)
        dirs[:] = kept
        curp = Path(cur)
        for f in files:
            if should_ignore_file(f, cfg.ignore_globs, cfg.include_hidden): continue
            yield curp / f

def build(cfg: ScanConfig) -> None:
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[repo-map] Root: {cfg.root}")
    print(f"[repo-map] Out : {cfg.out_dir}")

    print("[repo-map] Counting…")
    t0 = time.time()
    dir_count, file_count = count_files(cfg)
    newline()
    print(f"[repo-map] dirs={dir_count:,} files={file_count:,} counted in {time.time()-t0:.2f}s")

    if cfg.db_path.exists():
        cfg.db_path.unlink(missing_ok=True)

    con = sqlite3.connect(str(cfg.db_path))
    con.executescript(SQL_SCHEMA)

    meta = {
        "generated_ts_utc": now_utc_iso(),
        "python_version": sys.version.replace("\n"," "),
        "platform": platform.platform(),
        "root": str(cfg.root),
        "files_counted": str(file_count),
        "dirs_counted": str(dir_count),
        "include_hidden": str(cfg.include_hidden),
        "follow_symlinks": str(cfg.follow_symlinks),
        "hash_mode": cfg.hash_mode,
        "hash_head_bytes": str(cfg.hash_head_bytes),
        "ignore_dirs": json.dumps(sorted(cfg.ignore_dirs)),
        "ignore_globs": json.dumps(cfg.ignore_globs),
    }
    con.executemany("INSERT OR REPLACE INTO meta(k,v) VALUES(?,?)", list(meta.items()))
    con.commit()

    ext_acc: Dict[str, List[int]] = {}  # ext -> [count,total,min,max]
    dir_acc: Dict[str, List[int]] = {}  # dir_rel -> [count,total]
    errors: List[str] = []

    print("[repo-map] Ingest → SQLite…")
    start_ts = time.time()
    done = 0
    batch = []

    def flush():
        nonlocal batch
        if not batch: return
        con.executemany(
            "INSERT INTO files(rel_path,dir_rel,name,ext,size_bytes,mtime_epoch,mtime_iso,is_symlink,depth,sha1) VALUES(?,?,?,?,?,?,?,?,?,?)",
            batch
        )
        batch = []

    con.execute("BEGIN;")
    try:
        for p in iter_files(cfg):
            done += 1
            if done % 250 == 0 or done == file_count:
                print_progress("[repo-map] Ingest", done, file_count, start_ts)

            try:
                st = p.lstat()
                is_symlink = 1 if p.is_symlink() else 0
                size_bytes = int(st.st_size)
                mtime_epoch = int(st.st_mtime)
                mtime_iso = datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
            except Exception as e:
                errors.append(f"STAT_FAIL: {p} :: {e}")
                continue

            rel_path = safe_relpath(p, cfg.root)
            dir_rel = rel_path.rsplit("/",1)[0] if "/" in rel_path else ""
            name = p.name
            ext = (p.suffix or "").lower()
            depth = rel_path.count("/")

            sha1_val = None
            if cfg.hash_mode != "none" and not is_symlink:
                try:
                    if cfg.hash_mode == "head":
                        sha1_val = sha1_file(p, max_bytes=cfg.hash_head_bytes)
                    elif cfg.hash_mode == "full":
                        sha1_val = sha1_file(p, max_bytes=None)
                except Exception as e:
                    errors.append(f"HASH_FAIL: {p} :: {e}")

            batch.append((rel_path,dir_rel,name,ext,size_bytes,mtime_epoch,mtime_iso,is_symlink,depth,sha1_val))

            if ext not in ext_acc:
                ext_acc[ext] = [0,0,size_bytes,size_bytes]
            ext_acc[ext][0] += 1
            ext_acc[ext][1] += size_bytes
            ext_acc[ext][2] = min(ext_acc[ext][2], size_bytes)
            ext_acc[ext][3] = max(ext_acc[ext][3], size_bytes)

            if dir_rel not in dir_acc:
                dir_acc[dir_rel] = [0,0]
            dir_acc[dir_rel][0] += 1
            dir_acc[dir_rel][1] += size_bytes

            if len(batch) >= BATCH_SIZE:
                flush()

        flush()
        con.execute("COMMIT;")
        newline()
    except KeyboardInterrupt:
        newline()
        print("[repo-map] Interrupted. Committing partial results…")
        try: con.execute("COMMIT;")
        except Exception: pass
    except Exception:
        newline()
        try: con.execute("ROLLBACK;")
        except Exception: pass
        raise

    print("[repo-map] Stats tables…")
    con.execute("BEGIN;")
    con.execute("DELETE FROM ext_stats;")
    con.execute("DELETE FROM dir_stats;")

    ext_rows = []
    for ext,(cnt,total,mn,mx) in ext_acc.items():
        avg = float(total)/float(cnt) if cnt else 0.0
        ext_rows.append((ext,cnt,total,avg,mn,mx))
    con.executemany("INSERT INTO ext_stats(ext,file_count,total_size_bytes,avg_size_bytes,min_size_bytes,max_size_bytes) VALUES(?,?,?,?,?,?)", ext_rows)

    dir_rows = [(d,v[0],v[1]) for d,v in dir_acc.items()]
    con.executemany("INSERT INTO dir_stats(dir_rel,file_count,total_size_bytes) VALUES(?,?,?)", dir_rows)

    con.execute("INSERT OR REPLACE INTO meta(k,v) VALUES(?,?)", ("files_indexed", str(done)))
    con.execute("INSERT OR REPLACE INTO meta(k,v) VALUES(?,?)", ("errors_count", str(len(errors))))
    con.execute("COMMIT;")
    con.execute("ANALYZE;")
    con.commit()

    # Exports
    if cfg.export_csv:
        print("[repo-map] Export CSVs…")
        with cfg.csv_files.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["rel_path","dir_rel","name","ext","size_bytes","mtime_iso","mtime_epoch","is_symlink","depth","sha1"])
            for row in con.execute("SELECT rel_path,dir_rel,name,ext,size_bytes,mtime_iso,mtime_epoch,is_symlink,depth,sha1 FROM files ORDER BY dir_rel,name"):
                w.writerow(row)

        with cfg.csv_ext.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ext","file_count","total_size_bytes","total_size_mb","avg_size_kb","min_size_bytes","max_size_bytes"])
            for row in con.execute("SELECT ext,file_count,total_size_bytes,total_size_mb,avg_size_kb,min_size_bytes,max_size_bytes FROM v_ext_summary"):
                w.writerow(row)

        with cfg.csv_dir.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["dir_rel","file_count","total_size_bytes","total_size_mb"])
            for row in con.execute("SELECT dir_rel,file_count,total_size_bytes, ROUND(total_size_bytes/1048576.0,2) FROM dir_stats ORDER BY total_size_bytes DESC"):
                w.writerow(row)

    # Errors log
    if errors:
        (cfg.out_dir/"repo_map_errors.log").write_text("\n".join(errors[:5000]), encoding="utf-8")

    # Query helper
    (cfg.out_dir/"QUERIES.sql").write_text("\n".join([
        "-- Top extensions by total size",
        "SELECT * FROM v_ext_summary LIMIT 50;",
        "",
        "-- Biggest files",
        "SELECT rel_path, size_bytes, ROUND(size_bytes/1048576.0,2) AS mb, mtime_iso FROM files ORDER BY size_bytes DESC LIMIT 50;",
        "",
        "-- Example: TSX under keystone",
        "SELECT rel_path, size_bytes FROM files WHERE ext='.tsx' AND rel_path LIKE '%apps/keystone%' ORDER BY size_bytes DESC LIMIT 200;",
        "",
        "-- Directory size leaderboard",
        "SELECT dir_rel, file_count, ROUND(total_size_bytes/1048576.0,2) AS total_mb FROM dir_stats ORDER BY total_size_bytes DESC LIMIT 100;",
        "",
        "-- If sha1 enabled: real duplicates",
        "SELECT sha1, COUNT(*) c, MIN(size_bytes) size_bytes FROM files WHERE sha1 IS NOT NULL GROUP BY sha1 HAVING c>1 ORDER BY c DESC LIMIT 100;"
    ]), encoding="utf-8")

    con.close()

    print("[repo-map] DONE ✅")
    print(f"[repo-map] DB: {cfg.db_path}")
    if cfg.export_csv:
        print(f"[repo-map] CSV: {cfg.csv_files}")
    if is_windows() and cfg.open_out_dir:
        try: os.startfile(str(cfg.out_dir))
        except Exception: pass

def parse_args(argv: List[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="", help="Root folder to scan")
    ap.add_argument("--out-dir", default="", help="Output folder (default: <root>/.repo_map)")
    ap.add_argument("--db-name", default="repo_map.sqlite")
    ap.add_argument("--include-hidden", action="store_true")
    ap.add_argument("--follow-symlinks", action="store_true")
    ap.add_argument("--no-csv", action="store_true")
    ap.add_argument("--hash", choices=["none","head","full"], default="none")
    ap.add_argument("--hash-head-bytes", type=int, default=1024*1024)
    ap.add_argument("--no-open", action="store_true")
    return ap.parse_args(argv)

def main(argv: List[str]) -> int:
    ns = parse_args(argv)
    root = Path(ns.root).resolve() if ns.root else Path.cwd().resolve()
    if not root.exists():
        print(f"[repo-map] root not found: {root}")
        return 2

    out_dir = Path(ns.out_dir).resolve() if ns.out_dir else (root/".repo_map")
    db_path = out_dir / ns.db_name

    cfg = ScanConfig(
        root=root,
        out_dir=out_dir,
        db_path=db_path,
        export_csv=(not ns.no_csv),
        csv_files=(out_dir/"repo_map_files.csv"),
        csv_ext=(out_dir/"repo_map_ext_stats.csv"),
        csv_dir=(out_dir/"repo_map_dir_stats.csv"),
        ignore_dirs=set(DEFAULT_IGNORE_DIRS),
        ignore_globs=list(DEFAULT_IGNORE_GLOBS),
        include_hidden=bool(ns.include_hidden),
        follow_symlinks=bool(ns.follow_symlinks),
        hash_mode=str(ns.hash),
        hash_head_bytes=int(ns.hash_head_bytes),
        open_out_dir=(not ns.no_open),
    )
    build(cfg)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
# %%
def run_jupyter(root=r"F:\repos\hitech-os"):
    return main([
        "--root", root,
        "--hash", "head",
        "--hash-head-bytes", "1048576",
    ])
