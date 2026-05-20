import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
from collections import Counter
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path

REGISTRY_REL = Path("products/chart-lab/app/src/prisma-charts/chart-lab-registry.tsx")
RUNTIME_TS_REL = Path("products/chart-lab/app/src/prisma-charts/chart-runtime-data.ts")
SNAPSHOT_JSON_REL = Path("products/chart-lab/app/src/prisma-charts/prisma-chart-runtime.snapshot.json")
TOOL_REL = Path("tools/prisma/prisma_chart_runtime_snapshot.py")
NEXT_ENV_REL = Path("products/chart-lab/app/next-env.d.ts")
ROOT_PACKAGE_REL = Path("package.json")
CHART_LAB_PACKAGE_REL = Path("products/chart-lab/app/package.json")
DEFAULT_RUNTIME_DB_REL = Path("products/chart-lab/app/data/chart-runtime-governance.db")

ALLOWED_RELS = [REGISTRY_REL, RUNTIME_TS_REL, SNAPSHOT_JSON_REL, TOOL_REL, ROOT_PACKAGE_REL, CHART_LAB_PACKAGE_REL]
GENERATED_RELS = [NEXT_ENV_REL]

GATES = [
    ["pnpm", "--filter", "@hitech/prisma-chart-lab", "--fail-if-no-match", "typecheck"],
    ["pnpm", "--filter", "@hitech/prisma-chart-lab", "--fail-if-no-match", "build"],
    ["pnpm", "--filter", "@hitech/prisma-chart-lab", "--fail-if-no-match", "verify:controls"],
    ["pnpm", "--filter", "@hitech/prisma-chart-lab", "--fail-if-no-match", "verify:echarts-boundary"],
    ["pnpm", "--filter", "@hitech/prisma-chart-lab", "--fail-if-no-match", "verify"],
    ["pnpm", "--filter", "@hitech/prisma-chart-lab", "--fail-if-no-match", "verify:all"],
    ["pnpm", "run", "verify:no-direct-db-in-ui"],
]

FORBIDDEN_UI_TOKENS = [
    "localStorage",
    "sessionStorage",
    "indexedDB",
    "IndexedDB",
    "navigator.storage",
    "fetch(",
    "XMLHttpRequest"
]

RUNTIME_TS = r'''import runtimeSnapshotJson from "./prisma-chart-runtime.snapshot.json";
import { mockMobileCharts, mockPcCharts, mockTabletCharts } from "../../../../../shared/prisma-charts/prismaChartMocks";
import type {
  PrismaMobileChartsViewModel,
  PrismaPcChartsViewModel,
  PrismaTabletChartsViewModel,
  PrismaTripleAppChartsViewModel
} from "../../../../../shared/prisma-charts/prismaChartContracts";
import type { LabChartDataStatus } from "./chart-lab-types";

type RuntimeSnapshotMeta = {
  runtimeReady?: boolean;
  sourceMode?: string;
  dataStatus?: string;
  generatedAt?: string;
  databasePaths?: Record<string, string | null>;
  warnings?: string[];
  evidence?: string[];
  discovery?: Record<string, unknown>;
};

type RuntimeSnapshot = Partial<PrismaTripleAppChartsViewModel> & {
  meta?: RuntimeSnapshotMeta;
};

const runtimeSnapshot = runtimeSnapshotJson as unknown as RuntimeSnapshot;

function isRuntimeSourceMode(sourceMode: string | undefined) {
  return sourceMode === "sqlite-runtime";
}

function isLabRuntimeDataStatus(value: string | undefined): value is LabChartDataStatus {
  return value === "shared/mock"
    || value === "partial/adapter-ready"
    || value === "runtime"
    || value === "stale"
    || value === "invalid";
}

function hasUsableRuntimeSnapshot(snapshot: RuntimeSnapshot): snapshot is RuntimeSnapshot & {
  pc: Partial<PrismaPcChartsViewModel>;
  tablet: Partial<PrismaTabletChartsViewModel>;
  mobile: Partial<PrismaMobileChartsViewModel>;
} {
  return snapshot.schemaVersion === "1.0" && snapshot.meta?.runtimeReady === true && isRuntimeSourceMode(snapshot.meta?.sourceMode);
}

export const chartRuntimeSnapshotAvailable = hasUsableRuntimeSnapshot(runtimeSnapshot);
const hasRuntimeGovernanceSource = chartRuntimeSnapshotAvailable
  && Boolean(runtimeSnapshot.meta?.databasePaths?.pc || runtimeSnapshot.meta?.databasePaths?.canonical);

export const runtimePcCharts: PrismaPcChartsViewModel = chartRuntimeSnapshotAvailable
  ? ({ ...mockPcCharts, ...(runtimeSnapshot.pc ?? {}) } as PrismaPcChartsViewModel)
  : mockPcCharts;

export const runtimeTabletCharts: PrismaTabletChartsViewModel = chartRuntimeSnapshotAvailable
  ? ({ ...mockTabletCharts, ...(runtimeSnapshot.tablet ?? {}) } as PrismaTabletChartsViewModel)
  : mockTabletCharts;

export const runtimeMobileCharts: PrismaMobileChartsViewModel = chartRuntimeSnapshotAvailable
  ? ({ ...mockMobileCharts, ...(runtimeSnapshot.mobile ?? {}) } as PrismaMobileChartsViewModel)
  : mockMobileCharts;

const snapshotDataStatus = isLabRuntimeDataStatus(runtimeSnapshot.meta?.dataStatus)
  ? runtimeSnapshot.meta?.dataStatus
  : undefined;

export const chartRuntimeDataStatus: LabChartDataStatus = runtimeSnapshot.schemaVersion !== "1.0"
  ? "invalid"
  : chartRuntimeSnapshotAvailable
    ? snapshotDataStatus ?? (hasRuntimeGovernanceSource ? "runtime" : "partial/adapter-ready")
    : runtimeSnapshot.meta?.sourceMode === "mock-fallback"
      ? "shared/mock"
      : "invalid";

export const chartRuntimeFreshnessLabel = chartRuntimeDataStatus === "invalid"
  ? "Invalid Chart Lab runtime snapshot metadata; charts fall back to shared deterministic mocks and no browser DB access is used."
  : chartRuntimeSnapshotAvailable
    ? hasRuntimeGovernanceSource
      ? `SQLite runtime snapshot generated ${runtimeSnapshot.meta?.generatedAt ?? runtimeSnapshot.generatedAt ?? "unknown"} from read-only local DB sources; no browser DB access.`
      : `SQLite runtime snapshot generated ${runtimeSnapshot.meta?.generatedAt ?? runtimeSnapshot.generatedAt ?? "unknown"} from read-only Tablet SQLite; PC/canonical DB are optional and currently unknown, so PC/Mobile charts are partial adapter-ready derivatives; no browser DB access.`
    : "Shared deterministic mock; run tools/prisma/prisma_chart_runtime_snapshot.py --collect-only to refresh a local SQLite runtime snapshot.";
'''

SNAPSHOT_STUB = {
    "schemaVersion": "1.0",
    "generatedAt": None,
    "meta": {
        "runtimeReady": False,
        "sourceMode": "mock-fallback",
        "dataStatus": "shared/mock",
        "generatedAt": None,
        "databasePaths": {"tablet": None, "pc": None, "canonical": None},
        "warnings": ["No SQLite database snapshot has been generated yet."],
        "evidence": [],
        "discovery": {},
        "safety": {"readOnlySqlite": True, "browserDbAccess": False, "persistentBrowserStorage": False, "tabletStillStandalone": True, "pcOptional": True, "mobileSupervisionOnly": True}
    },
    "pc": {},
    "tablet": {},
    "mobile": {},
    "quality": {}
}

# ------------------------------------------------------------
# General utilities
# ------------------------------------------------------------

def iso_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def is_terminal_repo_root(path: Path) -> bool:
    package_path = path / "package.json"
    if not package_path.exists():
        return False
    try:
        return json.loads(read_text(package_path)).get("name") == "@hitech/terminal-de-venta-system"
    except Exception:
        return False


def resolve_repo_root(candidate: str) -> Path:
    repo = Path(candidate).resolve()
    if is_terminal_repo_root(repo):
        return repo
    fallback = Path(__file__).resolve().parents[2]
    if is_terminal_repo_root(fallback):
        return fallback
    raise RuntimeError(f"Repo root invalido: {repo}")


def sha_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def run_cmd(cmd, cwd: Path, timeout=1200):
    started = iso_now()
    try:
        env = os.environ.copy()
        env["CI"] = env.get("CI", "1")
        completed = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, shell=False, env=env)
        return {"cmd": cmd, "started_at": started, "finished_at": iso_now(), "exit_code": completed.returncode, "output_tail": (completed.stdout or "")[-24000:]}
    except FileNotFoundError as exc:
        return {"cmd": cmd, "started_at": started, "finished_at": iso_now(), "exit_code": 127, "output_tail": str(exc)}
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        if not isinstance(out, str):
            out = ""
        return {"cmd": cmd, "started_at": started, "finished_at": iso_now(), "exit_code": 124, "timeout": True, "output_tail": out[-24000:]}


def git_root_for(repo: Path) -> Path:
    result = run_cmd(["git", "-C", str(repo), "rev-parse", "--show-toplevel"], repo, timeout=120)
    if result["exit_code"] != 0:
        raise RuntimeError("No pude obtener git root: " + result["output_tail"])
    return Path(result["output_tail"].strip())


def git_name_for(path: Path, git_root: Path) -> str:
    return path.resolve().relative_to(git_root.resolve()).as_posix()


def diff_names(repo: Path):
    result = run_cmd(["git", "-C", str(repo), "diff", "--name-only"], repo, timeout=120)
    names = []
    if result["exit_code"] == 0:
        for line in result["output_tail"].splitlines():
            value = line.strip().replace("\\", "/")
            if value and not value.lower().startswith("warning:"):
                names.append(value)
    return names, result


def git_status_porcelain(repo: Path):
    result = run_cmd(["git", "-C", str(repo), "status", "--short", "--untracked-files=all"], repo, timeout=120)
    rows = []
    if result["exit_code"] == 0:
        for line in result["output_tail"].splitlines():
            if not line.strip():
                continue
            status = line[:2]
            path = line[3:].strip().replace("\\", "/") if len(line) > 3 else line.strip()
            rows.append({"status": status, "path": path})
    return rows, result


def full_diff(repo: Path, files):
    existing = [str(path) for path in files if path.exists()]
    if not existing:
        return ""
    completed = subprocess.run(["git", "-C", str(repo), "diff", "--", *existing], cwd=str(repo), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180, shell=False)
    return completed.stdout or ""


def write_untracked_bundle(repo: Path, git_root: Path, files, bundle_path: Path):
    payload = {}
    for path in files:
        if path.exists():
            payload[git_name_for(path, git_root)] = read_text(path)
    write_text(bundle_path, json.dumps(payload, ensure_ascii=False, indent=2))
    return sorted(payload.keys())


def backup_file(repo: Path, rel_path: Path, backup_root: Path, manifest: list):
    target = repo / rel_path
    backup = backup_root / rel_path
    backup.parent.mkdir(parents=True, exist_ok=True)
    entry = {"relative_path": rel_path.as_posix(), "target": str(target), "backup": str(backup), "existed": target.exists()}
    if target.exists():
        shutil.copy2(target, backup)
        entry["sha256_before"] = sha_file(target)
    manifest.append(entry)


def restore_one(repo: Path, entry: dict):
    target = repo / Path(entry["relative_path"])
    backup = Path(entry["backup"])
    if entry.get("existed"):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup, target)
    elif target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()


def rollback(repo: Path, manifest: list):
    for entry in reversed(manifest):
        restore_one(repo, entry)


def clamp(value, min_value=0, max_value=100):
    try:
        return max(min_value, min(max_value, int(round(float(value)))))
    except Exception:
        return min_value


def parse_dt(value):
    if not value:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value / 1000 if value > 100000000000 else value, timezone.utc)
        except Exception:
            return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
        parsed = datetime.fromisoformat(text.replace(" ", "T"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def as_iso(dt):
    if not dt:
        return iso_now()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

# ------------------------------------------------------------
# DB discovery
# ------------------------------------------------------------

def normalize_sqlite_path(raw):
    if not raw:
        return None
    value = str(raw).strip().strip('"').strip("'")
    if value.startswith("sqlite:"):
        value = value[len("sqlite:"):]
    if value.startswith("file:"):
        value = value[5:]
    if "?" in value:
        value = value.split("?", 1)[0]
    if value.startswith("./") or value.startswith("../"):
        return Path(value)
    if "://" in value and not value.lower().startswith("file:"):
        return None
    return Path(value) if value else None


def parse_env_file(path: Path):
    values = {}
    if not path.exists() or not path.is_file():
        return values
    try:
        for raw in read_text(path).splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                values[key] = value
    except Exception:
        return values
    return values


def env_db_path(name):
    return normalize_sqlite_path(os.environ.get(name))


def add_candidate(candidates, key, path, origin, repo=None):
    if not path:
        return
    p = Path(path)
    if repo and not p.is_absolute():
        p = repo / p
    candidates[key].append({"path": p, "origin": origin})


def discover_db_paths(repo: Path, explicit=None):
    explicit = explicit or {}
    candidates = {"tablet": [], "pc": [], "canonical": []}

    for key in ["tablet", "pc", "canonical"]:
        if explicit.get(key):
            add_candidate(candidates, key, normalize_sqlite_path(explicit[key]), f"cli:{key}", repo)

    env_map = {
        "tablet": ["PRISMA_CHART_TABLET_DATABASE", "PRISMA_TABLET_DATABASE", "PRISMA_CHART_TABLET_DATABASE_URL", "TABLET_DATABASE_URL"],
        "pc": ["PRISMA_CHART_PC_DATABASE", "PRISMA_PC_DATABASE", "PRISMA_CHART_PC_DATABASE_URL", "PC_DATABASE_URL"],
        "canonical": ["PRISMA_CHART_CANONICAL_DATABASE", "PRISMA_CANONICAL_DATABASE", "PRISMA_CHART_CANONICAL_DATABASE_URL", "DATABASE_URL"]
    }
    for key, env_names in env_map.items():
        for env_name in env_names:
            add_candidate(candidates, key, env_db_path(env_name), f"env:{env_name}", repo)

    env_files = [
        repo / ".env",
        repo / ".env.local",
        repo / "products/chart-lab/app/.env.local",
        repo / "products/tablet/app/.env",
        repo / "products/tablet/app/.env.local",
        repo / "products/pc/app/.env",
        repo / "products/pc/app/.env.local",
    ]
    for env_file in env_files:
        values = parse_env_file(env_file)
        for key, env_names in env_map.items():
            for env_name in env_names:
                if env_name in values:
                    add_candidate(candidates, key, normalize_sqlite_path(values[env_name]), f"envfile:{env_file.name}:{env_name}", env_file.parent)

    fixed = {
        "tablet": [
            repo / "products/tablet/app/data/tablet-pos.db",
            repo / "products/tablet/app/prisma/dev.db",
            repo / "products/tablet/app/prisma/prisma.db",
            repo / "products/tablet/app/dev.db",
            repo / "products/tablet/app/local.db"
        ],
        "pc": [
            repo / "products/pc/app/data/pc-governance.db",
            repo / "products/pc/app/data/pc.db",
            repo / "products/pc/app/prisma/dev.db",
            repo / "products/pc/app/prisma/prisma.db",
            repo / "products/pc/app/dev.db",
            repo / "products/pc/app/local.db"
        ],
        "canonical": [
            repo / "data/canonical.db",
            repo / "data/prisma-canonical.db",
            repo / "prisma/dev.db",
            repo / "prisma/prisma.db",
            repo / "dev.db",
            repo / "local.db"
        ]
    }
    for key, paths in fixed.items():
        for path in paths:
            add_candidate(candidates, key, path, "fixed")

    bounded_roots = [repo / "products/tablet/app", repo / "products/pc/app", repo / "prisma", repo / "data", repo / "tools/_local"]
    excluded = {"node_modules", ".next", "out", "dist", "build", ".git", "coverage", ".turbo"}
    found = []
    for root in bounded_roots:
        if not root.exists():
            continue
        for current, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in excluded]
            current_path = Path(current)
            for name in files:
                lower = name.lower()
                if lower.endswith((".db", ".sqlite", ".sqlite3")):
                    found.append(current_path / name)
            if len(found) > 120:
                break
    for path in found:
        low = str(path).lower().replace("\\", "/")
        low_match = "/" + low.lstrip("/")
        if "/products/tablet/" in low_match:
            add_candidate(candidates, "tablet", path, "bounded-scan")
        elif "/products/pc/" in low_match:
            add_candidate(candidates, "pc", path, "bounded-scan")
        elif "/prisma/" in low_match or "/data/" in low_match:
            add_candidate(candidates, "canonical", path, "bounded-scan")

    selected = {}
    discovery = {}
    for key, entries in candidates.items():
        seen = []
        normalized = []
        for entry in entries:
            try:
                resolved = entry["path"].resolve()
            except Exception:
                resolved = entry["path"]
            if resolved not in seen:
                seen.append(resolved)
                normalized.append({"path": resolved, "origin": entry["origin"], "exists": resolved.exists(), "bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else 0})
        chosen = next((item for item in normalized if item["exists"] and item["bytes"] > 0), None)
        selected[key] = chosen["path"] if chosen else None
        discovery[key] = [{"path": str(item["path"]), "origin": item["origin"], "exists": item["exists"], "bytes": item["bytes"]} for item in normalized[:30]]
    return selected, discovery


def connect_ro(path: Path):
    uri = f"file:{path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def resolve_runtime_db_path(repo: Path, runtime_db: str | None) -> Path:
    path = Path(runtime_db) if runtime_db else repo / DEFAULT_RUNTIME_DB_REL
    if not path.is_absolute():
        path = repo / path
    resolved = path.resolve()
    if not is_within(resolved, repo):
        raise RuntimeError(f"runtime DB must stay inside repo-controlled paths: {resolved}")
    if is_within(resolved, repo / "products/tablet"):
        raise RuntimeError(f"runtime DB cannot be placed inside Tablet product paths: {resolved}")
    return resolved


def runtime_db_status(path: Path) -> dict:
    return {
        "path": str(path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
        "mode": "optional-derived-read-model",
        "sourceOfTruth": False,
        "requiredForTabletSales": False,
        "openedByBrowser": False
    }


def derive_data_status(runtime_ready: bool, paths: dict) -> str:
    if not runtime_ready:
        return "shared/mock"
    if paths.get("pc") or paths.get("canonical"):
        return "runtime"
    return "partial/adapter-ready"


def table_exists(conn, table):
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
    return row is not None


def table_columns(conn, table):
    if not table_exists(conn, table):
        return set()
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")').fetchall()}


def count_table(conn, table, where="1=1"):
    if not table_exists(conn, table):
        return 0
    try:
        return int(conn.execute(f'SELECT COUNT(*) AS c FROM "{table}" WHERE {where}').fetchone()["c"] or 0)
    except Exception:
        return 0


def sum_table(conn, table, col, where="1=1"):
    if not table_exists(conn, table) or col not in table_columns(conn, table):
        return 0
    try:
        return int(conn.execute(f'SELECT COALESCE(SUM("{col}"), 0) AS c FROM "{table}" WHERE {where}').fetchone()["c"] or 0)
    except Exception:
        return 0


def rows(conn, query, params=()):
    try:
        return [dict(row) for row in conn.execute(query, params).fetchall()]
    except Exception:
        return []


def latest_sale_time(conn):
    if not table_exists(conn, "Sale"):
        return None
    row = conn.execute('SELECT MAX("createdAt") AS maxCreatedAt FROM "Sale"').fetchone()
    return parse_dt(row["maxCreatedAt"] if row else None)


def fetch_recent_sales(conn, hours=8, limit=5000):
    if not table_exists(conn, "Sale"):
        return []
    max_dt = latest_sale_time(conn) or datetime.now(timezone.utc)
    start_dt = max_dt - timedelta(hours=hours)
    return rows(conn, 'SELECT id, businessId, terminalId, cashSessionId, cashier, totalCents, status, createdAt FROM "Sale" WHERE datetime(createdAt) >= datetime(?) ORDER BY createdAt ASC LIMIT ?', (as_iso(start_dt), limit))


def bucket_start(dt, minutes=45):
    dt = dt.astimezone(timezone.utc).replace(second=0, microsecond=0)
    total_minutes = dt.hour * 60 + dt.minute
    bucket = (total_minutes // minutes) * minutes
    return dt.replace(hour=bucket // 60, minute=bucket % 60)


def build_shift_pulse(conn):
    sales = fetch_recent_sales(conn)
    if not sales:
        return []
    grouped = {}
    for sale in sales:
        dt = parse_dt(sale.get("createdAt")) or datetime.now(timezone.utc)
        start = bucket_start(dt)
        key = as_iso(start)
        item = grouped.setdefault(key, {"bucketStart": key, "bucketEnd": as_iso(start + timedelta(minutes=45)), "shiftId": sale.get("cashSessionId") or "current-shift", "terminalId": sale.get("terminalId") or "tablet-local", "cashierId": sale.get("cashier"), "saleCount": 0, "grossSales": 0, "refundCount": 0, "cancellationCount": 0, "avgTicket": 0, "offlineSaleCount": 0, "pendingSyncCount": 0, "queuePressure": 0, "status": "normal"})
        status = str(sale.get("status") or "").lower()
        if status in {"cancelled", "canceled", "void", "annulled"}:
            item["cancellationCount"] += 1
        else:
            item["saleCount"] += 1
            item["grossSales"] += int(sale.get("totalCents") or 0)
    pending_by_bucket = Counter()
    if table_exists(conn, "OutboxEvent"):
        for event in rows(conn, 'SELECT status, topic, eventType, createdAt FROM "OutboxEvent" ORDER BY createdAt ASC LIMIT 5000'):
            created = parse_dt(event.get("createdAt")) or datetime.now(timezone.utc)
            status = str(event.get("status") or "").lower()
            topic = str(event.get("topic") or event.get("eventType") or "").lower()
            if "sale" in topic and status not in {"sent", "accepted", "projected", "reconciled", "done", "ok", "success"}:
                pending_by_bucket[as_iso(bucket_start(created))] += 1
    for key, item in grouped.items():
        item["pendingSyncCount"] = pending_by_bucket.get(key, 0)
        item["offlineSaleCount"] = min(item["saleCount"], item["pendingSyncCount"])
        item["avgTicket"] = round(item["grossSales"] / item["saleCount"]) if item["saleCount"] else 0
        item["queuePressure"] = clamp(item["saleCount"] * 4 + item["pendingSyncCount"] * 8 + item["offlineSaleCount"] * 6)
        item["status"] = "blocked" if item["queuePressure"] >= 82 else "risk" if item["queuePressure"] >= 66 else "busy" if item["queuePressure"] >= 50 else "normal"
    return list(grouped.values())[-16:]


def map_sync_state(status):
    value = str(status or "pending").lower()
    if value in {"sent", "accepted", "projected", "reconciled", "done", "ok", "success"}:
        return "sent"
    if value in {"failed", "error", "dead_letter", "deadletter"}:
        return "failed"
    if value in {"sending", "processing", "in_progress"}:
        return "sending"
    if value in {"retry", "retrying"}:
        return "retrying"
    return "pending"


def map_item_type(topic):
    text = str(topic or "event").lower()
    if "sale" in text:
        return "sale"
    if "refund" in text or "return" in text:
        return "refund"
    if "inventory" in text or "stock" in text:
        return "inventory_adjustment"
    if "cash" in text or "session" in text:
        return "cash_shift"
    if "ticket" in text:
        return "ticket"
    if "customer" in text:
        return "customer"
    return "event"


def build_sync_matrix(conn):
    if not table_exists(conn, "OutboxEvent"):
        return []
    data = {}
    now = datetime.now(timezone.utc)
    for event in rows(conn, 'SELECT status, lifecycleStatus, topic, eventType, attempts, createdAt, sentAt, failedAt FROM "OutboxEvent" ORDER BY createdAt DESC LIMIT 5000'):
        state = map_sync_state(event.get("lifecycleStatus") or event.get("status"))
        item_type = map_item_type(event.get("topic") or event.get("eventType"))
        key = (item_type, state)
        created = parse_dt(event.get("createdAt")) or now
        item = data.setdefault(key, {"itemType": item_type, "syncState": state, "count": 0, "oldestAgeMinutes": 0, "lastAttemptAt": None, "retryCount": 0, "blocking": False, "confidence": 72})
        item["count"] += 1
        item["oldestAgeMinutes"] = max(item["oldestAgeMinutes"], int((now - created).total_seconds() // 60))
        item["retryCount"] += int(event.get("attempts") or 0)
        item["lastAttemptAt"] = event.get("failedAt") or event.get("sentAt") or event.get("createdAt") or item["lastAttemptAt"]
        item["blocking"] = item["blocking"] or state in {"failed", "retrying"} or item["oldestAgeMinutes"] > 60
    return list(data.values())[:32]


def build_inventory(conn):
    if not table_exists(conn, "Product"):
        return []
    products = rows(conn, 'SELECT id, sku, name, category, stockOnHand, costCents, priceCents, isActive, updatedAt FROM "Product" WHERE isActive = 1 LIMIT 500')
    root = {"id": "inventory-root", "label": "Inventario real SQLite", "level": "category", "stockOnHand": 0, "reorderPoint": 0, "daysOfCover": 7, "velocityPerDay": 0, "stockoutRisk": 0, "overstockRisk": 0, "revenueAtRisk": 0, "confidence": 72}
    nodes = [root]
    by_category = {}
    snapshots = {}
    if table_exists(conn, "StockSnapshot"):
        for row in rows(conn, 'SELECT productId, onHand, available, daysCover, snapshotAt FROM "StockSnapshot" ORDER BY snapshotAt DESC LIMIT 2000'):
            if row.get("productId") not in snapshots:
                snapshots[row.get("productId")] = row
    for product in products:
        pid = product.get("id")
        snap = snapshots.get(pid, {})
        stock = int(snap.get("available") if snap.get("available") is not None else product.get("stockOnHand") or 0)
        price = int(product.get("priceCents") or 0)
        days = float(snap.get("daysCover") if snap.get("daysCover") is not None else 7)
        risk = clamp((8 - min(days, 8)) * 11 + (12 - min(stock, 12)) * 3 if stock < 12 else max(0, 18 - days))
        category = product.get("category") or "General"
        category_id = "cat-" + re.sub(r"[^a-z0-9]+", "-", str(category).lower()).strip("-")
        cat = by_category.setdefault(category_id, {"id": category_id, "parentId": "inventory-root", "label": str(category), "level": "category", "stockOnHand": 0, "reorderPoint": 0, "daysOfCover": 7, "velocityPerDay": 0, "stockoutRisk": 0, "overstockRisk": 0, "revenueAtRisk": 0, "confidence": 70})
        cat["stockOnHand"] += stock
        cat["stockoutRisk"] = max(cat["stockoutRisk"], risk)
        cat["revenueAtRisk"] += price if risk > 50 else 0
        root["stockOnHand"] += stock
        root["stockoutRisk"] = max(root["stockoutRisk"], risk)
        root["revenueAtRisk"] += price if risk > 50 else 0
        if risk >= 35:
            nodes.append({"id": "sku-" + str(product.get("sku") or pid), "parentId": category_id, "label": str(product.get("name") or product.get("sku") or pid), "level": "sku", "stockOnHand": stock, "reorderPoint": 8, "daysOfCover": days, "velocityPerDay": max(1, int((price or 1000) / 1000)), "stockoutRisk": risk, "overstockRisk": 10 if stock > 100 else 0, "revenueAtRisk": price if risk > 50 else 0, "lastMovementAt": product.get("updatedAt") or snap.get("snapshotAt"), "confidence": 68})
    nodes[1:1] = list(by_category.values())[:12]
    return nodes[:40]


def build_waterfall(conn):
    gross = sum_table(conn, "Sale", "totalCents", "LOWER(status) NOT IN ('cancelled','canceled','void')")
    refunds = sum_table(conn, "SaleReturnLine", "totalCents")
    cogs = 0
    if table_exists(conn, "SaleLine") and table_exists(conn, "Product"):
        for row in rows(conn, 'SELECT sl.qty AS qty, p.costCents AS costCents FROM "SaleLine" sl LEFT JOIN "Product" p ON p.id = sl.productId AND p.businessId = sl.businessId LIMIT 5000'):
            cogs += int(row.get("qty") or 0) * int(row.get("costCents") or 0)
    low_stock = sum(1 for node in build_inventory(conn) if node.get("level") == "sku" and node.get("stockoutRisk", 0) >= 50)
    risk = low_stock * 15000
    net = gross - refunds - cogs - risk
    return [
        {"id": "gross-sales", "label": "Ventas brutas", "kind": "positive", "value": gross, "currency": "MXN", "source": "sales", "relatedIds": ["Sale"], "confidence": 76},
        {"id": "refunds", "label": "Devoluciones", "kind": "negative", "value": refunds, "currency": "MXN", "source": "refunds", "relatedIds": ["SaleReturnLine"], "confidence": 60},
        {"id": "estimated-cogs", "label": "Costo estimado", "kind": "negative", "value": cogs, "currency": "MXN", "source": "costs", "relatedIds": ["SaleLine", "Product.costCents"], "confidence": 58},
        {"id": "inventory-risk", "label": "Riesgo inventario", "kind": "negative", "value": risk, "currency": "MXN", "source": "inventory", "relatedIds": ["StockSnapshot", "Product"], "confidence": 48},
        {"id": "net-visible", "label": "Neto visible", "kind": "subtotal", "value": net, "currency": "MXN", "source": "sales", "relatedIds": ["SQLite snapshot"], "confidence": 62}
    ]


def build_density(conn):
    now = latest_sale_time(conn) or datetime.now(timezone.utc)
    recent_sales = fetch_recent_sales(conn, hours=8)
    modules = ["sales", "sync", "inventory", "incidents"]
    cells = []
    outbox_events = rows(conn, 'SELECT status, createdAt FROM "OutboxEvent" ORDER BY createdAt DESC LIMIT 5000') if table_exists(conn, "OutboxEvent") else []
    inventory_nodes = build_inventory(conn)
    low_stock = sum(1 for node in inventory_nodes if node.get("level") == "sku" and node.get("stockoutRisk", 0) >= 50)
    incident_count = count_table(conn, "SupportIncident", "LOWER(status) NOT IN ('resolved','closed')")
    for index in range(8):
        start = now - timedelta(minutes=(8 - index) * 30)
        end = start + timedelta(minutes=30)
        sale_count = len([s for s in recent_sales if start <= (parse_dt(s.get("createdAt")) or now) < end])
        outbox_count = 0
        failed_count = 0
        for event in outbox_events:
            dt = parse_dt(event.get("createdAt")) or now
            if start <= dt < end:
                outbox_count += 1
                failed_count += 1 if map_sync_state(event.get("status")) == "failed" else 0
        values = {
            "sales": (sale_count, 0, 0, sale_count * 7, "sales_flow"),
            "sync": (outbox_count, outbox_count - failed_count, failed_count, outbox_count * 8 + failed_count * 16, "outbox"),
            "inventory": (low_stock, low_stock, 0, low_stock * 12, "stockout"),
            "incidents": (incident_count, incident_count, 0, incident_count * 20, "support")
        }
        for module in modules:
            event_count, warn, error, pressure, cause = values[module]
            cells.append({"bucketStart": as_iso(start), "bucketEnd": as_iso(end), "moduleId": module, "moduleName": module.title(), "eventCount": event_count, "warnCount": warn, "errorCount": error, "staleMinutesAvg": 0, "retryCount": warn, "pressureScore": clamp(pressure), "dominantCause": cause, "confidence": 65, "bucketLabel": start.strftime("%H:%M"), "state": "anomaly" if error else "peak" if pressure >= 60 else "normal", "evidenceRef": "sqlite-runtime-snapshot"})
    return cells


def build_causal(conn):
    pending = count_table(conn, "OutboxEvent", "LOWER(status) NOT IN ('sent','accepted','projected','reconciled','done','ok','success')")
    failed = count_table(conn, "OutboxEvent", "LOWER(status) IN ('failed','error','dead_letter','deadletter')")
    conflicts = count_table(conn, "SyncConflict", "LOWER(status) NOT IN ('resolved','closed')")
    low_stock = sum(1 for node in build_inventory(conn) if node.get("level") == "sku" and node.get("stockoutRisk", 0) >= 50)
    now = iso_now()
    rows_out = []
    if pending or failed or conflicts:
        rows_out.append({"sourceModule": "Sync", "causeType": "failed_events" if failed else "pending_events", "effectType": "governance_attention", "actionTarget": "Review ingest/outbox", "weight": max(1, pending + failed * 3 + conflicts * 4), "severity": "CRITICAL" if conflicts else "ERROR" if failed else "WARN", "confidence": 70, "evidenceCount": pending + failed + conflicts, "incidentIds": ["sqlite-sync"], "firstSeenAt": now, "lastSeenAt": now, "ownerRole": "Backoffice"})
    if low_stock:
        rows_out.append({"sourceModule": "Inventory", "causeType": "low_stock", "effectType": "continuity_risk", "actionTarget": "Replenishment review", "weight": max(1, low_stock), "severity": "ERROR" if low_stock > 5 else "WARN", "confidence": 64, "evidenceCount": low_stock, "incidentIds": ["sqlite-inventory"], "firstSeenAt": now, "lastSeenAt": now, "ownerRole": "Inventory"})
    if not rows_out:
        rows_out.append({"sourceModule": "SQLite", "causeType": "snapshot_ready", "effectType": "chart_runtime", "actionTarget": "Monitor", "weight": 1, "severity": "INFO", "confidence": 72, "evidenceCount": 1, "incidentIds": ["sqlite-runtime"], "firstSeenAt": now, "lastSeenAt": now, "ownerRole": "Control"})
    return rows_out


def build_service_graph(paths):
    now = iso_now()
    nodes = []
    edges = []
    def node(id_, label, kind, ok, owner):
        nodes.append({"id": id_, "label": label, "kind": kind, "status": "PASS" if ok else "UNKNOWN", "healthy": bool(ok), "criticality": "high" if kind == "db" else "medium", "owner": owner, "lastProbeAt": now})
    tablet_ok = bool(paths.get("tablet"))
    pc_ok = bool(paths.get("pc"))
    canonical_ok = bool(paths.get("canonical"))
    node("chart-lab", "Chart Lab", "app", True, "Lab")
    node("tablet-sqlite", "Tablet SQLite", "db", tablet_ok, "Tablet local")
    node("pc-sqlite", "PC SQLite", "db", pc_ok, "PC governance")
    node("canonical-sqlite", "Canonical SQLite", "db", canonical_ok, "Shared/Core")
    node("runtime-snapshot", "Runtime Snapshot", "worker", tablet_ok or pc_ok or canonical_ok, "Shared charts")
    edges.extend([
        {"source": "runtime-snapshot", "target": "tablet-sqlite", "relation": "probes", "status": "PASS" if tablet_ok else "UNKNOWN", "evidence": paths.get("tablet") or "not-found"},
        {"source": "runtime-snapshot", "target": "pc-sqlite", "relation": "probes", "status": "PASS" if pc_ok else "UNKNOWN", "evidence": paths.get("pc") or "not-found"},
        {"source": "runtime-snapshot", "target": "canonical-sqlite", "relation": "probes", "status": "PASS" if canonical_ok else "UNKNOWN", "evidence": paths.get("canonical") or "not-found"},
        {"source": "chart-lab", "target": "runtime-snapshot", "relation": "reads_snapshot", "status": "PASS" if tablet_ok or pc_ok or canonical_ok else "UNKNOWN", "evidence": "prisma-chart-runtime.snapshot.json"}
    ])
    return {"nodes": nodes, "edges": edges}


def build_decision(conn):
    out = []
    if table_exists(conn, "AuditEvent"):
        for row in rows(conn, 'SELECT id, topic, entityType, entityId, summary, createdAt FROM "AuditEvent" ORDER BY createdAt DESC LIMIT 12'):
            out.append({"decisionId": str(row.get("id")), "time": row.get("createdAt") or iso_now(), "title": row.get("summary") or row.get("topic") or "Audit event", "type": "evidence", "actorName": "Audit", "responsibleRole": "Control", "status": "resolved", "relatedIncidentIds": [str(row.get("entityId") or row.get("id"))], "evidenceCount": 1, "impactScore": 35, "confidence": 68})
    if table_exists(conn, "SupportIncident"):
        for row in rows(conn, 'SELECT id, title, status, severity, createdAt, resolvedAt FROM "SupportIncident" ORDER BY createdAt DESC LIMIT 12'):
            severity = str(row.get("severity") or "normal").lower()
            out.append({"decisionId": str(row.get("id")), "time": row.get("createdAt") or iso_now(), "title": row.get("title") or "Support incident", "type": "incident", "actorName": "Support", "responsibleRole": "Operations", "status": "resolved" if row.get("resolvedAt") else "open", "relatedIncidentIds": [str(row.get("id"))], "evidenceCount": 1, "impactScore": 82 if severity in {"critical", "high"} else 55, "confidence": 64})
    if not out:
        out.append({"decisionId": "sqlite-runtime-connected", "time": iso_now(), "title": "SQLite runtime snapshot generated", "type": "evidence", "actorName": "Chart Runtime Collector", "responsibleRole": "Control", "status": "resolved", "relatedIncidentIds": [], "evidenceCount": 1, "impactScore": 24, "confidence": 72})
    return sorted(out, key=lambda item: item["time"])[-16:]


def build_mobile(pc_data, tablet_data, conn, source_paths=None):
    source_paths = source_paths or {}
    governance_available = bool(source_paths.get("pc") or source_paths.get("canonical"))
    generated = iso_now()
    pending = sum(item.get("count", 0) for item in tablet_data.get("syncOutboxStatusMatrix", []) if item.get("syncState") in {"pending", "retrying", "failed"})
    failed = sum(item.get("count", 0) for item in tablet_data.get("syncOutboxStatusMatrix", []) if item.get("syncState") == "failed")
    low_stock = sum(1 for item in pc_data.get("inventoryRiskTreemap", []) if item.get("level") == "sku" and item.get("stockoutRisk", 0) >= 50)
    incident_count = count_table(conn, "SupportIncident", "LOWER(status) NOT IN ('resolved','closed')") if conn else 0
    health = clamp(92 - failed * 12 - pending * 2 - low_stock * 5 - incident_count * 10, 20, 98)
    status = "PASS" if health >= 80 else "DEGRADED" if health >= 55 else "FAIL"
    radar = [
        {"axis": "data_quality", "label": "Data quality", "value": 78 if governance_available else 68, "status": "PASS" if governance_available else "DEGRADED", "confidence": 72 if governance_available else 58, "staleMinutes": 0, "topReason": "SQLite snapshot read-only" if governance_available else "Tablet SQLite snapshot; PC/canonical optional source absent"},
        {"axis": "sync", "label": "Sync", "value": clamp(90 - failed * 15 - pending * 3), "status": "PASS" if failed == 0 else "DEGRADED", "confidence": 70, "staleMinutes": 0, "topReason": f"{pending} pending / {failed} failed"},
        {"axis": "alerts", "label": "Alerts", "value": clamp(90 - incident_count * 12), "status": "PASS" if incident_count == 0 else "DEGRADED", "confidence": 62, "staleMinutes": 0, "topReason": f"{incident_count} open incidents"},
        {"axis": "inventory", "label": "Inventory", "value": clamp(88 - low_stock * 8), "status": "PASS" if low_stock == 0 else "DEGRADED", "confidence": 64, "staleMinutes": 0, "topReason": f"{low_stock} risky SKUs"},
        {"axis": "uptime", "label": "Uptime", "value": 82 if governance_available else 64, "status": "PASS" if governance_available else "DEGRADED", "confidence": 60 if governance_available else 48, "staleMinutes": 0, "topReason": "Local DB reachable" if governance_available else "Tablet DB reachable; PC/canonical optional source absent"},
        {"axis": "cashflow", "label": "Cashflow", "value": health, "status": status, "confidence": 63, "staleMinutes": 0, "topReason": "Sales snapshot"}
    ]
    actions = []
    if failed:
        actions.append({"responsibleName": "Sync", "role": "Backoffice", "moduleId": "sync", "priority": "critical" if failed > 3 else "high", "openCount": failed, "overdueCount": failed, "blockedCount": failed, "dueSoonCount": pending, "evidenceMissingCount": 0})
    if low_stock:
        actions.append({"responsibleName": "Inventory", "role": "Backoffice", "moduleId": "inventory", "priority": "high", "openCount": low_stock, "overdueCount": 0, "blockedCount": 0, "dueSoonCount": low_stock, "evidenceMissingCount": 0})
    if not actions:
        actions.append({"responsibleName": "Operations", "role": "Supervisor", "moduleId": "runtime", "priority": "low", "openCount": 1, "overdueCount": 0, "blockedCount": 0, "dueSoonCount": 1, "evidenceMissingCount": 0})
    pulse = []
    for index in range(8):
        t = datetime.now(timezone.utc) - timedelta(minutes=(7 - index) * 30)
        value = clamp(health - max(0, 3 - index) * 2 + min(index, 4), 0, 100)
        pulse.append({"time": as_iso(t), "healthScore": value, "status": "PASS" if value >= 80 else "DEGRADED" if value >= 55 else "FAIL", "activeIncidentCount": incident_count, "openActionCount": sum(item["openCount"] for item in actions), "dataConfidence": 70, "freshnessMinutes": 0, "annotation": "SQLite snapshot" if index == 7 else None})
    governance_beacon = {
        "moduleId": "pc-canonical-db",
        "moduleName": "PC/Canonical DB",
        "lastUpdatedAt": generated,
        "staleMinutes": 0,
        "ttlMinutes": 30,
        "freshnessState": "fresh",
        "confidence": 68,
        "source": "server"
    } if governance_available else {
        "moduleId": "pc-canonical-db",
        "moduleName": "PC/Canonical DB (optional)",
        "lastUpdatedAt": generated,
        "staleMinutes": 0,
        "ttlMinutes": 30,
        "freshnessState": "unknown",
        "confidence": 42,
        "source": "cache"
    }
    freshness = [
        {"moduleId": "tablet-db", "moduleName": "Tablet DB", "lastUpdatedAt": generated, "staleMinutes": 0, "ttlMinutes": 15, "freshnessState": "fresh", "confidence": 74, "source": "local"},
        governance_beacon,
        {"moduleId": "chart-runtime", "moduleName": "Chart Runtime", "lastUpdatedAt": generated, "staleMinutes": 0, "ttlMinutes": 10, "freshnessState": "fresh", "confidence": 76, "source": "cache"}
    ]
    incidents = []
    if incident_count or failed or low_stock:
        incidents.append({"incidentId": "sqlite-runtime-pressure", "title": "Runtime pressure detected", "severity": "ERROR" if failed or incident_count else "WARN", "state": "active", "moduleId": "sync" if failed else "inventory", "points": [{"time": point["time"], "impactScore": clamp(100 - point["healthScore"]), "healthScore": point["healthScore"]} for point in pulse], "recommendedNextAction": "Review sync and inventory evidence", "owner": "Operations", "evidenceCount": pending + low_stock + incident_count})
    else:
        incidents.append({"incidentId": "sqlite-runtime-ok", "title": "Runtime snapshot healthy", "severity": "INFO", "state": "resolved", "moduleId": "runtime", "points": [{"time": point["time"], "impactScore": 10, "healthScore": point["healthScore"]} for point in pulse], "recommendedNextAction": "Keep monitoring", "owner": "Operations", "evidenceCount": 1})
    confidence = [
        {"dimension": "completeness", "label": "Completeness", "value": 72, "state": "medium", "reason": "Core SQLite tables sampled", "affectedModules": ["sales", "sync", "inventory"]},
        {"dimension": "recency", "label": "Recency", "value": 86, "state": "high", "reason": "Snapshot generated locally", "affectedModules": ["runtime"]},
        {"dimension": "consistency", "label": "Consistency", "value": 68, "state": "medium", "reason": "Read-only aggregate queries", "affectedModules": ["sqlite"]},
        {"dimension": "evidence", "label": "Evidence", "value": 70, "state": "medium", "reason": "Counts mapped from DB tables", "affectedModules": ["outbox", "sales"]},
        {"dimension": "coverage", "label": "Coverage", "value": 64, "state": "medium", "reason": "Some charts use derived runtime metrics", "affectedModules": ["mobile", "pc"]}
    ]
    return {"ownerPulseTimeline": pulse, "actionInboxPriorityStack": actions, "healthRadarCompact": radar, "freshnessBeaconGrid": freshness, "incidentSparkCards": incidents, "confidenceMeterBands": confidence}


def prepare_runtime_read_model(repo: Path, runtime_db: Path, snapshot: dict | None = None, status: dict | None = None) -> dict:
    runtime_db = resolve_runtime_db_path(repo, str(runtime_db))
    runtime_db.parent.mkdir(parents=True, exist_ok=True)
    generated_at = (snapshot or {}).get("meta", {}).get("generatedAt") or (snapshot or {}).get("generatedAt") or iso_now()
    meta = (snapshot or {}).get("meta", {}) if snapshot else {}
    paths = meta.get("databasePaths") or (status or {}).get("databasePaths") or {}
    warnings = meta.get("warnings") or (status or {}).get("warnings") or []
    evidence = meta.get("evidence") or (status or {}).get("evidence") or []
    runtime_ready = bool(meta.get("runtimeReady") if snapshot else (status or {}).get("runtimeReady"))
    source_mode = meta.get("sourceMode") or (status or {}).get("sourceMode") or ("sqlite-runtime" if runtime_ready else "mock-fallback")
    data_status = meta.get("dataStatus") or (status or {}).get("dataStatus") or derive_data_status(runtime_ready, paths)

    conn = sqlite3.connect(runtime_db)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runtime_metadata (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL,
              updatedAt TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runtime_sources (
              sourceKey TEXT PRIMARY KEY,
              path TEXT,
              state TEXT NOT NULL,
              sourceKind TEXT NOT NULL,
              sourceOfTruth INTEGER NOT NULL DEFAULT 0,
              openedReadOnly INTEGER NOT NULL DEFAULT 1,
              requiredForTabletSales INTEGER NOT NULL DEFAULT 0,
              updatedAt TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runtime_chart_payloads (
              chartKey TEXT PRIMARY KEY,
              surface TEXT NOT NULL,
              payloadJson TEXT NOT NULL,
              dataStatus TEXT NOT NULL,
              sourceMode TEXT NOT NULL,
              generatedAt TEXT NOT NULL
            )
        """)
        metadata = {
            "runtimeDbKind": "derived-read-model",
            "sourceOfTruth": False,
            "replacesCanonicalDb": False,
            "requiredForTabletSales": False,
            "uiMayOpenDb": False,
            "generatedAt": generated_at,
            "sourceMode": source_mode,
            "dataStatus": data_status,
            "warnings": warnings,
            "evidence": evidence
        }
        for key, value in metadata.items():
            conn.execute(
                "INSERT OR REPLACE INTO runtime_metadata (key, value, updatedAt) VALUES (?, ?, ?)",
                (key, json.dumps(value, ensure_ascii=False), generated_at)
            )

        conn.execute("DELETE FROM runtime_sources")
        for source_key in ["tablet", "pc", "canonical"]:
            source_path = paths.get(source_key)
            state = "available" if source_path else "optional-missing" if source_key in {"pc", "canonical"} else "missing"
            source_kind = "tablet-sqlite-read-only" if source_key == "tablet" else "governance-sqlite-read-only"
            conn.execute(
                """
                INSERT INTO runtime_sources
                  (sourceKey, path, state, sourceKind, sourceOfTruth, openedReadOnly, requiredForTabletSales, updatedAt)
                VALUES (?, ?, ?, ?, 0, 1, 0, ?)
                """,
                (source_key, source_path, state, source_kind, generated_at)
            )

        if snapshot:
            conn.execute("DELETE FROM runtime_chart_payloads")
            for surface in ["pc", "tablet", "mobile"]:
                charts = snapshot.get(surface) or {}
                for chart_key, payload in charts.items():
                    conn.execute(
                        """
                        INSERT INTO runtime_chart_payloads
                          (chartKey, surface, payloadJson, dataStatus, sourceMode, generatedAt)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (chart_key, surface, json.dumps(payload, ensure_ascii=False), data_status, source_mode, generated_at)
                    )
        conn.commit()
    finally:
        conn.close()

    chart_count = 0
    source_count = 0
    conn = sqlite3.connect(f"file:{runtime_db.as_posix()}?mode=ro", uri=True)
    try:
        chart_count = int(conn.execute("SELECT COUNT(*) FROM runtime_chart_payloads").fetchone()[0])
        source_count = int(conn.execute("SELECT COUNT(*) FROM runtime_sources").fetchone()[0])
    finally:
        conn.close()
    return {
        **runtime_db_status(runtime_db),
        "status": "PASS",
        "refreshedPayloads": bool(snapshot),
        "chartPayloadCount": chart_count,
        "sourceCount": source_count,
        "safety": {
            "writesOnlyRuntimeReadModel": True,
            "writesTabletSQLite": False,
            "sourceSqliteOpenedReadOnly": True,
            "uiOpensDb": False
        }
    }


def collect_snapshot(repo: Path, output: Path, explicit=None, runtime_db: Path | None = None):
    selected, discovery = discover_db_paths(repo, explicit=explicit)
    warnings = []
    evidence = []
    conns = {}
    for key, path in selected.items():
        if path:
            try:
                conns[key] = connect_ro(path)
                evidence.append(f"{key}:{path}")
            except Exception as exc:
                warnings.append(f"Could not open {key} DB {path}: {exc}")
    primary = conns.get("pc") or conns.get("canonical") or conns.get("tablet")
    tablet_conn = conns.get("tablet") or primary
    pc_conn = conns.get("pc") or conns.get("canonical") or primary
    runtime_ready = bool(primary)
    paths = {k: str(v) if v else None for k, v in selected.items()}
    data_status = derive_data_status(runtime_ready, paths)
    if not runtime_ready:
        warnings.append("No SQLite database found under repo candidates or explicit args; Chart Lab will keep shared mock fallback.")
    elif not conns.get("pc") and not conns.get("canonical"):
        warnings.append("PC/canonical DB not found; PC governance charts are derived from the available Tablet SQLite snapshot.")
    pc = {}
    tablet = {}
    mobile = {}
    if runtime_ready and pc_conn:
        paths_for_graph = {k: str(v) if v else None for k, v in selected.items()}
        pc = {
            "causalFlowRibbon": build_causal(pc_conn),
            "operationalDensityField": build_density(pc_conn),
            "operationalDensityHeatmap": build_density(pc_conn),
            "serviceDependencyGraph": build_service_graph(paths_for_graph),
            "inventoryRiskTreemap": build_inventory(pc_conn),
            "decisionLedgerTimeline": build_decision(pc_conn),
            "financialOperationalWaterfall": build_waterfall(pc_conn)
        }
    if runtime_ready and tablet_conn:
        tablet = {"shiftPulseStrip": build_shift_pulse(tablet_conn), "syncOutboxStatusMatrix": build_sync_matrix(tablet_conn)}
    if runtime_ready:
        mobile = build_mobile(pc, tablet, pc_conn, selected)
    snapshot = {
        "schemaVersion": "1.0",
        "generatedAt": iso_now(),
        "meta": {
            "runtimeReady": runtime_ready,
            "sourceMode": "sqlite-runtime" if runtime_ready else "mock-fallback",
            "dataStatus": data_status,
            "generatedAt": iso_now(),
            "databasePaths": paths,
            "warnings": warnings,
            "evidence": evidence,
            "discovery": discovery,
            "runtimeReadModel": runtime_db_status(runtime_db) if runtime_db else None,
            "safety": {"readOnlySqlite": True, "browserDbAccess": False, "persistentBrowserStorage": False, "tabletStillStandalone": True, "pcOptional": True, "mobileSupervisionOnly": True}
        },
        "pc": pc,
        "tablet": tablet,
        "mobile": mobile,
        "quality": {}
    }
    write_text(output, json.dumps(snapshot, ensure_ascii=False, indent=2))
    for conn in conns.values():
        try:
            conn.close()
        except Exception:
            pass
    return snapshot


def inspect_runtime_status(repo: Path, explicit=None, runtime_db: Path | None = None):
    selected, discovery = discover_db_paths(repo, explicit=explicit)
    warnings = []
    evidence = []
    opened = {}
    for key, path in selected.items():
        if not path:
            continue
        try:
            conn = connect_ro(path)
            opened[key] = path
            evidence.append(f"{key}:{path}")
            conn.close()
        except Exception as exc:
            warnings.append(f"Could not open {key} DB {path}: {exc}")
    runtime_ready = bool(opened)
    if not runtime_ready:
        warnings.append("No readable SQLite database found under repo candidates or explicit args; Chart Lab will keep shared mock fallback.")
    elif not opened.get("pc") and not opened.get("canonical"):
        warnings.append("PC/canonical DB not found; PC governance charts are derived from the available Tablet SQLite snapshot.")
    paths = {k: str(opened.get(k)) if opened.get(k) else None for k in ["tablet", "pc", "canonical"]}
    return {
        "selected": {k: str(v) if v else None for k, v in selected.items()},
        "databasePaths": paths,
        "discovery": discovery,
        "runtimeReady": runtime_ready,
        "sourceMode": "sqlite-runtime" if runtime_ready else "mock-fallback",
        "dataStatus": derive_data_status(runtime_ready, paths),
        "warnings": warnings,
        "evidence": evidence,
        "runtimeReadModel": runtime_db_status(runtime_db) if runtime_db else runtime_db_status(resolve_runtime_db_path(repo, None)),
        "safety": {
            "readOnlySqlite": True,
            "browserDbAccess": False,
            "persistentBrowserStorage": False,
            "tabletStillStandalone": True,
            "pcOptional": True,
            "mobileSupervisionOnly": True
        }
    }

# ------------------------------------------------------------
# Patch helpers
# ------------------------------------------------------------

def patch_registry(path: Path):
    text = read_text(path)
    original = text
    import_line = 'import { chartRuntimeDataStatus, chartRuntimeFreshnessLabel, runtimeMobileCharts, runtimePcCharts, runtimeTabletCharts } from "./chart-runtime-data";\n'
    if import_line not in text:
        marker = 'import type { LabChartEntry } from "./chart-lab-types";\n'
        if marker not in text:
            raise RuntimeError("No encontre import de LabChartEntry en chart-lab-registry.tsx")
        text = text.replace(marker, marker + import_line, 1)
    text = text.replace("mockPcCharts.", "runtimePcCharts.")
    text = text.replace("mockTabletCharts.", "runtimeTabletCharts.")
    text = text.replace("mockMobileCharts.", "runtimeMobileCharts.")
    text = text.replace('dataStatus: "shared/mock",', "dataStatus: chartRuntimeDataStatus,")
    text = re.sub(r'freshnessLabel: "[^"]*",', "freshnessLabel: chartRuntimeFreshnessLabel,", text)
    if text != original:
        write_text(path, text)
        return True
    return False


def scan_forbidden_ui(repo: Path):
    hits = []
    for rel in [REGISTRY_REL, RUNTIME_TS_REL]:
        path = repo / rel
        if not path.exists():
            continue
        text = read_text(path)
        for token in FORBIDDEN_UI_TOKENS:
            if token in text:
                hits.append(f"{rel.as_posix()}: {token}")
    if hits:
        raise RuntimeError("Token prohibido en UI/runtime chart loader: " + "; ".join(hits))


def patch_repo(repo: Path, report: dict):
    changed = []
    runtime_ts = repo / RUNTIME_TS_REL
    if not runtime_ts.exists() or read_text(runtime_ts) != RUNTIME_TS:
        write_text(runtime_ts, RUNTIME_TS)
        changed.append(RUNTIME_TS_REL)
    snapshot_path = repo / SNAPSHOT_JSON_REL
    if not snapshot_path.exists():
        write_text(snapshot_path, json.dumps(SNAPSHOT_STUB, ensure_ascii=False, indent=2))
        changed.append(SNAPSHOT_JSON_REL)
    tool_path = repo / TOOL_REL
    current_engine = Path(__file__).read_text(encoding="utf-8")
    if not tool_path.exists() or read_text(tool_path) != current_engine:
        write_text(tool_path, current_engine)
        changed.append(TOOL_REL)
    if patch_registry(repo / REGISTRY_REL):
        changed.append(REGISTRY_REL)
    report["files_modified"].extend([rel.as_posix() for rel in changed])
    return changed

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=os.environ.get("PRISMA_REPO_ROOT", r"F:\repos\hitech-os\apps\terminal-de-venta-system"))
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--output", default=None)
    parser.add_argument("--tablet-db", default=None)
    parser.add_argument("--pc-db", default=None)
    parser.add_argument("--canonical-db", default=None)
    parser.add_argument("--status-only", action="store_true")
    parser.add_argument("--runtime-db", default=None, help="Optional derived read-model SQLite DB. Default: products/chart-lab/app/data/chart-runtime-governance.db")
    parser.add_argument("--prepare-runtime-db", action="store_true", help="Create/update the optional Chart Lab derived read-model DB schema and metadata. Does not touch Tablet SQLite.")
    parser.add_argument("--refresh-runtime-db", action="store_true", help="Refresh the optional derived read-model DB from the generated snapshot payloads. Implies --prepare-runtime-db.")
    args = parser.parse_args()

    repo = resolve_repo_root(args.repo_root)

    explicit = {"tablet": args.tablet_db, "pc": args.pc_db, "canonical": args.canonical_db}
    output = Path(args.output) if args.output else repo / SNAPSHOT_JSON_REL
    runtime_db = resolve_runtime_db_path(repo, args.runtime_db)

    if args.status_only:
        print(json.dumps(inspect_runtime_status(repo, explicit=explicit, runtime_db=runtime_db), indent=2, ensure_ascii=False))
        return 0

    if args.prepare_runtime_db or args.refresh_runtime_db:
        snapshot = collect_snapshot(repo, output, explicit=explicit, runtime_db=runtime_db) if args.refresh_runtime_db else None
        status = None if snapshot else inspect_runtime_status(repo, explicit=explicit, runtime_db=runtime_db)
        result = prepare_runtime_read_model(repo, runtime_db, snapshot=snapshot, status=status)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.collect_only:
        snapshot = collect_snapshot(repo, output, explicit=explicit, runtime_db=runtime_db)
        print(json.dumps({"status": "PASS", "output": str(output), "runtimeReady": snapshot.get("meta", {}).get("runtimeReady"), "sourceMode": snapshot.get("meta", {}).get("sourceMode"), "dataStatus": snapshot.get("meta", {}).get("dataStatus"), "databasePaths": snapshot.get("meta", {}).get("databasePaths"), "warnings": snapshot.get("meta", {}).get("warnings", [])}, indent=2, ensure_ascii=False))
        return 0

    run = stamp()
    descargas = Path(r"F:\descargasf") if os.name == "nt" else Path.cwd()
    backup_root = descargas / f"PRISMA_CONNECT_CHARTS_TO_DATABASES_V2_BACKUP_{run}"
    report_path = descargas / f"PRISMA_CONNECT_CHARTS_TO_DATABASES_V2_REPORT_{run}.json"
    diff_path = descargas / f"PRISMA_CONNECT_CHARTS_TO_DATABASES_V2_DIFF_{run}.patch"
    untracked_bundle_path = descargas / f"PRISMA_CONNECT_CHARTS_TO_DATABASES_V2_UNTRACKED_{run}.json"
    backup_root.mkdir(parents=True, exist_ok=True)

    report = {
        "started_at": iso_now(),
        "repo_root": str(repo),
        "operation": "Connect Chart Lab charts to local SQLite databases through a read-only runtime snapshot, with explicit DB args, env-file discovery, untracked reporting, and mock fallback preserved.",
        "files_modified": [],
        "gates": [],
        "generated_cleanup": [],
        "snapshot": {},
        "safety_confirmations": {"tablet_product_touched": False, "mobile_product_touched": False, "pc_product_touched": False, "auth_sync_tri_db_licensing_backend_runtime_db_touched": False, "runtime_db_written": False, "browser_storage_added": False, "browser_direct_db_access_added": False, "mock_fallback_preserved": True, "tablet_still_sells_alone": True, "pc_optional": True, "mobile_supervision_only": True},
        "status": "STARTED"
    }
    manifest = []
    try:
        git_root = git_root_for(repo)
        report["git_root"] = str(git_root)
        before_names, before_probe = diff_names(repo)
        before_status, before_status_probe = git_status_porcelain(repo)
        report["git_diff_names_before"] = before_names
        report["git_status_before"] = before_status
        report["git_probe_before"] = before_probe
        report["git_status_probe_before"] = before_status_probe

        for rel in [*ALLOWED_RELS, *GENERATED_RELS]:
            backup_file(repo, rel, backup_root, manifest)

        patch_repo(repo, report)
        snapshot = collect_snapshot(repo, repo / SNAPSHOT_JSON_REL, explicit=explicit, runtime_db=runtime_db)
        if SNAPSHOT_JSON_REL.as_posix() not in report["files_modified"]:
            report["files_modified"].append(SNAPSHOT_JSON_REL.as_posix())
        report["snapshot"] = {"runtimeReady": snapshot.get("meta", {}).get("runtimeReady"), "sourceMode": snapshot.get("meta", {}).get("sourceMode"), "dataStatus": snapshot.get("meta", {}).get("dataStatus"), "databasePaths": snapshot.get("meta", {}).get("databasePaths"), "warnings": snapshot.get("meta", {}).get("warnings", []), "runtimeReadModel": snapshot.get("meta", {}).get("runtimeReadModel"), "pcKeys": sorted(snapshot.get("pc", {}).keys()), "tabletKeys": sorted(snapshot.get("tablet", {}).keys()), "mobileKeys": sorted(snapshot.get("mobile", {}).keys())}

        scan_forbidden_ui(repo)

        allowed_git_names = set()
        generated_git_names = set()
        for rel in ALLOWED_RELS:
            allowed_git_names.add(rel.as_posix())
            allowed_git_names.add(git_name_for(repo / rel, git_root))
        for rel in GENERATED_RELS:
            generated_git_names.add(rel.as_posix())
            generated_git_names.add(git_name_for(repo / rel, git_root))
        report["allowed_git_names"] = sorted(allowed_git_names)
        report["generated_git_names"] = sorted(generated_git_names)

        after_patch_names, after_patch_probe = diff_names(repo)
        after_patch_status, after_patch_status_probe = git_status_porcelain(repo)
        report["git_diff_names_after_patch"] = after_patch_names
        report["git_status_after_patch"] = after_patch_status
        report["git_probe_after_patch"] = after_patch_probe
        report["git_status_probe_after_patch"] = after_patch_status_probe

        new_dirty = sorted(set(after_patch_names) - set(before_names))
        report["new_dirty_files_after_patch"] = new_dirty
        unexpected = [item for item in new_dirty if item not in allowed_git_names]
        if unexpected:
            raise RuntimeError("Cambios fuera del perimetro tras patch: " + ", ".join(unexpected))

        pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd")
        if not pnpm:
            raise RuntimeError("pnpm no esta en PATH")
        for gate in GATES:
            actual = [pnpm if idx == 0 else part for idx, part in enumerate(gate)]
            result = run_cmd(actual, repo, timeout=1500)
            result["requested_cmd"] = gate
            report["gates"].append(result)
            if result["exit_code"] != 0:
                raise RuntimeError("Gate fallo: " + " ".join(gate) + f" exit={result['exit_code']}")

        after_gate_names, after_gate_probe = diff_names(repo)
        after_gate_status, after_gate_status_probe = git_status_porcelain(repo)
        report["git_diff_names_after_gates_before_cleanup"] = after_gate_names
        report["git_status_after_gates_before_cleanup"] = after_gate_status
        report["git_probe_after_gates_before_cleanup"] = after_gate_probe
        report["git_status_probe_after_gates_before_cleanup"] = after_gate_status_probe
        new_dirty_after_gates = sorted(set(after_gate_names) - set(before_names))
        report["new_dirty_files_after_gates_before_cleanup"] = new_dirty_after_gates
        generated_dirty = [item for item in new_dirty_after_gates if item in generated_git_names]
        for item in generated_dirty:
            entry = next((entry for entry in manifest if entry["relative_path"] == NEXT_ENV_REL.as_posix()), None)
            if entry:
                restore_one(repo, entry)
                report["generated_cleanup"].append({"file": item, "action": "restored_to_pre_run_state", "reason": "Next build generated or touched next-env.d.ts"})

        after_cleanup_names, after_cleanup_probe = diff_names(repo)
        after_cleanup_status, after_cleanup_status_probe = git_status_porcelain(repo)
        report["git_diff_names_after_cleanup"] = after_cleanup_names
        report["git_status_after_cleanup"] = after_cleanup_status
        report["git_probe_after_cleanup"] = after_cleanup_probe
        report["git_status_probe_after_cleanup"] = after_cleanup_status_probe
        new_dirty_after_cleanup = sorted(set(after_cleanup_names) - set(before_names))
        report["new_dirty_files_after_cleanup"] = new_dirty_after_cleanup
        unexpected_after_cleanup = [item for item in new_dirty_after_cleanup if item not in allowed_git_names]
        if unexpected_after_cleanup:
            raise RuntimeError("Cambios fuera del perimetro tras cleanup: " + ", ".join(unexpected_after_cleanup))

        untracked_paths = [repo / rel for rel in ALLOWED_RELS if (repo / rel).exists()]
        untracked_names = write_untracked_bundle(repo, git_root, untracked_paths, untracked_bundle_path)
        report["untracked_bundle_path"] = str(untracked_bundle_path)
        report["untracked_bundle_files"] = untracked_names

        diff_text = full_diff(repo, [repo / rel for rel in ALLOWED_RELS])
        diff_path.write_text(diff_text, encoding="utf-8")
        report["diff_path"] = str(diff_path)
        report["diff_bytes"] = len(diff_text.encode("utf-8"))
        report["status"] = "PASS"
        report["finished_at"] = iso_now()
        report["backup_manifest"] = manifest
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        print("PASS: Chart Lab DB connection V2 listo.")
        print("Archivos modificados:")
        for item in report["files_modified"]:
            print(" - " + item)
        print("Snapshot runtimeReady:", report["snapshot"].get("runtimeReady"))
        print("DB paths:", json.dumps(report["snapshot"].get("databasePaths"), ensure_ascii=False))
        print("Gates:")
        for gate in report["gates"]:
            print(f" - {' '.join(gate['requested_cmd'])}: exit {gate['exit_code']}")
        print("Reporte:", report_path)
        print("Diff:", diff_path)
        print("Bundle de archivos nuevos/estado:", untracked_bundle_path)
        print("Backup:", backup_root)
        return 0
    except Exception as exc:
        report["status"] = "ROLLBACK"
        report["error"] = str(exc)
        try:
            rollback(repo, manifest)
            report["rollback"] = "completed"
        except Exception as rb_exc:
            report["rollback"] = "failed: " + str(rb_exc)
        try:
            diff_text = full_diff(repo, [repo / rel for rel in ALLOWED_RELS])
            diff_path.write_text(diff_text, encoding="utf-8")
            report["diff_path"] = str(diff_path)
            report["diff_bytes"] = len(diff_text.encode("utf-8"))
            status_rows, status_probe = git_status_porcelain(repo)
            report["git_status_after_rollback"] = status_rows
            report["git_status_probe_after_rollback"] = status_probe
        except Exception:
            pass
        report["finished_at"] = iso_now()
        report["backup_manifest"] = manifest
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print("FAILED: rollback ejecutado.")
        print("Error:", exc)
        print("Reporte:", report_path)
        print("Backup:", backup_root)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
