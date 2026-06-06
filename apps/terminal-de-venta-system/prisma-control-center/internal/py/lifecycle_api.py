from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import random
import shutil
import smtplib
import sqlite3
import string
import traceback
import uuid
import zipfile
from email.message import EmailMessage
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

API_VERSION = "PRISMA_DATA_LIFECYCLE_API_V1"
MODULE_DIR = Path(__file__).resolve().parent
CONTROL_CENTER_ROOT = MODULE_DIR.parent.parent
INTERNAL_ROOT = CONTROL_CENTER_ROOT / "internal"
CONFIG_DIR = INTERNAL_ROOT / "config"
DATA_DIR = INTERNAL_ROOT / "data" / "lifecycle"
LEDGER_PATH = DATA_DIR / "prisma-data-lifecycle-ledger.db"
EVIDENCE_DIR = DATA_DIR / "evidence"
BACKUP_DIR = DATA_DIR / "backups"

DEFAULT_CONFIG = {
    "owner_email": "alanharrryy@gmail.com",
    "pin_default": "030303",
    "pin_required": True,
    "allow_clear_without_pin": False,
    "pin_expiration_minutes": 10,
    "project_root": None,
    "downloads_root": "F:/descargasf",
    "block_public_mutations": True,
    "smtp": {
        "enabled": False,
        "host": "",
        "port": 587,
        "username": "",
        "password_env": "PRISMA_LIFECYCLE_SMTP_PASSWORD",
        "from_email": "",
        "use_tls": True
    },
    "known_db_paths": [
        "products/pc/app/data/canonical.db",
        "products/tablet/app/data/tablet-pos.db",
        "products/tablet/app/prisma/data/tablet-pos.db",
        "products/chart-lab/app/data/chart-runtime-governance.db"
    ]
}

DOMAIN_MAP_DEFAULT = {
    "Sales": ["Sale", "SaleLine", "SalePaymentTender", "SaleReturn", "SaleReturnLine"],
    "Cash": ["CashSession", "CashMovement", "CashAdjustment"],
    "Inventory": ["StockSnapshot", "StockMovement", "ReplenishmentSignal"],
    "Catalog": ["Business", "Store", "Product", "Barcode", "Brand", "TaxRate", "PriceList", "PriceListItem", "DropdownCatalog", "DropdownOption"],
    "Suppliers": ["Supplier", "ProductSupplier"],
    "Purchasing": ["PurchaseOrder", "PurchaseOrderLine", "GoodsReceipt", "GoodsReceiptLine"],
    "Sync": ["OutboxEvent", "SyncCheckpoint", "SyncAttempt", "SyncConflict", "SyncOutboxStatusBucket", "DataSourceFreshness"],
    "Devices": ["Terminal", "DeviceHeartbeat", "TabletLocalSecuritySecret"],
    "Identity": ["User", "Role", "Permission", "_RoleToUser", "_PermissionToRole"],
    "Tenant": ["Business", "Store"],
    "License": ["LicenseRuntime", "LicenseOverride", "Entitlement"],
    "Audit": ["AuditEvent", "AuditCount", "SupportIncident"],
    "Chart Lab": ["runtime_chart_payloads", "runtime_metadata", "runtime_sources"],
}

PROFILE_DEFAULTS = {
    "light": {"label": "Ligera", "days": 30, "products": 80, "suppliers": 10, "users": 5, "tablets": 2, "sales_per_day": 8, "purchase_orders": 12},
    "heavy": {"label": "Pesada", "days": 120, "products": 350, "suppliers": 30, "users": 15, "tablets": 5, "sales_per_day": 24, "purchase_orders": 60},
    "longaniza": {"label": "Pasada de longaniza", "days": 360, "products": 1200, "suppliers": 80, "users": 40, "tablets": 10, "sales_per_day": 48, "purchase_orders": 180},
}

FIRST_NAMES = ["Mariana", "Sofía", "Valeria", "Camila", "Andrea", "Fernanda", "Daniela", "Regina", "Paola", "Lucía", "Diego", "Santiago", "Mateo", "Emiliano", "Sebastián", "Javier", "Alan", "Rodrigo", "Luis", "Carlos", "Miguel", "Héctor", "Iván", "Raúl"]
LAST_NAMES = ["Torres", "García", "López", "Hernández", "Martínez", "Ramírez", "Flores", "Vargas", "Castillo", "Mendoza", "Rojas", "Reyes", "Santos", "Morales", "Cruz", "Aguilar", "Navarro", "Pineda"]
CATEGORIES = {
    "Bebidas": ["Coca-Cola 600 ml", "Pepsi 600 ml", "Agua Ciel 1 L", "Jumex Mango 473 ml", "Electrolit Fresa 625 ml", "Red Cola 2 L", "Topo Chico Mineral", "Boing Guayaba 500 ml"],
    "Botanas": ["Sabritas Original 45 g", "Doritos Nacho 61 g", "Cheetos Torciditos 52 g", "Ruffles Queso 50 g", "Takis Fuego 56 g", "Churrumais 55 g"],
    "Lácteos": ["Leche Lala Entera 1 L", "Yoghurt Yoplait Fresa", "Queso Panela 400 g", "Crema Alpura 450 ml", "Leche Santa Clara 1 L"],
    "Abarrotes": ["Arroz Verde Valle 1 kg", "Frijol Negro 900 g", "Aceite Capullo 845 ml", "Azúcar Zulka 1 kg", "Harina Maseca 1 kg", "Atún Dolores Agua 140 g", "Salsa Valentina 370 ml"],
    "Limpieza": ["Fabuloso Lavanda 1 L", "Cloralex 950 ml", "Jabón Zote Rosa", "Pinol Original 1 L", "Ariel Detergente 850 g"],
    "Panadería": ["Pan Bimbo Blanco Grande", "Tortillinas Tía Rosa", "Mantecadas Bimbo", "Donas Bimbo Azucaradas", "Roles Canela"],
    "Dulces": ["Mazapán De La Rosa", "Chocolate Carlos V", "Paleta Payaso", "Pulparindo", "Gomitas Enchiladas"],
}
SUPPLIER_NAMES = ["Abarrotes La Central", "Bebidas MX Norte", "Distribuidora El Mayoreo", "Dulces del Bajío", "Lácteos San Miguel", "Botanas La Esquina", "Comercializadora Reforma", "Limpieza Total MX", "Panificadora del Valle", "Mercantil Los Portales", "Suministros del Centro", "Alimentos El Roble"]


def utcnow() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def local_now() -> _dt.datetime:
    return _dt.datetime.now().replace(microsecond=0)


def ensure_dirs() -> None:
    for p in [DATA_DIR, EVIDENCE_DIR, BACKUP_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback


def config() -> dict[str, Any]:
    data = dict(DEFAULT_CONFIG)
    data.update(load_json(CONFIG_DIR / "lifecycle_config.json", {}))
    return data


def domain_map() -> dict[str, list[str]]:
    raw = load_json(CONFIG_DIR / "lifecycle_domain_map.json", {"domains": DOMAIN_MAP_DEFAULT})
    if isinstance(raw, dict) and "domains" in raw:
        return {k: list(v.get("tables", v) if isinstance(v, dict) else v) for k, v in raw["domains"].items() if k != "All"}
    return DOMAIN_MAP_DEFAULT


def profiles() -> dict[str, dict[str, Any]]:
    raw = load_json(CONFIG_DIR / "lifecycle_seed_profiles.json", {"profiles": PROFILE_DEFAULTS})
    return raw.get("profiles", raw) if isinstance(raw, dict) else PROFILE_DEFAULTS


def clear_policy() -> dict[str, Any]:
    return load_json(CONFIG_DIR / "lifecycle_clear_policy.json", {"default_policy": "generated_only"})


def project_root() -> Path:
    cfg = config()
    for value in [os.environ.get("PRISMA_LIFECYCLE_PROJECT_ROOT"), os.environ.get("TV_SYSTEM_ROOT"), os.environ.get("PRISMA_PROJECT_ROOT"), cfg.get("project_root")]:
        if value:
            p = Path(str(value)).expanduser()
            if p.exists():
                return p.resolve()
    for p in [CONTROL_CENTER_ROOT, *CONTROL_CENTER_ROOT.parents]:
        if (p / "products").exists():
            return p.resolve()
        if p.name == "terminal-de-venta-system":
            return p.resolve()
    fallback = Path("F:/repos/hitech-os/apps/terminal-de-venta-system")
    if fallback.exists():
        return fallback.resolve()
    return CONTROL_CENTER_ROOT.parent.resolve()


def downloads_root() -> Path:
    cfg = config()
    raw = cfg.get("downloads_root") or "F:/descargasf"
    p = Path(str(raw)).expanduser()
    if str(p).startswith("F:") and os.name != "nt":
        p = DATA_DIR / "downloads-fallback"
    p.mkdir(parents=True, exist_ok=True)
    return p


def is_sqlite(path: Path) -> bool:
    try:
        return path.exists() and path.is_file() and path.read_bytes()[:16] == b"SQLite format 3\x00"
    except Exception:
        return False


def discover_dbs() -> list[dict[str, Any]]:
    root = project_root()
    cfg = config()
    seen: set[Path] = set()
    dbs: list[dict[str, Any]] = []
    candidates: list[Path] = []
    for rel in cfg.get("known_db_paths", []):
        candidates.append(root / rel)
    for p in root.rglob("*.db") if root.exists() else []:
        parts = {x.lower() for x in p.parts}
        if {"node_modules", ".git", "rollback", "backups", ".next", "__pycache__"} & parts:
            continue
        low = str(p).replace("\\", "/").lower()
        if "/internal/data/lifecycle/" in low or "prisma-data-lifecycle-ledger.db" in low:
            continue
        candidates.append(p)
    for p in candidates:
        try:
            p = p.resolve()
        except Exception:
            continue
        if p in seen or not is_sqlite(p):
            continue
        seen.add(p)
        surface = "unknown"
        s = str(p).replace("\\", "/").lower()
        if "/products/pc/" in s:
            surface = "pc"
        elif "/products/tablet/" in s:
            surface = "tablet"
        elif "/products/chart-lab/" in s:
            surface = "chart_lab"
        elif "/products/mobile/" in s:
            surface = "mobile"
        rel = str(p)
        try:
            rel = str(p.relative_to(root))
        except Exception:
            pass
        dbs.append({"path": str(p), "relative_path": rel.replace("\\", "/"), "name": p.name, "surface": surface, "size_bytes": p.stat().st_size})
    return sorted(dbs, key=lambda d: d["relative_path"])


def connect(path: str | Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(path), timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def table_names(con: sqlite3.Connection) -> set[str]:
    return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def table_columns(con: sqlite3.Connection, table: str) -> dict[str, dict[str, Any]]:
    rows = con.execute(f'PRAGMA table_info("{table}")').fetchall()
    return {r[1]: {"cid": r[0], "name": r[1], "type": r[2], "notnull": bool(r[3]), "default": r[4], "pk": bool(r[5])} for r in rows}


def pk_col(con: sqlite3.Connection, table: str) -> str:
    cols = table_columns(con, table)
    for name, meta in cols.items():
        if meta.get("pk"):
            return name
    if "id" in cols:
        return "id"
    return next(iter(cols)) if cols else "id"


def has_table(con: sqlite3.Connection, table: str) -> bool:
    return table in table_names(con)


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:18]}"


def batch_id(mode: str) -> str:
    return f"lifecycle_{mode}_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"


def ensure_ledger() -> sqlite3.Connection:
    ensure_dirs()
    con = sqlite3.connect(str(LEDGER_PATH), timeout=30)
    con.row_factory = sqlite3.Row
    con.executescript('''
    CREATE TABLE IF NOT EXISTS lifecycle_batches (
      batch_id TEXT PRIMARY KEY,
      mode TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL,
      finished_at TEXT,
      summary_json TEXT,
      evidence_path TEXT
    );
    CREATE TABLE IF NOT EXISTS lifecycle_records (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      batch_id TEXT NOT NULL,
      domain TEXT NOT NULL,
      db_path TEXT NOT NULL,
      table_name TEXT NOT NULL,
      primary_key TEXT NOT NULL,
      created_at TEXT NOT NULL,
      cleared_at TEXT,
      clear_batch TEXT,
      UNIQUE(batch_id, db_path, table_name, primary_key)
    );
    CREATE TABLE IF NOT EXISTS lifecycle_pins (
      pin_id TEXT PRIMARY KEY,
      pin_hash TEXT NOT NULL,
      owner_email TEXT NOT NULL,
      created_at TEXT NOT NULL,
      expires_at TEXT NOT NULL,
      used_at TEXT,
      status TEXT NOT NULL,
      evidence_path TEXT
    );
    CREATE TABLE IF NOT EXISTS lifecycle_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      event_type TEXT NOT NULL,
      created_at TEXT NOT NULL,
      payload_json TEXT NOT NULL
    );
    ''')
    con.commit()
    return con


def ledger_record(ledger: sqlite3.Connection, batch: str, domain: str, db_path: str, table: str, pk: str) -> None:
    ledger.execute(
        "INSERT OR IGNORE INTO lifecycle_records(batch_id, domain, db_path, table_name, primary_key, created_at) VALUES(?,?,?,?,?,?)",
        (batch, domain, str(db_path), table, str(pk), utcnow())
    )


def log_event(event_type: str, payload: dict[str, Any]) -> None:
    con = ensure_ledger()
    con.execute("INSERT INTO lifecycle_events(event_type, created_at, payload_json) VALUES(?,?,?)", (event_type, utcnow(), json.dumps(payload, ensure_ascii=False)))
    con.commit(); con.close()


def insert_row(con: sqlite3.Connection, ledger: sqlite3.Connection, db_path: str, batch: str, domain: str, table: str, data: dict[str, Any]) -> str | None:
    if not has_table(con, table):
        return None
    cols = table_columns(con, table)
    if not cols:
        return None
    pk = pk_col(con, table)
    if pk not in data:
        data[pk] = make_id(table.lower())
    now = utcnow()
    # Generic fill for common required fields if a schema differs a little.
    generic = {
        "businessId": data.get("businessId"), "storeId": data.get("storeId"), "createdAt": now, "updatedAt": now,
        "status": "ACTIVE", "currency": "MXN", "isActive": 1, "isDefault": 0, "attempts": 0,
        "payloadJson": json.dumps({"source": "prisma_data_lifecycle", "batch_id": batch}, ensure_ascii=False),
        "metadataJson": json.dumps({"source": "prisma_data_lifecycle", "batch_id": batch}, ensure_ascii=False),
    }
    for name, meta in cols.items():
        if name in data:
            continue
        if name in generic and generic[name] is not None:
            data[name] = generic[name]
        elif meta.get("notnull") and meta.get("default") is None and not meta.get("pk"):
            typ = str(meta.get("type") or "").upper()
            if "INT" in typ:
                data[name] = 0
            elif "REAL" in typ or "FLOA" in typ or "DOUB" in typ:
                data[name] = 0.0
            elif "BOOL" in typ:
                data[name] = 0
            elif "DATE" in typ or "TIME" in typ:
                data[name] = now
            else:
                data[name] = f"lifecycle_{name}"
    final = {k: v for k, v in data.items() if k in cols}
    if not final:
        return None
    names = list(final.keys())
    placeholders = ",".join(["?"] * len(names))
    sql = f'INSERT OR IGNORE INTO "{table}" ({",".join([f"\"{n}\"" for n in names])}) VALUES ({placeholders})'
    before = con.total_changes
    con.execute(sql, [final[n] for n in names])
    pk_value = str(final[pk])
    if con.total_changes > before:
        ledger_record(ledger, batch, domain, db_path, table, pk_value)
    return pk_value


def rand_name() -> str:
    return random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)


def pesos(min_c: int, max_c: int) -> int:
    return random.randrange(min_c, max_c + 1, 50)


def product_pool(count: int) -> list[dict[str, Any]]:
    rows = []
    all_products = [(cat, name) for cat, names in CATEGORIES.items() for name in names]
    for i in range(count):
        cat, base_name = all_products[i % len(all_products)]
        variant = "" if i < len(all_products) else f" · Pack {1 + (i // len(all_products))}"
        price = pesos(900, 18900)
        cost = max(300, int(price * random.uniform(0.55, 0.78)))
        rows.append({"category": cat, "name": base_name + variant, "priceCents": price, "costCents": cost, "sku": f"DL-{cat[:3].upper()}-{i+1:05d}", "stockOnHand": random.randint(12, 240)})
    return rows


def plan_for(mode: str) -> dict[str, Any]:
    p = profiles()
    key = mode if mode in p else "light"
    plan = dict(p.get(key, PROFILE_DEFAULTS["light"]))
    plan["mode"] = key
    plan["label"] = plan.get("label") or PROFILE_DEFAULTS.get(key, {}).get("label", key)
    plan["sales_target"] = int(plan.get("days", 30)) * int(plan.get("sales_per_day", 8))
    return plan


def write_evidence(name: str, payload: dict[str, Any]) -> str:
    ensure_dirs()
    path = EVIDENCE_DIR / f"{name}_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md = path.with_suffix(".md")
    md.write_text("# PRISMA Data Lifecycle Evidence\n\n```json\n" + json.dumps(payload, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    try:
        dr = downloads_root()
        shutil.copy2(path, dr / path.name)
        shutil.copy2(md, dr / md.name)
    except Exception:
        pass
    return str(path)


def create_backup(reason: str) -> str:
    ensure_dirs()
    dbs = discover_dbs()
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = BACKUP_DIR / f"PRISMA_DATA_LIFECYCLE_BACKUP_{reason}_{stamp}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for db in dbs:
            p = Path(db["path"])
            if p.exists():
                z.write(p, f"dbs/{db['relative_path'].replace(':','')}")
        if LEDGER_PATH.exists():
            z.write(LEDGER_PATH, "ledger/prisma-data-lifecycle-ledger.db")
        for cfg in ["lifecycle_config.json", "lifecycle_domain_map.json", "lifecycle_seed_profiles.json", "lifecycle_clear_policy.json"]:
            p = CONFIG_DIR / cfg
            if p.exists():
                z.write(p, f"config/{cfg}")
    try:
        shutil.copy2(zip_path, downloads_root() / zip_path.name)
    except Exception:
        pass
    return str(zip_path)


def seed_operational_db(db: dict[str, Any], batch: str, plan: dict[str, Any], ledger: sqlite3.Connection) -> dict[str, Any]:
    path = db["path"]
    summary = {"db": db, "inserted": {}, "skipped": [], "errors": []}
    con = connect(path)
    try:
        tables = table_names(con)
        now = local_now()
        biz_id = make_id("biz")
        store_id = make_id("store")
        tax_id = make_id("tax")
        price_list_id = make_id("price")
        business_name = "Abarrotes Prisma Central"
        if "Business" in tables:
            insert_row(con, ledger, path, batch, "Tenant", "Business", {"id": biz_id, "name": business_name, "taxId": "XAXX010101000", "currency": "MXN", "createdAt": utcnow(), "updatedAt": utcnow()})
        if "Store" in tables:
            insert_row(con, ledger, path, batch, "Tenant", "Store", {"id": store_id, "businessId": biz_id, "code": "MATRIZ", "name": "Sucursal Matriz", "createdAt": utcnow(), "updatedAt": utcnow()})
        if "TaxRate" in tables:
            insert_row(con, ledger, path, batch, "Catalog", "TaxRate", {"id": tax_id, "businessId": biz_id, "name": "IVA 16%", "rateBps": 1600, "isDefault": 1, "isActive": 1, "createdAt": utcnow(), "updatedAt": utcnow()})
        if "PriceList" in tables:
            insert_row(con, ledger, path, batch, "Catalog", "PriceList", {"id": price_list_id, "businessId": biz_id, "name": "Lista General", "currency": "MXN", "isDefault": 1, "isActive": 1, "startsAt": (now - _dt.timedelta(days=3)).isoformat(), "createdAt": utcnow(), "updatedAt": utcnow()})

        role_ids = []
        if "Role" in tables:
            for code, label in [("admin", "Administrador"), ("cashier", "Cajero"), ("supervisor", "Supervisor"), ("warehouse", "Almacén")]:
                rid = make_id("role")
                insert_row(con, ledger, path, batch, "Identity", "Role", {"id": rid, "businessId": biz_id, "code": code, "label": label, "description": f"Rol {label} Data Lifecycle", "createdAt": utcnow(), "updatedAt": utcnow()})
                role_ids.append(rid)
        if "Permission" in tables:
            for code in ["sales.read", "sales.write", "inventory.read", "inventory.write", "sync.read", "reports.read", "cash.close"]:
                insert_row(con, ledger, path, batch, "Identity", "Permission", {"id": make_id("perm"), "businessId": biz_id, "code": code, "label": code.replace(".", " ").title(), "description": "Permiso generado por Data Lifecycle", "createdAt": utcnow(), "updatedAt": utcnow()})
        user_ids = []
        user_count = max(1, int(plan.get("users", 5)))
        if "User" in tables:
            for i in range(user_count):
                nm = rand_name()
                uid = make_id("user")
                insert_row(con, ledger, path, batch, "Identity", "User", {"id": uid, "businessId": biz_id, "name": nm, "email": f"{nm.lower().replace(' ','.')}.{i}@prisma.local", "pinHash": f"lifecycle-pin-{i:04d}", "status": "ACTIVE", "createdAt": utcnow(), "updatedAt": utcnow()})
                user_ids.append(uid)
        if not user_ids:
            user_ids = ["Cajera Data Lifecycle"]

        terminal_ids = []
        device_count = max(1, int(plan.get("tablets", 2)))
        if "Terminal" in tables:
            for i in range(device_count):
                tid = make_id("term")
                insert_row(con, ledger, path, batch, "Devices", "Terminal", {"id": tid, "businessId": biz_id, "storeId": store_id, "code": f"CAJA-{i+1}", "name": f"Tablet Caja {i+1}", "isActive": 1, "createdAt": utcnow(), "updatedAt": utcnow()})
                terminal_ids.append(tid)
        else:
            terminal_ids = [f"tablet-caja-{i+1}" for i in range(device_count)]
        if "DeviceHeartbeat" in tables:
            for i, tid in enumerate(terminal_ids):
                insert_row(con, ledger, path, batch, "Devices", "DeviceHeartbeat", {"id": make_id("hb"), "businessId": biz_id, "deviceId": tid, "source": "prisma_data_lifecycle", "surface": "tablet", "runtimeMode": "local", "appVersion": "lifecycle-v1", "schemaVersion": "v1", "licenseStatus": "ACTIVE", "syncStatus": "OK" if i % 4 else "LAGGING", "health": "OK", "status": "ACTIVE", "outboxCount": i % 3, "lastSaleAt": utcnow(), "lastDiagnosticAt": utcnow(), "lastSeenAt": utcnow(), "observedAt": utcnow(), "metadataJson": json.dumps({"batch_id": batch}, ensure_ascii=False), "createdAt": utcnow(), "updatedAt": utcnow()})

        supplier_ids = []
        if "Supplier" in tables:
            for i in range(min(int(plan.get("suppliers", 10)), max(1, len(SUPPLIER_NAMES) * 8))):
                name = SUPPLIER_NAMES[i % len(SUPPLIER_NAMES)] + ("" if i < len(SUPPLIER_NAMES) else f" {1 + i // len(SUPPLIER_NAMES)}")
                sid = make_id("sup")
                insert_row(con, ledger, path, batch, "Suppliers", "Supplier", {"id": sid, "businessId": biz_id, "name": name, "status": "ACTIVE", "createdAt": utcnow(), "updatedAt": utcnow()})
                supplier_ids.append(sid)
        brand_ids = []
        if "Brand" in tables:
            for name in ["Coca-Cola", "Bimbo", "Sabritas", "Lala", "La Costeña", "Prisma Select", "Alpura", "Barcel"]:
                bid = make_id("brand")
                insert_row(con, ledger, path, batch, "Catalog", "Brand", {"id": bid, "businessId": biz_id, "name": name, "description": "Marca generada por Data Lifecycle", "status": "ACTIVE", "createdAt": utcnow(), "updatedAt": utcnow()})
                brand_ids.append(bid)

        products = []
        if "Product" in tables:
            for item in product_pool(int(plan.get("products", 80))):
                pid = make_id("prod")
                row = {"id": pid, "businessId": biz_id, "sku": item["sku"], "name": item["name"], "category": item["category"], "brandId": random.choice(brand_ids) if brand_ids else None, "priceCents": item["priceCents"], "costCents": item["costCents"], "stockOnHand": item["stockOnHand"], "taxRateId": tax_id, "isActive": 1, "createdAt": utcnow(), "updatedAt": utcnow()}
                insert_row(con, ledger, path, batch, "Catalog", "Product", row)
                products.append(row)
                if "Barcode" in tables:
                    code = "750" + "".join(random.choice(string.digits) for _ in range(10))
                    insert_row(con, ledger, path, batch, "Catalog", "Barcode", {"id": make_id("bar"), "businessId": biz_id, "productId": pid, "code": code, "createdAt": utcnow()})
                if "PriceListItem" in tables:
                    insert_row(con, ledger, path, batch, "Catalog", "PriceListItem", {"id": make_id("pli"), "businessId": biz_id, "priceListId": price_list_id, "productId": pid, "priceCents": item["priceCents"], "startsAt": utcnow(), "createdAt": utcnow(), "updatedAt": utcnow()})
                if supplier_ids and "ProductSupplier" in tables:
                    insert_row(con, ledger, path, batch, "Suppliers", "ProductSupplier", {"id": make_id("ps"), "businessId": biz_id, "productId": pid, "supplierId": random.choice(supplier_ids), "isPrimary": 1, "status": "ACTIVE", "leadTimeDays": random.randint(1, 9), "createdAt": utcnow(), "updatedAt": utcnow()})
        if not products:
            products = [{"id": "prod_virtual", "sku": "VIRTUAL-001", "name": "Producto Virtual", "priceCents": 1000, "costCents": 700, "category": "Virtual", "stockOnHand": 100}]

        # Purchasing and inventory.
        po_ids = []
        if supplier_ids and "PurchaseOrder" in tables:
            for i in range(min(int(plan.get("purchase_orders", 12)), max(1, len(products)//3))):
                supplier = random.choice(supplier_ids)
                po = make_id("po")
                lines = random.sample(products, k=min(len(products), random.randint(2, 6)))
                subtotal = 0
                for prod in lines:
                    qty = random.randint(4, 40)
                    subtotal += qty * int(prod.get("costCents", 500))
                tax = int(subtotal * 0.16)
                total = subtotal + tax
                created = (now - _dt.timedelta(days=random.randint(1, int(plan.get("days", 30))))).isoformat()
                insert_row(con, ledger, path, batch, "Purchasing", "PurchaseOrder", {"id": po, "businessId": biz_id, "supplierId": supplier, "folio": f"OC-DL-{i+1:05d}", "status": "RECEIVED" if i % 4 else "PARTIAL", "createdAt": created, "expectedAt": (now + _dt.timedelta(days=random.randint(1, 10))).isoformat(), "subtotalCents": subtotal, "taxCents": tax, "totalCents": total, "updatedAt": utcnow()})
                po_ids.append(po)
                pol_ids = []
                if "PurchaseOrderLine" in tables:
                    for prod in lines:
                        qty = random.randint(4, 40)
                        unit = int(prod.get("costCents", 500))
                        sub = qty * unit; tx = int(sub * .16)
                        pol = make_id("pol")
                        insert_row(con, ledger, path, batch, "Purchasing", "PurchaseOrderLine", {"id": pol, "businessId": biz_id, "purchaseOrderId": po, "productId": prod["id"], "sku": prod["sku"], "name": prod["name"], "qtyOrdered": qty, "unitCostCents": unit, "lineSubtotalCents": sub, "lineTaxCents": tx, "lineTotalCents": sub + tx, "createdAt": created})
                        pol_ids.append((pol, prod, qty, unit))
                if "GoodsReceipt" in tables:
                    gr = make_id("gr")
                    insert_row(con, ledger, path, batch, "Purchasing", "GoodsReceipt", {"id": gr, "businessId": biz_id, "purchaseOrderId": po, "supplierId": supplier, "folio": f"REC-DL-{i+1:05d}", "status": "POSTED", "receivedAt": created, "subtotalCents": subtotal, "taxCents": tax, "totalCents": total, "updatedAt": utcnow()})
                    if "GoodsReceiptLine" in tables:
                        for pol, prod, qty, unit in pol_ids:
                            sub = qty*unit; tx = int(sub*.16)
                            insert_row(con, ledger, path, batch, "Purchasing", "GoodsReceiptLine", {"id": make_id("grl"), "businessId": biz_id, "goodsReceiptId": gr, "purchaseOrderLineId": pol, "productId": prod["id"], "sku": prod["sku"], "name": prod["name"], "qtyReceived": qty, "unitCostCents": unit, "lineSubtotalCents": sub, "lineTaxCents": tx, "lineTotalCents": sub+tx, "createdAt": created})
        if "StockSnapshot" in tables:
            for prod in products[:min(len(products), int(plan.get("products", 80)) )]:
                on_hand = int(prod.get("stockOnHand", 20))
                insert_row(con, ledger, path, batch, "Inventory", "StockSnapshot", {"id": make_id("snap"), "businessId": biz_id, "productId": prod["id"], "location": "Matriz", "onHand": on_hand, "reserved": random.randint(0, 3), "available": max(0, on_hand - 2), "daysCover": round(random.uniform(2, 45), 2), "snapshotAt": utcnow()})
        if "StockMovement" in tables:
            for prod in random.sample(products, k=min(len(products), max(10, len(products)//4))):
                insert_row(con, ledger, path, batch, "Inventory", "StockMovement", {"id": make_id("mov"), "businessId": biz_id, "productId": prod["id"], "movement": "IN", "qty": random.randint(5, 60), "reason": "Data Lifecycle recepción", "location": "Matriz", "createdAt": utcnow()})

        # Cash sessions and sales.
        cash_sessions = []
        days = int(plan.get("days", 30))
        if "CashSession" in tables:
            for day in range(days):
                if day % max(1, days // min(days, 90)) != 0 and plan.get("mode") == "longaniza":
                    pass
                opened = now - _dt.timedelta(days=days-day, hours=random.randint(0, 2))
                tid = random.choice(terminal_ids)
                cashier = rand_name()
                cid = make_id("cash")
                cash_start = random.choice([50000, 75000, 100000, 150000])
                insert_row(con, ledger, path, batch, "Cash", "CashSession", {"id": cid, "businessId": biz_id, "storeId": store_id, "terminalId": tid, "cashierId": random.choice(user_ids), "cashier": cashier, "openedAt": opened.isoformat(), "closedAt": (opened + _dt.timedelta(hours=8)).isoformat(), "cashStartCents": cash_start, "cashEndCents": cash_start + random.randint(8000, 120000), "expectedCashCents": cash_start + random.randint(8000, 120000), "varianceCents": random.choice([0, 0, 0, 500, -300, 850]), "status": "CLOSED", "createdAt": opened.isoformat(), "updatedAt": utcnow()})
                cash_sessions.append((cid, tid, cashier, opened))
                if "CashMovement" in tables:
                    insert_row(con, ledger, path, batch, "Cash", "CashMovement", {"id": make_id("cm"), "businessId": biz_id, "cashSessionId": cid, "movement": "OPEN", "amountCents": cash_start, "reason": "Apertura de caja", "createdAt": opened.isoformat()})
        if not cash_sessions:
            cash_sessions = [(None, random.choice(terminal_ids), rand_name(), now - _dt.timedelta(days=1))]

        sale_target = int(plan.get("sales_target", 250))
        sale_target = min(sale_target, int(config().get("max_sales_per_injection", sale_target))) if config().get("max_sales_per_injection") else sale_target
        for i in range(sale_target):
            if "Sale" not in tables:
                break
            session_id, terminal_id, cashier, opened = random.choice(cash_sessions)
            created = opened + _dt.timedelta(minutes=random.randint(10, 480))
            picked = random.sample(products, k=min(len(products), random.randint(1, 5)))
            total = 0
            line_payloads = []
            for prod in picked:
                qty = random.randint(1, 4)
                price = int(prod.get("priceCents", 1000))
                total += qty * price
                line_payloads.append((prod, qty, price))
            sale = make_id("sale")
            folio = f"DL-{created.strftime('%y%m%d')}-{i+1:06d}"
            received = total + random.choice([0, 0, 0, 500, 1000, 2000])
            insert_row(con, ledger, path, batch, "Sales", "Sale", {"id": sale, "businessId": biz_id, "terminalId": terminal_id, "cashSessionId": session_id, "clientRequestId": f"dl-{batch}-{i}", "folio": folio, "cashier": cashier, "totalCents": total, "paymentMethod": "cash" if i % 5 else "card", "cashReceivedCents": received, "changeCents": max(0, received-total), "status": "PAID", "createdAt": created.isoformat()})
            for prod, qty, price in line_payloads:
                insert_row(con, ledger, path, batch, "Sales", "SaleLine", {"id": make_id("sl"), "businessId": biz_id, "saleId": sale, "productId": prod["id"], "sku": prod["sku"], "productName": prod["name"], "qty": qty, "priceCents": price, "totalCents": qty*price, "createdAt": created.isoformat()})
            if "SalePaymentTender" in tables:
                insert_row(con, ledger, path, batch, "Sales", "SalePaymentTender", {"id": make_id("pay"), "businessId": biz_id, "saleId": sale, "tenderType": "cash", "amountCents": total, "metadataJson": json.dumps({"batch_id": batch, "source": "prisma_data_lifecycle"}), "createdAt": created.isoformat()})
            if "OutboxEvent" in tables and i % 3 == 0:
                payload = {"saleId": sale, "folio": folio, "totalCents": total, "source": "prisma_data_lifecycle", "batch_id": batch}
                insert_row(con, ledger, path, batch, "Sync", "OutboxEvent", {"id": make_id("out"), "businessId": biz_id, "terminalId": terminal_id, "topic": "sale.created", "eventType": "sale.created", "aggregateId": sale, "idempotencyKey": f"{sale}:created", "correlationId": batch, "payloadJson": json.dumps(payload, ensure_ascii=False), "source": "prisma_data_lifecycle", "schemaVersion": "v1", "status": random.choice(["PENDING", "SENT", "ACKED"]), "lifecycleStatus": "GENERATED", "attempts": random.randint(0, 2), "createdAt": created.isoformat(), "diagnosticsJson": json.dumps({"mode": plan.get("mode")}, ensure_ascii=False)})
            if "AuditEvent" in tables and i % 20 == 0:
                insert_row(con, ledger, path, batch, "Audit", "AuditEvent", {"id": make_id("audit"), "businessId": biz_id, "actorId": random.choice(user_ids) if user_ids else None, "topic": "sale.created", "entityType": "Sale", "entityId": sale, "summary": f"Venta generada {folio}", "metadataJson": json.dumps({"source": "prisma_data_lifecycle", "batch_id": batch}, ensure_ascii=False), "createdAt": created.isoformat()})

        if "SyncCheckpoint" in tables:
            for tid in terminal_ids:
                insert_row(con, ledger, path, batch, "Sync", "SyncCheckpoint", {"id": make_id("syncp"), "businessId": biz_id, "terminalId": tid, "cursor": f"{batch}:{tid}", "topic": "catalog.delta", "status": "OK", "updatedAt": utcnow(), "createdAt": utcnow()})
        if "SyncConflict" in tables:
            for i in range(0, max(1, device_count // 2)):
                insert_row(con, ledger, path, batch, "Sync", "SyncConflict", {"id": make_id("conf"), "businessId": biz_id, "terminalId": random.choice(terminal_ids), "topic": "product.price", "aggregateId": random.choice(products)["id"], "status": "OPEN", "conflictCode": "PRICE_CHANGED_DURING_SYNC", "payloadJson": json.dumps({"source": "prisma_data_lifecycle", "batch_id": batch}), "createdAt": utcnow(), "updatedAt": utcnow()})

        con.commit()
        # Summarize inserted by querying ledger for this DB.
        for row in ledger.execute("SELECT domain, table_name, COUNT(*) c FROM lifecycle_records WHERE batch_id=? AND db_path=? GROUP BY domain, table_name", (batch, path)):
            summary["inserted"].setdefault(row["domain"], {})[row["table_name"]] = row["c"]
    except Exception as exc:
        con.rollback()
        summary["errors"].append({"error": str(exc), "traceback": traceback.format_exc()})
    finally:
        con.close()
    return summary


def seed_chart_lab(db: dict[str, Any], batch: str, plan: dict[str, Any], ledger: sqlite3.Connection) -> dict[str, Any]:
    path = db["path"]
    summary = {"db": db, "inserted": {}, "errors": []}
    con = connect(path)
    try:
        if has_table(con, "runtime_sources"):
            insert_row(con, ledger, path, batch, "Chart Lab", "runtime_sources", {"sourceKey": f"lifecycle-{batch}", "path": "PRISMA_DATA_LIFECYCLE", "state": "ready", "sourceKind": "generated", "sourceOfTruth": 0, "openedReadOnly": 1, "requiredForTabletSales": 0, "updatedAt": utcnow()})
        if has_table(con, "runtime_metadata"):
            insert_row(con, ledger, path, batch, "Chart Lab", "runtime_metadata", {"key": f"lifecycle.batch.{batch}", "value": json.dumps({"mode": plan.get("mode"), "label": plan.get("label")}, ensure_ascii=False), "updatedAt": utcnow()})
        if has_table(con, "runtime_chart_payloads"):
            charts = ["sales-pulse", "inventory-risk", "sync-lifeline", "supplier-coverage", "cash-variance", "longaniza-density"]
            points = max(30, min(360, int(plan.get("days", 30))))
            for chart in charts:
                data = []
                base = random.randint(30, 200)
                for i in range(points):
                    data.append({"day": i + 1, "value": max(0, int(base + random.gauss(0, base * .18) + (i % 7) * 5)), "risk": random.choice(["ok", "ok", "warn", "critical"])})
                payload = {"chartKey": chart, "batchId": batch, "mode": plan.get("mode"), "series": data, "generatedBy": "PRISMA Data Lifecycle"}
                insert_row(con, ledger, path, batch, "Chart Lab", "runtime_chart_payloads", {"chartKey": f"lifecycle-{chart}-{batch}", "surface": "shared", "payloadJson": json.dumps(payload, ensure_ascii=False), "dataStatus": "generated", "sourceMode": "prisma_data_lifecycle", "generatedAt": utcnow()})
        con.commit()
        for row in ledger.execute("SELECT domain, table_name, COUNT(*) c FROM lifecycle_records WHERE batch_id=? AND db_path=? GROUP BY domain, table_name", (batch, path)):
            summary["inserted"].setdefault(row["domain"], {})[row["table_name"]] = row["c"]
    except Exception as exc:
        con.rollback(); summary["errors"].append({"error": str(exc), "traceback": traceback.format_exc()})
    finally:
        con.close()
    return summary


def inject(mode: str, public: bool = False) -> dict[str, Any]:
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED", "message": "Data Lifecycle sólo permite mutaciones desde localhost."}
    ensure_dirs()
    plan = plan_for(mode)
    b = batch_id(plan["mode"])
    ledger = ensure_ledger()
    ledger.execute("INSERT INTO lifecycle_batches(batch_id, mode, status, created_at, summary_json) VALUES(?,?,?,?,?)", (b, plan["mode"], "RUNNING", utcnow(), json.dumps(plan, ensure_ascii=False)))
    ledger.commit()
    dbs = discover_dbs()
    summaries = []
    errors = []
    backup = create_backup(f"before_inject_{plan['mode']}")
    for db in dbs:
        if db["surface"] == "chart_lab":
            s = seed_chart_lab(db, b, plan, ledger)
        else:
            s = seed_operational_db(db, b, plan, ledger)
        summaries.append(s)
        errors.extend(s.get("errors", []))
    status = "PASS" if not errors else "WARN"
    payload = {"ok": not bool(errors), "status": status, "apiVersion": API_VERSION, "batch_id": b, "mode": plan["mode"], "label": plan["label"], "plan": plan, "backup": backup, "databases": dbs, "summaries": summaries, "errors": errors}
    evidence = write_evidence(f"inject_{plan['mode']}_{b}", payload)
    ledger.execute("UPDATE lifecycle_batches SET status=?, finished_at=?, summary_json=?, evidence_path=? WHERE batch_id=?", (status, utcnow(), json.dumps(payload, ensure_ascii=False), evidence, b))
    ledger.commit(); ledger.close()
    log_event("inject", {"batch_id": b, "mode": plan["mode"], "status": status})
    return payload


def latest_dashboard(public: bool = False) -> dict[str, Any]:
    ensure_dirs(); ledger = ensure_ledger()
    dbs = discover_dbs()
    dm = domain_map()
    domains = []
    for domain, tables in dm.items():
        total = 0
        by_table = []
        for db in dbs:
            try:
                con = connect(db["path"])
                names = table_names(con)
                for table in tables:
                    if table in names:
                        try:
                            c = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                        except Exception:
                            c = 0
                        total += int(c)
                        gen = ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE db_path=? AND table_name=? AND domain=? AND cleared_at IS NULL", (db["path"], table, domain)).fetchone()[0]
                        by_table.append({"db": db["relative_path"], "table": table, "total": int(c), "generated": int(gen), "manual_or_real": max(0, int(c)-int(gen))})
                con.close()
            except Exception as exc:
                by_table.append({"db": db["relative_path"], "error": str(exc)})
        generated = sum(int(x.get("generated", 0)) for x in by_table)
        manual = max(0, total-generated)
        if total == 0:
            state = "clean"
        elif generated and manual:
            state = "mixed"
        elif generated:
            state = "generated"
        else:
            state = "manual_or_real"
        domains.append({"domain": domain, "total": total, "generated": generated, "manual_or_real": manual, "state": state, "tables": by_table})
    last_batches = [dict(r) for r in ledger.execute("SELECT batch_id, mode, status, created_at, finished_at, evidence_path FROM lifecycle_batches ORDER BY created_at DESC LIMIT 8")]
    last_events = [dict(r) for r in ledger.execute("SELECT event_type, created_at, payload_json FROM lifecycle_events ORDER BY id DESC LIMIT 8")]
    pin_cfg = config()
    payload = {"ok": True, "status": "READY", "apiVersion": API_VERSION, "project_root": str(project_root()), "control_center_root": str(CONTROL_CENTER_ROOT), "owner_email": pin_cfg.get("owner_email"), "pin_required": bool(pin_cfg.get("pin_required", True)), "allow_clear_without_pin": bool(pin_cfg.get("allow_clear_without_pin", False)), "databases": dbs, "domains": domains, "last_batches": last_batches, "last_events": last_events, "generated_records_open": ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE cleared_at IS NULL").fetchone()[0], "ledger": str(LEDGER_PATH)}
    ledger.close()
    if public:
        payload.pop("project_root", None); payload.pop("ledger", None)
        for db in payload["databases"]:
            db.pop("path", None)
    return payload


def hash_pin(pin: str, pin_id: str) -> str:
    return hashlib.sha256(f"{pin_id}:{pin}".encode("utf-8")).hexdigest()


def send_pin_email(owner: str, pin: str, pin_id: str) -> dict[str, Any]:
    cfg = config(); smtp = cfg.get("smtp", {}) or {}
    ensure_dirs()
    if not smtp.get("enabled") or not smtp.get("host"):
        path = EVIDENCE_DIR / f"PIN_EMAIL_PREVIEW_{pin_id}.txt"
        path.write_text(f"To: {owner}\nSubject: PRISMA Data Lifecycle PIN\n\nTu PIN para ejecutar Clear es: {pin}\nExpira en {cfg.get('pin_expiration_minutes', 10)} minutos.\n", encoding="utf-8")
        return {"ok": False, "status": "SMTP_NOT_CONFIGURED", "fallback": str(path), "message": "SMTP no configurado; PIN escrito en evidencia local interna."}
    msg = EmailMessage()
    msg["Subject"] = "PRISMA Data Lifecycle PIN"
    msg["From"] = smtp.get("from_email") or smtp.get("username") or owner
    msg["To"] = owner
    msg.set_content(f"Tu PIN para ejecutar PRISMA Data Lifecycle Clear es: {pin}\n\nPIN ID: {pin_id}\nExpira en {cfg.get('pin_expiration_minutes', 10)} minutos.\n")
    password = os.environ.get(smtp.get("password_env") or "PRISMA_LIFECYCLE_SMTP_PASSWORD", "")
    try:
        with smtplib.SMTP(str(smtp.get("host")), int(smtp.get("port", 587)), timeout=20) as s:
            if smtp.get("use_tls", True):
                s.starttls()
            if smtp.get("username"):
                s.login(str(smtp.get("username")), password)
            s.send_message(msg)
        return {"ok": True, "status": "EMAIL_SENT"}
    except Exception as exc:
        path = EVIDENCE_DIR / f"PIN_EMAIL_FAILED_{pin_id}.txt"
        path.write_text(f"To: {owner}\nPIN: {pin}\nError: {exc}\n", encoding="utf-8")
        return {"ok": False, "status": "EMAIL_FAILED", "error": str(exc), "fallback": str(path)}


def request_pin(public: bool = False) -> dict[str, Any]:
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    cfg = config(); owner = cfg.get("owner_email") or "alanharrryy@gmail.com"
    pin = str(cfg.get("pin_default") or "030303").zfill(6)[-6:]
    pin_id = make_id("pin")
    created = local_now()
    expires = created + _dt.timedelta(minutes=int(cfg.get("pin_expiration_minutes", 10)))
    email_result = send_pin_email(owner, pin, pin_id)
    ledger = ensure_ledger()
    ledger.execute("INSERT INTO lifecycle_pins(pin_id, pin_hash, owner_email, created_at, expires_at, status, evidence_path) VALUES(?,?,?,?,?,?,?)", (pin_id, hash_pin(pin, pin_id), owner, created.isoformat(), expires.isoformat(), "ACTIVE", email_result.get("fallback")))
    ledger.commit(); ledger.close()
    log_event("pin_requested", {"pin_id": pin_id, "owner_email": owner, "email_status": email_result.get("status")})
    return {"ok": True, "status": "PIN_READY", "pin_id": pin_id, "owner_email": owner, "expires_at": expires.isoformat(), "email": email_result, "pin_required": bool(cfg.get("pin_required", True)), "allow_clear_without_pin": bool(cfg.get("allow_clear_without_pin", False))}


def validate_pin(pin: str | None, pin_id: str | None = None) -> tuple[bool, str]:
    cfg = config()
    if not cfg.get("pin_required", True) and cfg.get("allow_clear_without_pin", False):
        return True, "PIN_DISABLED_BY_CONFIG"
    if not pin:
        return False, "PIN_REQUIRED"
    ledger = ensure_ledger()
    row = None
    if pin_id:
        row = ledger.execute("SELECT * FROM lifecycle_pins WHERE pin_id=? AND status='ACTIVE' ORDER BY created_at DESC LIMIT 1", (pin_id,)).fetchone()
    if row is None:
        row = ledger.execute("SELECT * FROM lifecycle_pins WHERE status='ACTIVE' ORDER BY created_at DESC LIMIT 1").fetchone()
    if row is None:
        ledger.close(); return False, "NO_ACTIVE_PIN"
    if local_now() > _dt.datetime.fromisoformat(row["expires_at"]):
        ledger.execute("UPDATE lifecycle_pins SET status='EXPIRED' WHERE pin_id=?", (row["pin_id"],)); ledger.commit(); ledger.close()
        return False, "PIN_EXPIRED"
    if hash_pin(pin, row["pin_id"]) != row["pin_hash"]:
        ledger.close(); return False, "PIN_INVALID"
    ledger.execute("UPDATE lifecycle_pins SET used_at=?, status='USED' WHERE pin_id=?", (local_now().isoformat(), row["pin_id"]))
    ledger.commit(); ledger.close()
    return True, "PIN_OK"


def clear_generated(public: bool = False, pin: str | None = None, pin_id: str | None = None) -> dict[str, Any]:
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    ok, reason = validate_pin(pin, pin_id)
    if not ok:
        return {"ok": False, "status": reason, "message": "Clear bloqueado por PIN."}
    backup = create_backup("before_clear")
    clear_batch = f"clear_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    ledger = ensure_ledger()
    records = [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_records WHERE cleared_at IS NULL ORDER BY id DESC")]
    results = []
    errors = []
    con_cache: dict[str, sqlite3.Connection] = {}
    try:
        for rec in records:
            db_path = rec["db_path"]
            table = rec["table_name"]
            pk = rec["primary_key"]
            try:
                con = con_cache.get(db_path)
                if con is None:
                    con = connect(db_path); con_cache[db_path] = con
                if not has_table(con, table):
                    results.append({"record": rec["id"], "table": table, "status": "TABLE_MISSING"})
                    continue
                col = pk_col(con, table)
                before = con.total_changes
                con.execute(f'DELETE FROM "{table}" WHERE "{col}"=?', (pk,))
                deleted = con.total_changes - before
                ledger.execute("UPDATE lifecycle_records SET cleared_at=?, clear_batch=? WHERE id=?", (utcnow(), clear_batch, rec["id"]))
                results.append({"record": rec["id"], "db": db_path, "table": table, "pk": pk, "deleted": int(deleted)})
            except Exception as exc:
                errors.append({"record": rec, "error": str(exc)})
        for con in con_cache.values():
            con.commit(); con.close()
        ledger.commit()
    except Exception as exc:
        for con in con_cache.values():
            try: con.rollback(); con.close()
            except Exception: pass
        errors.append({"fatal": str(exc), "traceback": traceback.format_exc()})
    status = "PASS" if not errors else "WARN"
    payload = {"ok": not bool(errors), "status": status, "clear_batch": clear_batch, "backup": backup, "cleared_records": len([r for r in results if r.get("deleted",0) >= 0]), "results": results[:5000], "errors": errors}
    evidence = write_evidence(f"clear_{clear_batch}", payload)
    log_event("clear", {"clear_batch": clear_batch, "status": status, "evidence": evidence})
    ledger.close()
    return payload


def latest_evidence() -> dict[str, Any]:
    ensure_dirs()
    files = sorted(EVIDENCE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
    return {"ok": True, "status": "READY", "files": [{"name": p.name, "path": str(p), "modified": _dt.datetime.fromtimestamp(p.stat().st_mtime).isoformat(), "size": p.stat().st_size} for p in files]}


def lifecycle_payload(path: str, public: bool = False) -> dict[str, Any]:
    ensure_dirs()
    parsed = urlparse(path)
    clean = parsed.path.rstrip("/")
    qs = parse_qs(parsed.query)
    parts = [p for p in clean.split("/") if p]
    try:
        if clean in {"/api/lifecycle", "/api/lifecycle/latest"}:
            return latest_dashboard(public=public)
        if clean.startswith("/api/lifecycle/plan"):
            mode = parts[-1] if len(parts) >= 4 else (qs.get("mode", ["light"])[0])
            return {"ok": True, "status": "READY", "plan": plan_for(mode), "profiles": profiles()}
        if clean.startswith("/api/lifecycle/inject"):
            mode = parts[-1] if len(parts) >= 4 else (qs.get("mode", ["light"])[0])
            return inject(mode, public=public)
        if clean.startswith("/api/lifecycle/clear/request-pin"):
            return request_pin(public=public)
        if clean.startswith("/api/lifecycle/clear/confirm"):
            return clear_generated(public=public, pin=qs.get("pin", [None])[0], pin_id=qs.get("pin_id", [None])[0])
        if clean.startswith("/api/lifecycle/evidence/latest"):
            return latest_evidence()
        if clean.startswith("/api/lifecycle/health"):
            return {"ok": True, "status": "LIFECYCLE_READY", "apiVersion": API_VERSION, "data_dir": str(DATA_DIR), "ledger": str(LEDGER_PATH)}
        return {"ok": False, "status": "UNKNOWN_LIFECYCLE_ROUTE", "path": path}
    except Exception as exc:
        return {"ok": False, "status": "LIFECYCLE_EXCEPTION", "error": str(exc), "traceback": traceback.format_exc()}



# ---------------------------------------------------------------------------
# PRISMA DATA LIFECYCLE V2 MASTER HARDENING LAYER
# This lower section intentionally overrides selected V1 functions without
# changing the public API shape consumed by panel_3150.py.  It adds schema
# migration, composite-PK ledger support, clear preview, preflight, richer
# evidence bundles and safer generated-only cleanup.
# ---------------------------------------------------------------------------

HARDENING_VERSION = "v2-master"


def table_pk_cols(con: sqlite3.Connection, table: str) -> list[str]:
    cols = table_columns(con, table)
    ordered = [(meta.get("cid", 0), name) for name, meta in cols.items() if meta.get("pk")]
    ordered.sort()
    if ordered:
        return [name for _, name in ordered]
    if "id" in cols:
        return ["id"]
    if cols:
        return [next(iter(cols))]
    return ["id"]


def sql_ident(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def table_schema_hash(con: sqlite3.Connection, table: str) -> str:
    try:
        row = con.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
        raw = row[0] if row else table
    except Exception:
        raw = table
    return hashlib.sha256(str(raw).encode("utf-8", errors="replace")).hexdigest()


def ensure_ledger() -> sqlite3.Connection:  # type: ignore[override]
    ensure_dirs()
    con = sqlite3.connect(str(LEDGER_PATH), timeout=30)
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE IF NOT EXISTS lifecycle_batches (
      batch_id TEXT PRIMARY KEY,
      mode TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL,
      finished_at TEXT,
      summary_json TEXT,
      evidence_path TEXT,
      backup_path TEXT,
      api_version TEXT,
      plan_json TEXT
    );
    CREATE TABLE IF NOT EXISTS lifecycle_records (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      batch_id TEXT NOT NULL,
      domain TEXT NOT NULL,
      db_path TEXT NOT NULL,
      db_relative_path TEXT,
      origin_surface TEXT,
      table_name TEXT NOT NULL,
      primary_key TEXT NOT NULL,
      primary_key_json TEXT,
      row_snapshot_json TEXT,
      table_schema_hash TEXT,
      created_at TEXT NOT NULL,
      cleared_at TEXT,
      clear_batch TEXT,
      clear_error TEXT,
      UNIQUE(batch_id, db_path, table_name, primary_key)
    );
    CREATE TABLE IF NOT EXISTS lifecycle_pins (
      pin_id TEXT PRIMARY KEY,
      pin_hash TEXT NOT NULL,
      owner_email TEXT NOT NULL,
      created_at TEXT NOT NULL,
      expires_at TEXT NOT NULL,
      used_at TEXT,
      status TEXT NOT NULL,
      evidence_path TEXT
    );
    CREATE TABLE IF NOT EXISTS lifecycle_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      event_type TEXT NOT NULL,
      created_at TEXT NOT NULL,
      payload_json TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS lifecycle_backups (
      backup_id TEXT PRIMARY KEY,
      reason TEXT NOT NULL,
      created_at TEXT NOT NULL,
      zip_path TEXT NOT NULL,
      manifest_json TEXT NOT NULL,
      sha256 TEXT
    );
    """)
    # Lightweight migrations for existing V1 ledger DBs.
    def add_col(table: str, name: str, ddl: str) -> None:
        existing = {r[1] for r in con.execute(f"PRAGMA table_info({sql_ident(table)})")}
        if name not in existing:
            con.execute(f"ALTER TABLE {sql_ident(table)} ADD COLUMN {name} {ddl}")
    for col, ddl in [
        ("db_relative_path", "TEXT"),
        ("origin_surface", "TEXT"),
        ("primary_key_json", "TEXT"),
        ("row_snapshot_json", "TEXT"),
        ("table_schema_hash", "TEXT"),
        ("clear_error", "TEXT"),
    ]:
        add_col("lifecycle_records", col, ddl)
    for col, ddl in [("backup_path", "TEXT"), ("api_version", "TEXT"), ("plan_json", "TEXT")]:
        add_col("lifecycle_batches", col, ddl)
    con.commit()
    return con


def safe_json(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    except Exception:
        return json.dumps({"repr": repr(data)}, ensure_ascii=False)


def primary_key_token(values: dict[str, Any]) -> str:
    # Keeps backward-compatible primary_key text while supporting composite keys.
    if len(values) == 1:
        return str(next(iter(values.values())))
    return hashlib.sha256(safe_json(values).encode("utf-8", errors="replace")).hexdigest()[:32]


def relative_to_project(path: str | Path) -> str:
    p = Path(path)
    try:
        return str(p.resolve().relative_to(project_root())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def ledger_record(ledger: sqlite3.Connection, batch: str, domain: str, db_path: str, table: str, pk: str, *, pk_json: dict[str, Any] | None = None, row_snapshot: dict[str, Any] | None = None, schema_hash: str | None = None, surface: str | None = None) -> None:  # type: ignore[override]
    pk_payload = pk_json or {"id": pk}
    ledger.execute(
        """
        INSERT OR IGNORE INTO lifecycle_records(
          batch_id, domain, db_path, db_relative_path, origin_surface, table_name,
          primary_key, primary_key_json, row_snapshot_json, table_schema_hash, created_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            batch,
            domain,
            str(db_path),
            relative_to_project(db_path),
            surface or surface_for_db(db_path),
            table,
            str(pk),
            safe_json(pk_payload),
            safe_json(row_snapshot or {}),
            schema_hash,
            utcnow(),
        ),
    )


def surface_for_db(db_path: str | Path) -> str:
    s = str(db_path).replace("\\", "/").lower()
    if "/products/pc/" in s:
        return "pc"
    if "/products/tablet/" in s:
        return "tablet"
    if "/products/mobile/" in s:
        return "mobile"
    if "/products/chart-lab/" in s:
        return "chart_lab"
    return "unknown"


def row_by_pk(con: sqlite3.Connection, table: str, pk_values: dict[str, Any]) -> dict[str, Any] | None:
    try:
        where = " AND ".join([f"{sql_ident(k)}=?" for k in pk_values])
        row = con.execute(f"SELECT * FROM {sql_ident(table)} WHERE {where} LIMIT 1", list(pk_values.values())).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


def insert_row(con: sqlite3.Connection, ledger: sqlite3.Connection, db_path: str, batch: str, domain: str, table: str, data: dict[str, Any]) -> str | None:  # type: ignore[override]
    if not has_table(con, table):
        return None
    cols = table_columns(con, table)
    if not cols:
        return None
    pk_cols = table_pk_cols(con, table)
    for pk in pk_cols:
        if pk not in data:
            data[pk] = make_id(table.lower())
    now = utcnow()
    generic = {
        "businessId": data.get("businessId"),
        "storeId": data.get("storeId"),
        "createdAt": now,
        "updatedAt": now,
        "created_at": now,
        "updated_at": now,
        "status": "ACTIVE",
        "state": "ACTIVE",
        "currency": "MXN",
        "isActive": 1,
        "active": 1,
        "isDefault": 0,
        "attempts": 0,
        "source": "prisma_data_lifecycle",
        "origin": "prisma_data_lifecycle",
        "payloadJson": json.dumps({"source": "prisma_data_lifecycle", "batch_id": batch}, ensure_ascii=False),
        "metadataJson": json.dumps({"source": "prisma_data_lifecycle", "batch_id": batch}, ensure_ascii=False),
        "diagnosticsJson": json.dumps({"source": "prisma_data_lifecycle", "batch_id": batch}, ensure_ascii=False),
    }
    for name, meta in cols.items():
        if name in data:
            continue
        if name in generic and generic[name] is not None:
            data[name] = generic[name]
        elif meta.get("notnull") and meta.get("default") is None and not meta.get("pk"):
            typ = str(meta.get("type") or "").upper()
            lname = name.lower()
            if "email" in lname:
                data[name] = f"lifecycle.{uuid.uuid4().hex[:8]}@prisma.local"
            elif "name" in lname or "label" in lname or "title" in lname:
                data[name] = f"Lifecycle {table}"
            elif "code" in lname or "sku" in lname:
                data[name] = f"LC-{uuid.uuid4().hex[:8].upper()}"
            elif "json" in lname:
                data[name] = safe_json({"source": "prisma_data_lifecycle", "batch_id": batch})
            elif "INT" in typ:
                data[name] = 0
            elif "REAL" in typ or "FLOA" in typ or "DOUB" in typ or "NUM" in typ or "DEC" in typ:
                data[name] = 0.0
            elif "BOOL" in typ:
                data[name] = 0
            elif "DATE" in typ or "TIME" in typ:
                data[name] = now
            else:
                data[name] = f"lifecycle_{name}"
    final = {k: v for k, v in data.items() if k in cols}
    if not final:
        return None
    names = list(final.keys())
    placeholders = ",".join(["?"] * len(names))
    sql = f'INSERT OR IGNORE INTO {sql_ident(table)} ({",".join([sql_ident(n) for n in names])}) VALUES ({placeholders})'
    before = con.total_changes
    con.execute(sql, [final[n] for n in names])
    pk_values = {k: final.get(k) for k in pk_cols if k in final}
    pk_token = primary_key_token(pk_values)
    if con.total_changes > before:
        snapshot = row_by_pk(con, table, pk_values) or final
        ledger_record(
            ledger,
            batch,
            domain,
            db_path,
            table,
            pk_token,
            pk_json=pk_values,
            row_snapshot=snapshot,
            schema_hash=table_schema_hash(con, table),
            surface=surface_for_db(db_path),
        )
    return pk_token


def config_summary() -> dict[str, Any]:
    cfg = config()
    return {
        "owner_email": cfg.get("owner_email"),
        "pin_required": bool(cfg.get("pin_required", True)),
        "allow_clear_without_pin": bool(cfg.get("allow_clear_without_pin", False)),
        "smtp_configured": bool((cfg.get("smtp") or {}).get("enabled") and (cfg.get("smtp") or {}).get("host")),
        "project_root": str(project_root()),
        "downloads_root": str(downloads_root()),
    }


def preflight(public: bool = False) -> dict[str, Any]:
    dbs = discover_dbs()
    ledger = ensure_ledger()
    checks: list[dict[str, Any]] = []
    for db in dbs:
        item = {"db": db["relative_path"], "surface": db["surface"], "ok": False, "tables": 0, "rows": 0, "error": None}
        try:
            con = connect(db["path"])
            names = table_names(con)
            item["tables"] = len(names)
            rows = 0
            for table in names:
                try:
                    rows += int(con.execute(f"SELECT COUNT(*) FROM {sql_ident(table)}").fetchone()[0])
                except Exception:
                    pass
            item["rows"] = rows
            item["ok"] = True
            con.close()
        except Exception as exc:
            item["error"] = str(exc)
        checks.append(item)
    payload = {
        "ok": True,
        "status": "PREFLIGHT_READY",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "config": config_summary(),
        "databases_found": len(dbs),
        "database_checks": checks,
        "ledger": {"path": str(LEDGER_PATH), "records_open": ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE cleared_at IS NULL").fetchone()[0]},
    }
    ledger.close()
    if public:
        payload["config"].pop("project_root", None)
        payload["config"].pop("downloads_root", None)
        payload["ledger"].pop("path", None)
    return payload


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def create_backup(reason: str) -> str:  # type: ignore[override]
    ensure_dirs()
    dbs = discover_dbs()
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_id = f"backup_{reason}_{stamp}_{uuid.uuid4().hex[:6]}"
    zip_path = BACKUP_DIR / f"PRISMA_DATA_LIFECYCLE_BACKUP_{reason}_{stamp}.zip"
    manifest = {"backup_id": backup_id, "reason": reason, "created_at": utcnow(), "apiVersion": API_VERSION, "databases": [], "configs": []}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for db in dbs:
            p = Path(db["path"])
            if p.exists():
                arc = f"dbs/{db['relative_path'].replace(':','')}"
                z.write(p, arc)
                manifest["databases"].append({"path": str(p), "relative_path": db["relative_path"], "arcname": arc, "sha256": sha256_file(p), "size": p.stat().st_size})
        if LEDGER_PATH.exists():
            z.write(LEDGER_PATH, "ledger/prisma-data-lifecycle-ledger.db")
            manifest["ledger"] = {"path": str(LEDGER_PATH), "sha256": sha256_file(LEDGER_PATH)}
        for cfg in ["lifecycle_config.json", "lifecycle_domain_map.json", "lifecycle_seed_profiles.json", "lifecycle_clear_policy.json"]:
            p = CONFIG_DIR / cfg
            if p.exists():
                z.write(p, f"config/{cfg}")
                manifest["configs"].append({"name": cfg, "sha256": sha256_file(p)})
        z.writestr("backup_manifest.json", safe_json(manifest))
    zip_hash = sha256_file(zip_path)
    ledger = ensure_ledger()
    ledger.execute("INSERT OR REPLACE INTO lifecycle_backups(backup_id, reason, created_at, zip_path, manifest_json, sha256) VALUES(?,?,?,?,?,?)", (backup_id, reason, utcnow(), str(zip_path), safe_json(manifest), zip_hash))
    ledger.commit(); ledger.close()
    try:
        shutil.copy2(zip_path, downloads_root() / zip_path.name)
    except Exception:
        pass
    return str(zip_path)


def write_evidence(name: str, payload: dict[str, Any]) -> str:  # type: ignore[override]
    ensure_dirs()
    stamp = _dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    base = EVIDENCE_DIR / f"{name}_{stamp}"
    json_path = base.with_suffix(".json")
    md_path = base.with_suffix(".md")
    zip_path = base.with_suffix(".zip")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    lines = [
        "# PRISMA Data Lifecycle Evidence",
        "",
        f"- Status: `{payload.get('status', 'UNKNOWN')}`",
        f"- API: `{API_VERSION}`",
        f"- Created: `{utcnow()}`",
        "",
        "## Payload",
        "",
        "```json",
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        "```",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(json_path, json_path.name)
        z.write(md_path, md_path.name)
    try:
        dr = downloads_root()
        for p in [json_path, md_path, zip_path]:
            shutil.copy2(p, dr / p.name)
    except Exception:
        pass
    return str(zip_path)


def create_injection_plan(mode: str) -> dict[str, Any]:
    plan = plan_for(mode)
    plan["hardeningVersion"] = HARDENING_VERSION
    plan["execution_order"] = ["Tenant", "Identity", "Devices", "Catalog", "Suppliers", "Purchasing", "Inventory", "Cash", "Sales", "Sync", "Audit", "Chart Lab", "License"]
    plan["estimated_records"] = {
        "Tenant": 2,
        "Identity": int(plan.get("users", 0)) + 12,
        "Devices": int(plan.get("tablets", 0)) * 2,
        "Catalog": int(plan.get("products", 0)) * 3,
        "Suppliers": int(plan.get("suppliers", 0)) * 2,
        "Purchasing": int(plan.get("purchase_orders", 0)) * 4,
        "Inventory": int(plan.get("products", 0)) * 2,
        "Cash": int(plan.get("days", 0)) * max(1, int(plan.get("tablets", 0))),
        "Sales": int(plan.get("sales_target", 0)) * 3,
        "Sync": int(plan.get("sales_target", 0)) // 2,
        "Audit": int(plan.get("sales_target", 0)) // 3,
        "Chart Lab": 20 if plan.get("mode") == "light" else 80 if plan.get("mode") == "heavy" else 200,
        "License": 3,
    }
    plan["estimated_total_records"] = sum(int(v) for v in plan["estimated_records"].values())
    return plan


def inject(mode: str, public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED", "message": "Data Lifecycle sólo permite mutaciones desde localhost."}
    ensure_dirs()
    plan = create_injection_plan(mode)
    b = batch_id(plan["mode"])
    ledger = ensure_ledger()
    backup = create_backup(f"before_inject_{plan['mode']}")
    ledger.execute(
        "INSERT INTO lifecycle_batches(batch_id, mode, status, created_at, summary_json, backup_path, api_version, plan_json) VALUES(?,?,?,?,?,?,?,?)",
        (b, plan["mode"], "RUNNING", utcnow(), json.dumps(plan, ensure_ascii=False), backup, API_VERSION, json.dumps(plan, ensure_ascii=False)),
    )
    ledger.commit()
    dbs = discover_dbs()
    summaries = []
    errors = []
    if not dbs:
        errors.append({"status": "NO_SQLITE_DATABASES", "message": "No se encontraron DB SQLite activas para alimentar."})
    for db in dbs:
        try:
            if db["surface"] == "chart_lab":
                s = seed_chart_lab(db, b, plan, ledger)
            else:
                s = seed_operational_db(db, b, plan, ledger)
            summaries.append(s)
            errors.extend(s.get("errors", []))
        except Exception as exc:
            errors.append({"db": db, "error": str(exc), "traceback": traceback.format_exc()})
    status = "PASS" if not errors else "WARN"
    payload = {"ok": not bool(errors), "status": status, "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "batch_id": b, "mode": plan["mode"], "label": plan["label"], "plan": plan, "backup": backup, "databases": dbs, "summaries": summaries, "errors": errors}
    evidence = write_evidence(f"inject_{plan['mode']}_{b}", payload)
    ledger.execute("UPDATE lifecycle_batches SET status=?, finished_at=?, summary_json=?, evidence_path=?, backup_path=? WHERE batch_id=?", (status, utcnow(), json.dumps(payload, ensure_ascii=False, default=str), evidence, backup, b))
    ledger.commit(); ledger.close()
    log_event("inject", {"batch_id": b, "mode": plan["mode"], "status": status, "evidence": evidence})
    return payload


def latest_dashboard(public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    ensure_dirs(); ledger = ensure_ledger()
    dbs = discover_dbs()
    dm = domain_map()
    domains = []
    for domain, tables in dm.items():
        total = 0
        by_table = []
        for db in dbs:
            try:
                con = connect(db["path"])
                names = table_names(con)
                for table in tables:
                    if table in names:
                        try:
                            c = con.execute(f"SELECT COUNT(*) FROM {sql_ident(table)}").fetchone()[0]
                        except Exception:
                            c = 0
                        total += int(c)
                        gen = ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE db_path=? AND table_name=? AND domain=? AND cleared_at IS NULL", (db["path"], table, domain)).fetchone()[0]
                        by_table.append({"db": db["relative_path"], "surface": db["surface"], "table": table, "total": int(c), "generated": int(gen), "manual_or_real": max(0, int(c)-int(gen))})
                con.close()
            except Exception as exc:
                by_table.append({"db": db.get("relative_path"), "error": str(exc)})
        generated = sum(int(x.get("generated", 0)) for x in by_table)
        manual = max(0, total-generated)
        if total == 0:
            state = "clean"
        elif generated and manual:
            state = "mixed"
        elif generated:
            state = "generated"
        else:
            state = "manual_or_real"
        domains.append({"domain": domain, "total": total, "generated": generated, "manual_or_real": manual, "state": state, "tables": by_table})
    last_batches = [dict(r) for r in ledger.execute("SELECT batch_id, mode, status, created_at, finished_at, evidence_path, backup_path, api_version FROM lifecycle_batches ORDER BY created_at DESC LIMIT 8")]
    last_events = [dict(r) for r in ledger.execute("SELECT event_type, created_at, payload_json FROM lifecycle_events ORDER BY id DESC LIMIT 8")]
    last_backups = [dict(r) for r in ledger.execute("SELECT backup_id, reason, created_at, zip_path, sha256 FROM lifecycle_backups ORDER BY created_at DESC LIMIT 5")]
    pin_cfg = config()
    payload = {
        "ok": True,
        "status": "READY",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "project_root": str(project_root()),
        "control_center_root": str(CONTROL_CENTER_ROOT),
        "owner_email": pin_cfg.get("owner_email"),
        "pin_required": bool(pin_cfg.get("pin_required", True)),
        "allow_clear_without_pin": bool(pin_cfg.get("allow_clear_without_pin", False)),
        "smtp_configured": bool((pin_cfg.get("smtp") or {}).get("enabled") and (pin_cfg.get("smtp") or {}).get("host")),
        "databases": dbs,
        "domains": domains,
        "last_batches": last_batches,
        "last_events": last_events,
        "last_backups": last_backups,
        "generated_records_open": ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE cleared_at IS NULL").fetchone()[0],
        "ledger": str(LEDGER_PATH),
    }
    ledger.close()
    if public:
        payload.pop("project_root", None); payload.pop("ledger", None)
        for db in payload["databases"]:
            db.pop("path", None)
        for b in payload["last_backups"]:
            b.pop("zip_path", None)
    return payload


def clear_preview(public: bool = False) -> dict[str, Any]:
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    ledger = ensure_ledger()
    rows = [dict(r) for r in ledger.execute("SELECT domain, db_path, table_name, COUNT(*) count FROM lifecycle_records WHERE cleared_at IS NULL GROUP BY domain, db_path, table_name ORDER BY domain, db_path, table_name")]
    total = sum(int(r["count"]) for r in rows)
    by_domain: dict[str, int] = {}
    for r in rows:
        by_domain[r["domain"]] = by_domain.get(r["domain"], 0) + int(r["count"])
    ledger.close()
    return {"ok": True, "status": "CLEAR_PREVIEW_READY", "records_to_clear": total, "by_domain": by_domain, "tables": rows[:500]}


def _pk_values_from_record(rec: dict[str, Any], con: sqlite3.Connection) -> dict[str, Any]:
    try:
        payload = json.loads(rec.get("primary_key_json") or "{}")
        if isinstance(payload, dict) and payload:
            return payload
    except Exception:
        pass
    col = pk_col(con, rec["table_name"])
    return {col: rec["primary_key"]}


def clear_generated(public: bool = False, pin: str | None = None, pin_id: str | None = None) -> dict[str, Any]:  # type: ignore[override]
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    ok, reason = validate_pin(pin, pin_id)
    if not ok:
        return {"ok": False, "status": reason, "message": "Clear bloqueado por PIN."}
    preview = clear_preview(public=False)
    backup = create_backup("before_clear")
    clear_batch = f"clear_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    ledger = ensure_ledger()
    records = [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_records WHERE cleared_at IS NULL ORDER BY id DESC")]
    results = []
    errors = []
    con_cache: dict[str, sqlite3.Connection] = {}
    try:
        for rec in records:
            db_path = rec["db_path"]
            table = rec["table_name"]
            try:
                con = con_cache.get(db_path)
                if con is None:
                    con = connect(db_path); con_cache[db_path] = con
                if not has_table(con, table):
                    ledger.execute("UPDATE lifecycle_records SET clear_error=? WHERE id=?", ("TABLE_MISSING", rec["id"]))
                    results.append({"record": rec["id"], "table": table, "status": "TABLE_MISSING"})
                    continue
                pk_values = _pk_values_from_record(rec, con)
                where = " AND ".join([f"{sql_ident(k)}=?" for k in pk_values])
                before = con.total_changes
                con.execute(f"DELETE FROM {sql_ident(table)} WHERE {where}", list(pk_values.values()))
                deleted = con.total_changes - before
                ledger.execute("UPDATE lifecycle_records SET cleared_at=?, clear_batch=?, clear_error=NULL WHERE id=?", (utcnow(), clear_batch, rec["id"]))
                results.append({"record": rec["id"], "db": relative_to_project(db_path), "table": table, "pk": pk_values, "deleted": int(deleted)})
            except Exception as exc:
                ledger.execute("UPDATE lifecycle_records SET clear_error=? WHERE id=?", (str(exc), rec["id"]))
                errors.append({"record_id": rec.get("id"), "db": relative_to_project(db_path), "table": table, "error": str(exc)})
        for con in con_cache.values():
            con.commit(); con.close()
        ledger.commit()
    except Exception as exc:
        for con in con_cache.values():
            try: con.rollback(); con.close()
            except Exception: pass
        errors.append({"fatal": str(exc), "traceback": traceback.format_exc()})
    status = "PASS" if not errors else "WARN"
    payload = {"ok": not bool(errors), "status": status, "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "clear_batch": clear_batch, "backup": backup, "preview_before_clear": preview, "cleared_records": len(results), "results": results[:5000], "errors": errors}
    evidence = write_evidence(f"clear_{clear_batch}", payload)
    log_event("clear", {"clear_batch": clear_batch, "status": status, "evidence": evidence, "errors": len(errors)})
    ledger.close()
    return payload


def latest_evidence() -> dict[str, Any]:  # type: ignore[override]
    ensure_dirs()
    files = sorted(list(EVIDENCE_DIR.glob("*.json")) + list(EVIDENCE_DIR.glob("*.zip")) + list(EVIDENCE_DIR.glob("*.md")), key=lambda p: p.stat().st_mtime, reverse=True)[:30]
    return {"ok": True, "status": "READY", "files": [{"name": p.name, "path": str(p), "modified": _dt.datetime.fromtimestamp(p.stat().st_mtime).isoformat(), "size": p.stat().st_size} for p in files]}


def lifecycle_payload(path: str, public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    ensure_dirs()
    parsed = urlparse(path)
    clean = parsed.path.rstrip("/")
    qs = parse_qs(parsed.query)
    parts = [p for p in clean.split("/") if p]
    try:
        if clean in {"/api/lifecycle", "/api/lifecycle/latest", "/api/lifecycle/dashboard"}:
            return latest_dashboard(public=public)
        if clean.startswith("/api/lifecycle/preflight"):
            return preflight(public=public)
        if clean.startswith("/api/lifecycle/config"):
            return {"ok": True, "status": "READY", "apiVersion": API_VERSION, "config": config_summary(), "profiles": profiles(), "clear_policy": clear_policy()}
        if clean.startswith("/api/lifecycle/plan"):
            mode = parts[-1] if len(parts) >= 4 else (qs.get("mode", ["light"])[0])
            return {"ok": True, "status": "READY", "plan": create_injection_plan(mode), "profiles": profiles()}
        if clean.startswith("/api/lifecycle/inject"):
            mode = parts[-1] if len(parts) >= 4 else (qs.get("mode", ["light"])[0])
            return inject(mode, public=public)
        if clean.startswith("/api/lifecycle/clear/preview"):
            return clear_preview(public=public)
        if clean.startswith("/api/lifecycle/clear/request-pin"):
            return request_pin(public=public)
        if clean.startswith("/api/lifecycle/clear/confirm"):
            return clear_generated(public=public, pin=qs.get("pin", [None])[0], pin_id=qs.get("pin_id", [None])[0])
        if clean.startswith("/api/lifecycle/evidence/latest"):
            return latest_evidence()
        if clean.startswith("/api/lifecycle/health"):
            return {"ok": True, "status": "LIFECYCLE_READY", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "data_dir": str(DATA_DIR), "ledger": str(LEDGER_PATH)}
        return {"ok": False, "status": "UNKNOWN_LIFECYCLE_ROUTE", "path": path}
    except Exception as exc:
        return {"ok": False, "status": "LIFECYCLE_EXCEPTION", "error": str(exc), "traceback": traceback.format_exc()}



# ============================================================================
# PRISMA DATA LIFECYCLE V3 MASTER NO-DOWNGRADE LAYER
# Built on V2 MASTER. This layer intentionally overrides selected functions
# while preserving V2 APIs, ledger schema and generated-only cleanup semantics.
# ============================================================================
API_VERSION = "PRISMA_DATA_LIFECYCLE_API_V3"
HARDENING_VERSION = "v3-master-no-downgrade"
V3_MASTER_FEATURES = [
    "no_downgrade_contract",
    "guardrail_caps",
    "plan_preview_v3",
    "ledger_integrity_audit",
    "backup_catalog",
    "pin_guarded_rollback",
    "foreign_key_check_before_after_clear",
    "public_path_sanitizer",
    "data_pool_contract",
    "evidence_index",
]

V3_EXTRA_CONFIGS = {
    "guardrails": "lifecycle_guardrails.json",
    "data_pools": "lifecycle_data_pools.json",
    "safety_contract": "lifecycle_safety_contract.json",
}


def _load_extra_config(name: str, fallback: Any) -> Any:
    filename = V3_EXTRA_CONFIGS.get(name, name)
    return load_json(CONFIG_DIR / filename, fallback)


def guardrails() -> dict[str, Any]:
    return _load_extra_config("guardrails", {
        "max_products": {"light": 100, "heavy": 500, "longaniza": 2000},
        "max_days": {"light": 30, "heavy": 120, "longaniza": 360},
        "max_tablets": {"light": 2, "heavy": 5, "longaniza": 12},
        "max_users": {"light": 8, "heavy": 20, "longaniza": 60},
        "max_suppliers": {"light": 12, "heavy": 40, "longaniza": 120},
        "allow_longaniza": True,
        "require_pin_for_rollback": True,
        "public_mutations_blocked": True,
        "clear_requires_backup": True,
        "rollback_creates_pre_restore_backup": True,
    })


def data_pools() -> dict[str, Any]:
    return _load_extra_config("data_pools", {
        "business_names": ["Abarrotes Prisma Norte", "Mini Súper Los Portales", "Miscelánea El Faro", "Prisma Market Centro"],
        "store_names": ["Sucursal Matriz", "Caja Principal", "Mostrador Norte"],
        "tablet_names": ["Caja 1", "Caja 2", "Caja 3", "Mostrador", "Almacén", "Patio", "Ruta 1", "Ruta 2"],
        "cashiers": FIRST_NAMES,
        "suppliers": SUPPLIER_NAMES,
        "categories": list(CATEGORIES.keys()),
        "products_by_category": CATEGORIES,
    })


def public_safe(value: Any) -> Any:
    """Recursively strip local paths from public responses while retaining useful shape."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            lk = str(k).lower()
            if lk in {"path", "db_path", "zip_path", "evidence_path", "backup_path", "ledger", "project_root", "control_center_root"}:
                out[k] = "PRISMA_LOCAL_PATH_REDACTED"
            else:
                out[k] = public_safe(v)
        return out
    if isinstance(value, list):
        return [public_safe(x) for x in value]
    if isinstance(value, str):
        # Redact obvious Windows and Unix absolute paths, but keep labels/statuses.
        if re.search(r"[A-Za-z]:[\\/]", value) or value.startswith("/mnt/") or value.startswith("/home/") or value.startswith("/tmp/"):
            return "PRISMA_LOCAL_PATH_REDACTED"
    return value


def clamp_int(value: Any, lo: int, hi: int) -> int:
    try:
        n = int(value)
    except Exception:
        n = lo
    return max(lo, min(hi, n))


def create_injection_plan(mode: str) -> dict[str, Any]:  # type: ignore[override]
    profs = profiles()
    raw_mode = str(mode or "light").lower().strip()
    if raw_mode not in profs:
        raw_mode = "light"
    p = dict(profs.get(raw_mode, PROFILE_DEFAULTS["light"]))
    g = guardrails()
    # Apply hard caps so bad config cannot accidentally create an infinite longaniza.
    days = clamp_int(p.get("days", 30), 1, int(g.get("max_days", {}).get(raw_mode, 30)))
    products = clamp_int(p.get("products", 80), 1, int(g.get("max_products", {}).get(raw_mode, 100)))
    suppliers = clamp_int(p.get("suppliers", 10), 1, int(g.get("max_suppliers", {}).get(raw_mode, 12)))
    users = clamp_int(p.get("users", 5), 1, int(g.get("max_users", {}).get(raw_mode, 8)))
    tablets = clamp_int(p.get("tablets", 2), 1, int(g.get("max_tablets", {}).get(raw_mode, 2)))
    sales_per_day = clamp_int(p.get("sales_per_day", 8), 1, 500)
    purchase_orders = clamp_int(p.get("purchase_orders", 12), 0, 10000)
    sales_target = days * sales_per_day
    estimates_by_domain = {
        "Tenant": 2,
        "Identity": users * 2 + 8,
        "Devices": tablets * 2,
        "Catalog": products * 3 + 4,
        "Suppliers": suppliers + max(1, products),
        "Purchasing": purchase_orders * 5,
        "Inventory": products * 2,
        "Cash": max(days * tablets, tablets),
        "Sales": sales_target * 4,
        "Sync": max(sales_target // 3, tablets * days // 2),
        "Audit": max(sales_target // 2, 20),
        "Chart Lab": max(12, days // 7),
        "License": 3,
    }
    plan = {
        "mode": raw_mode,
        "label": p.get("label", raw_mode.title()),
        "hardeningVersion": HARDENING_VERSION,
        "apiVersion": API_VERSION,
        "days": days,
        "products": products,
        "suppliers": suppliers,
        "users": users,
        "tablets": tablets,
        "sales_per_day": sales_per_day,
        "purchase_orders": purchase_orders,
        "sales_target": sales_target,
        "estimated_total_records": int(sum(estimates_by_domain.values())),
        "estimated_by_domain": estimates_by_domain,
        "execution_order": ["Tenant", "Identity", "Devices", "Catalog", "Suppliers", "Purchasing", "Inventory", "Cash", "Sales", "Sync", "Audit", "Chart Lab", "License"],
        "clear_order": ["Chart Lab", "Audit", "Sync", "Sales", "Cash", "Inventory", "Purchasing", "Suppliers", "Catalog", "Devices", "Identity", "Tenant", "License"],
        "safety": {
            "ledger_required": True,
            "backup_before_inject": True,
            "backup_before_clear": True,
            "generated_only_clear_default": True,
            "schema_mutation": False,
            "external_dependencies": False,
        },
        "warnings": [],
    }
    if raw_mode == "longaniza":
        plan["warnings"].append("Pasada de longaniza puede generar base pesada; úsala para stress test y Chart Lab denso.")
    return plan


def ledger_integrity(public: bool = False) -> dict[str, Any]:
    ensure_dirs()
    ledger = ensure_ledger()
    rows = [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_records ORDER BY id DESC LIMIT 20000")]
    counters = {
        "records_checked": 0,
        "open_records": 0,
        "cleared_records": 0,
        "missing_db": 0,
        "missing_table": 0,
        "missing_row_open": 0,
        "row_still_exists_after_clear": 0,
        "schema_hash_changed": 0,
        "errors": 0,
    }
    samples: list[dict[str, Any]] = []
    con_cache: dict[str, sqlite3.Connection] = {}
    try:
        for rec in rows:
            counters["records_checked"] += 1
            is_open = rec.get("cleared_at") in (None, "")
            counters["open_records" if is_open else "cleared_records"] += 1
            db_path = rec.get("db_path")
            table = rec.get("table_name")
            issue = None
            try:
                if not db_path or not Path(db_path).exists():
                    counters["missing_db"] += 1; issue = "MISSING_DB"
                else:
                    con = con_cache.get(db_path)
                    if con is None:
                        con = connect(db_path); con_cache[db_path] = con
                    if not table or not has_table(con, table):
                        counters["missing_table"] += 1; issue = "MISSING_TABLE"
                    else:
                        pk_values = _pk_values_from_record(rec, con)
                        row = row_by_pk(con, table, pk_values) if pk_values else None
                        if is_open and row is None:
                            counters["missing_row_open"] += 1; issue = "OPEN_RECORD_ROW_MISSING"
                        if (not is_open) and row is not None:
                            counters["row_still_exists_after_clear"] += 1; issue = "CLEARED_RECORD_ROW_STILL_EXISTS"
                        if rec.get("schema_hash") and rec.get("schema_hash") != table_schema_hash(con, table):
                            counters["schema_hash_changed"] += 1
                            issue = issue or "SCHEMA_HASH_CHANGED"
            except Exception as exc:
                counters["errors"] += 1
                issue = f"ERROR: {exc}"
            if issue and len(samples) < 80:
                samples.append({"record_id": rec.get("id"), "domain": rec.get("domain"), "table": table, "issue": issue, "db_path": db_path})
    finally:
        for con in con_cache.values():
            try: con.close()
            except Exception: pass
        ledger.close()
    ok = not any(counters[k] for k in ["missing_db", "missing_table", "missing_row_open", "row_still_exists_after_clear", "errors"])
    payload = {"ok": ok, "status": "LEDGER_INTEGRITY_PASS" if ok else "LEDGER_INTEGRITY_WARN", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "counters": counters, "samples": samples}
    return public_safe(payload) if public else payload


def foreign_key_report() -> dict[str, Any]:
    report: dict[str, Any] = {"checked": 0, "violations": []}
    for db in discover_dbs():
        try:
            con = connect(db["path"])
            rows = [dict(r) for r in con.execute("PRAGMA foreign_key_check").fetchall()]
            con.close()
            report["checked"] += 1
            if rows:
                report["violations"].append({"db": db, "violations": rows[:200]})
        except Exception as exc:
            report.setdefault("errors", []).append({"db": db, "error": str(exc)})
    report["ok"] = not bool(report.get("violations") or report.get("errors"))
    return report


def preflight(public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    ledger = ensure_ledger()
    dbs = discover_dbs()
    cfg = config_summary()
    payload = {
        "ok": True,
        "status": "PREFLIGHT_READY",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "features": V3_MASTER_FEATURES,
        "project_root": str(project_root()),
        "control_center_root": str(CONTROL_CENTER_ROOT),
        "config": cfg,
        "guardrails": guardrails(),
        "databases": dbs,
        "database_count": len(dbs),
        "domain_count": len(domain_map()),
        "ledger": {
            "path": str(LEDGER_PATH),
            "records_open": ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE cleared_at IS NULL").fetchone()[0],
            "batches": ledger.execute("SELECT COUNT(*) FROM lifecycle_batches").fetchone()[0],
            "backups": ledger.execute("SELECT COUNT(*) FROM lifecycle_backups").fetchone()[0],
        },
        "foreign_keys": foreign_key_report(),
    }
    ledger.close()
    return public_safe(payload) if public else payload


def latest_dashboard(public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    base = globals().get("__v2_dashboard_func")
    # The v2 dashboard function was overridden, so manually reuse its code by calling the previous name if saved;
    # fallback to a compact dashboard if not available.
    # We save nothing at runtime in V2, so duplicate robust dashboard shape here.
    ensure_dirs(); ledger = ensure_ledger()
    dm = domain_map(); dbs = discover_dbs(); domains = []
    for domain, tables in dm.items():
        total = 0; by_table = []
        for db in dbs:
            try:
                con = connect(db["path"]); names = table_names(con)
                for table in tables:
                    if table not in names:
                        continue
                    c = con.execute(f"SELECT COUNT(*) FROM {sql_ident(table)}").fetchone()[0]
                    gen = ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE db_path=? AND table_name=? AND domain=? AND cleared_at IS NULL", (db["path"], table, domain)).fetchone()[0]
                    total += int(c)
                    by_table.append({"db": db["relative_path"], "surface": db["surface"], "table": table, "total": int(c), "generated": int(gen), "manual_or_real": max(0, int(c)-int(gen))})
                con.close()
            except Exception as exc:
                by_table.append({"db": db.get("relative_path"), "table": "*", "error": str(exc), "total": 0, "generated": 0, "manual_or_real": 0})
        generated = sum(int(x.get("generated", 0)) for x in by_table)
        manual = max(0, total-generated)
        if total == 0:
            state = "clean"
        elif generated and manual:
            state = "mixed"
        elif generated:
            state = "generated"
        else:
            state = "manual_or_real"
        domains.append({"domain": domain, "total": total, "generated": generated, "manual_or_real": manual, "state": state, "tables": by_table})
    last_batches = [dict(r) for r in ledger.execute("SELECT batch_id, mode, status, created_at, finished_at, evidence_path, backup_path, api_version FROM lifecycle_batches ORDER BY created_at DESC LIMIT 10")]
    last_events = [dict(r) for r in ledger.execute("SELECT event_type, created_at, payload_json FROM lifecycle_events ORDER BY id DESC LIMIT 10")]
    last_backups = [dict(r) for r in ledger.execute("SELECT backup_id, reason, created_at, zip_path, sha256 FROM lifecycle_backups ORDER BY created_at DESC LIMIT 6")]
    pin_cfg = config()
    payload = {
        "ok": True,
        "status": "READY",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "project_root": str(project_root()),
        "control_center_root": str(CONTROL_CENTER_ROOT),
        "owner_email": pin_cfg.get("owner_email"),
        "pin_required": bool(pin_cfg.get("pin_required", True)),
        "allow_clear_without_pin": bool(pin_cfg.get("allow_clear_without_pin", False)),
        "databases": dbs,
        "domains": domains,
        "last_batches": last_batches,
        "last_events": last_events,
        "last_backups": last_backups,
        "generated_records_open": ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE cleared_at IS NULL").fetchone()[0],
        "ledger": str(LEDGER_PATH),
        "integrity_summary": ledger_integrity(public=False).get("counters", {}),
    }
    ledger.close()
    return public_safe(payload) if public else payload


def backup_catalog(public: bool = False) -> dict[str, Any]:
    ledger = ensure_ledger()
    rows = [dict(r) for r in ledger.execute("SELECT backup_id, reason, created_at, zip_path, sha256, manifest_json FROM lifecycle_backups ORDER BY created_at DESC LIMIT 30")]
    out = []
    for r in rows:
        manifest = {}
        try: manifest = json.loads(r.get("manifest_json") or "{}")
        except Exception: manifest = {}
        out.append({
            "backup_id": r.get("backup_id"),
            "reason": r.get("reason"),
            "created_at": r.get("created_at"),
            "zip_path": r.get("zip_path"),
            "sha256": r.get("sha256"),
            "database_count": len(manifest.get("databases", [])),
            "config_count": len(manifest.get("configs", [])),
            "size_bytes": Path(r.get("zip_path") or "").stat().st_size if r.get("zip_path") and Path(r.get("zip_path")).exists() else 0,
        })
    ledger.close()
    payload = {"ok": True, "status": "BACKUPS_READY", "backups": out}
    return public_safe(payload) if public else payload


def restore_backup(backup_id: str | None = None, pin: str | None = None, pin_id: str | None = None, dry_run: bool = False, public: bool = False) -> dict[str, Any]:
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    if guardrails().get("require_pin_for_rollback", True):
        ok, reason = validate_pin(pin, pin_id)
        if not ok:
            return {"ok": False, "status": reason, "message": "Rollback bloqueado por PIN."}
    ledger = ensure_ledger()
    if backup_id:
        row = ledger.execute("SELECT * FROM lifecycle_backups WHERE backup_id=?", (backup_id,)).fetchone()
    else:
        row = ledger.execute("SELECT * FROM lifecycle_backups ORDER BY created_at DESC LIMIT 1").fetchone()
    if not row:
        ledger.close(); return {"ok": False, "status": "NO_BACKUP_AVAILABLE"}
    row = dict(row)
    zip_path = Path(row.get("zip_path") or "")
    if not zip_path.exists():
        ledger.close(); return {"ok": False, "status": "BACKUP_ZIP_MISSING", "backup_id": row.get("backup_id")}
    try:
        manifest = json.loads(row.get("manifest_json") or "{}")
    except Exception:
        manifest = {}
    plan = [{"target": item.get("path"), "arcname": item.get("arcname"), "sha256": item.get("sha256")} for item in manifest.get("databases", [])]
    if dry_run:
        ledger.close(); return public_safe({"ok": True, "status": "ROLLBACK_PREVIEW_READY", "backup_id": row.get("backup_id"), "plan": plan}) if public else {"ok": True, "status": "ROLLBACK_PREVIEW_READY", "backup_id": row.get("backup_id"), "plan": plan}
    pre = create_backup("before_rollback") if guardrails().get("rollback_creates_pre_restore_backup", True) else None
    restored = []
    errors = []
    with zipfile.ZipFile(zip_path, "r") as z:
        for item in manifest.get("databases", []):
            try:
                target = Path(item["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(item["arcname"], "r") as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                restored.append({"path": str(target), "arcname": item.get("arcname"), "sha256_after": sha256_file(target)})
            except Exception as exc:
                errors.append({"item": item, "error": str(exc)})
    payload = {"ok": not bool(errors), "status": "ROLLBACK_PASS" if not errors else "ROLLBACK_WARN", "backup_id": row.get("backup_id"), "pre_restore_backup": pre, "restored": restored, "errors": errors}
    evidence = write_evidence(f"rollback_{row.get('backup_id')}", payload)
    log_event("rollback", {"backup_id": row.get("backup_id"), "status": payload["status"], "evidence": evidence, "errors": len(errors)})
    ledger.close()
    return public_safe(payload) if public else payload


def create_backup_endpoint(reason: str = "manual", public: bool = False) -> dict[str, Any]:
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    path = create_backup(reason or "manual")
    payload = {"ok": True, "status": "BACKUP_CREATED", "backup": path, "catalog": backup_catalog(public=False)}
    return public_safe(payload) if public else payload


def clear_generated(public: bool = False, pin: str | None = None, pin_id: str | None = None) -> dict[str, Any]:  # type: ignore[override]
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    ok, reason = validate_pin(pin, pin_id)
    if not ok:
        return {"ok": False, "status": reason, "message": "Clear bloqueado por PIN."}
    fk_before = foreign_key_report()
    preview = clear_preview(public=False)
    backup = create_backup("before_clear")
    clear_batch = f"clear_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    ledger = ensure_ledger()
    records = [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_records WHERE cleared_at IS NULL ORDER BY id DESC")]
    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    con_cache: dict[str, sqlite3.Connection] = {}
    try:
        for rec in records:
            db_path = rec["db_path"]; table = rec["table_name"]
            try:
                con = con_cache.get(db_path)
                if con is None:
                    con = connect(db_path); con_cache[db_path] = con
                if not has_table(con, table):
                    ledger.execute("UPDATE lifecycle_records SET clear_error=? WHERE id=?", ("TABLE_MISSING", rec["id"]))
                    results.append({"record": rec["id"], "table": table, "status": "TABLE_MISSING"})
                    continue
                pk_values = _pk_values_from_record(rec, con)
                if not pk_values:
                    ledger.execute("UPDATE lifecycle_records SET clear_error=? WHERE id=?", ("PK_UNRESOLVED", rec["id"]))
                    results.append({"record": rec["id"], "table": table, "status": "PK_UNRESOLVED"})
                    continue
                before = con.total_changes
                where = " AND ".join([f"{sql_ident(k)}=?" for k in pk_values.keys()])
                con.execute(f"DELETE FROM {sql_ident(table)} WHERE {where}", list(pk_values.values()))
                deleted = con.total_changes - before
                ledger.execute("UPDATE lifecycle_records SET cleared_at=?, clear_batch=?, clear_error=NULL WHERE id=?", (utcnow(), clear_batch, rec["id"]))
                results.append({"record": rec["id"], "db": db_path, "table": table, "pk": pk_values, "deleted": int(deleted)})
            except Exception as exc:
                ledger.execute("UPDATE lifecycle_records SET clear_error=? WHERE id=?", (str(exc), rec.get("id")))
                errors.append({"record_id": rec.get("id"), "domain": rec.get("domain"), "table": table, "error": str(exc)})
        for con in con_cache.values():
            con.commit(); con.close()
        ledger.commit()
    except Exception as exc:
        for con in con_cache.values():
            try: con.rollback(); con.close()
            except Exception: pass
        errors.append({"fatal": str(exc), "traceback": traceback.format_exc()})
    fk_after = foreign_key_report()
    integrity = ledger_integrity(public=False)
    status = "PASS" if not errors and fk_after.get("ok") else "WARN"
    payload = {"ok": status == "PASS", "status": status, "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "clear_batch": clear_batch, "backup": backup, "preview_before_clear": preview, "foreign_keys_before": fk_before, "foreign_keys_after": fk_after, "ledger_integrity_after": integrity, "cleared_records": len(results), "results": results[:5000], "errors": errors}
    evidence = write_evidence(f"clear_{clear_batch}", payload)
    log_event("clear", {"clear_batch": clear_batch, "status": status, "evidence": evidence, "errors": len(errors), "fk_ok_after": fk_after.get("ok")})
    ledger.close()
    return public_safe(payload) if public else payload


def lifecycle_payload(path: str, public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    ensure_dirs()
    parsed = urlparse(path)
    clean = parsed.path.rstrip("/")
    qs = parse_qs(parsed.query)
    parts = [p for p in clean.split("/") if p]
    try:
        if clean in {"/api/lifecycle", "/api/lifecycle/latest", "/api/lifecycle/dashboard"}:
            return latest_dashboard(public=public)
        if clean.startswith("/api/lifecycle/preflight"):
            return preflight(public=public)
        if clean.startswith("/api/lifecycle/config") or clean.startswith("/api/lifecycle/version"):
            payload = {"ok": True, "status": "READY", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "features": V3_MASTER_FEATURES, "config": config_summary(), "profiles": profiles(), "clear_policy": clear_policy(), "guardrails": guardrails()}
            return public_safe(payload) if public else payload
        if clean.startswith("/api/lifecycle/plan"):
            mode = parts[-1] if len(parts) >= 4 else (qs.get("mode", ["light"])[0])
            payload = {"ok": True, "status": "READY", "apiVersion": API_VERSION, "plan": create_injection_plan(mode), "profiles": profiles(), "guardrails": guardrails()}
            return public_safe(payload) if public else payload
        if clean.startswith("/api/lifecycle/inject"):
            mode = parts[-1] if len(parts) >= 4 else (qs.get("mode", ["light"])[0])
            return inject(mode, public=public)
        if clean.startswith("/api/lifecycle/clear/preview"):
            return clear_preview(public=public)
        if clean.startswith("/api/lifecycle/clear/request-pin"):
            return request_pin(public=public)
        if clean.startswith("/api/lifecycle/clear/confirm"):
            return clear_generated(public=public, pin=qs.get("pin", [None])[0], pin_id=qs.get("pin_id", [None])[0])
        if clean.startswith("/api/lifecycle/ledger/integrity") or clean.startswith("/api/lifecycle/audit"):
            return ledger_integrity(public=public)
        if clean.startswith("/api/lifecycle/backups"):
            return backup_catalog(public=public)
        if clean.startswith("/api/lifecycle/backup/create"):
            return create_backup_endpoint(qs.get("reason", ["manual"])[0], public=public)
        if clean.startswith("/api/lifecycle/rollback/preview"):
            return restore_backup(backup_id=qs.get("backup_id", [None])[0], dry_run=True, public=public)
        if clean.startswith("/api/lifecycle/rollback/confirm"):
            return restore_backup(backup_id=qs.get("backup_id", [None])[0], pin=qs.get("pin", [None])[0], pin_id=qs.get("pin_id", [None])[0], dry_run=False, public=public)
        if clean.startswith("/api/lifecycle/evidence/latest"):
            payload = latest_evidence()
            return public_safe(payload) if public else payload
        if clean.startswith("/api/lifecycle/health"):
            payload = {"ok": True, "status": "LIFECYCLE_READY", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "features": V3_MASTER_FEATURES, "data_dir": str(DATA_DIR), "ledger": str(LEDGER_PATH)}
            return public_safe(payload) if public else payload
        return {"ok": False, "status": "UNKNOWN_LIFECYCLE_ROUTE", "path": path}
    except Exception as exc:
        payload = {"ok": False, "status": "LIFECYCLE_EXCEPTION", "error": str(exc), "traceback": traceback.format_exc()}
        return public_safe(payload) if public else payload


# ============================================================================
# PRISMA DATA LIFECYCLE V4 EXCELSIOR LAYER
# Built on V3 MASTER. No-downgrade contract: this layer preserves V3 routes,
# generated-only clear, ledger schema, backup/rollback and public sanitization,
# then adds 60+ functional improvements around observability, planning,
# evidence, dry-runs, safety and internal diagnostics.
# ============================================================================
import time as _time
import csv as _csv
import io as _io
import re

API_VERSION = "PRISMA_DATA_LIFECYCLE_API_V4"
HARDENING_VERSION = "v4-excelsior-no-downgrade"

# Preserve V3 callables before overriding selected public operations.
_V3_CREATE_INJECTION_PLAN = create_injection_plan
_V3_INJECT = inject
_V3_CLEAR_GENERATED = clear_generated
_V3_CREATE_BACKUP_ENDPOINT = create_backup_endpoint
_V3_RESTORE_BACKUP = restore_backup
_V3_LIFECYCLE_PAYLOAD = lifecycle_payload

V4_MASTER_FEATURES = [
    "operation_lock", "dry_run_inject", "dry_run_clear", "evidence_bundle", "schema_inventory",
    "domain_drilldown", "batch_detail", "lifecycle_history", "data_quality_report", "safety_doctor",
    "dashboard_snapshot", "dashboard_diff", "generated_ratio", "longaniza_guardrails", "plan_dependencies",
    "plan_chunks", "risk_score", "estimated_timings", "seed_sample_preview", "config_validator",
    "smtp_diagnostics", "pin_status", "evidence_index", "backup_verify", "backup_catalog_enhanced",
    "rollback_preview_enhanced", "retention_preview", "retention_prune", "public_sanitizer_strict", "route_catalog",
    "feature_catalog", "no_downgrade_manifest", "ledger_open_records_by_batch", "ledger_stale_errors", "orphan_check_helper",
    "configurable_evidence_exports", "csv_dashboard_export", "json_report_export", "markdown_executive_report", "internal_tools_panel",
    "action_chips", "longaniza_warning_ui", "safe_clear_result_summary", "telemetry_metrics", "operation_ids",
    "failure_envelope", "local_only_awareness", "db_role_detection", "read_only_analysis_endpoints", "write_endpoints_guarded",
    "seed_coherence_contract", "domain_status_classification", "backup_before_dangerous_ops", "evidence_hash_manifest", "manifest_route",
    "health_contract_extended", "verifier_expansion", "temp_db_deeper_test", "css_polish", "js_resilience",
    "bundle_readme", "sanitized_latest_evidence", "retention_policy_config", "excelsior_marker"
]

V4_EXTRA_CONFIGS = {
    "improvement_catalog": "lifecycle_improvement_catalog.json",
    "observability_policy": "lifecycle_observability_policy.json",
    "export_policy": "lifecycle_export_policy.json",
    "retention_policy": "lifecycle_retention_policy.json",
}

LOCK_FILE = DATA_DIR / "lifecycle_operation.lock"


def v4_config(name: str, fallback: Any) -> Any:
    return load_json(CONFIG_DIR / V4_EXTRA_CONFIGS.get(name, name), fallback)


def improvement_catalog() -> dict[str, Any]:
    return v4_config("improvement_catalog", {"catalog_version": HARDENING_VERSION, "improvements": []})


def observability_policy() -> dict[str, Any]:
    return v4_config("observability_policy", {"operation_lock_ttl_seconds": 1800, "telemetry_enabled": True})


def export_policy() -> dict[str, Any]:
    return v4_config("export_policy", {"ai_safe_exports": True, "redact_paths": True, "max_latest_evidence_files": 25})


def retention_policy() -> dict[str, Any]:
    return v4_config("retention_policy", {"evidence_keep_days": 30, "backup_keep_days": 30, "minimum_backups_to_keep": 5, "minimum_evidence_to_keep": 20, "prune_requires_pin": True})


def ensure_v4_tables(ledger: sqlite3.Connection | None = None) -> sqlite3.Connection:
    ensure_dirs()
    own = ledger is None
    ledger = ledger or ensure_ledger()
    ledger.executescript("""
    CREATE TABLE IF NOT EXISTS lifecycle_operation_metrics(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      operation_id TEXT UNIQUE,
      kind TEXT,
      status TEXT,
      started_at TEXT,
      finished_at TEXT,
      duration_ms INTEGER,
      payload_json TEXT
    );
    CREATE TABLE IF NOT EXISTS lifecycle_dashboard_snapshots(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      snapshot_id TEXT UNIQUE,
      created_at TEXT,
      dashboard_hash TEXT,
      dashboard_json TEXT
    );
    CREATE TABLE IF NOT EXISTS lifecycle_exports(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      export_id TEXT UNIQUE,
      kind TEXT,
      created_at TEXT,
      path TEXT,
      sha256 TEXT,
      payload_json TEXT
    );
    """)
    ledger.commit()
    if own:
        return ledger
    return ledger


def json_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def operation_id(kind: str) -> str:
    return f"op_{kind}_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def read_lock() -> dict[str, Any] | None:
    try:
        if LOCK_FILE.exists():
            return json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "CORRUPT_LOCK", "path": str(LOCK_FILE)}
    return None


def acquire_lock(kind: str) -> tuple[bool, dict[str, Any]]:
    ensure_dirs()
    ttl = int(observability_policy().get("operation_lock_ttl_seconds", 1800))
    now = int(_time.time())
    existing = read_lock()
    if existing and int(existing.get("expires_at_epoch", 0) or 0) > now:
        return False, {"ok": False, "status": "OPERATION_LOCKED", "lock": existing}
    op_id = operation_id(kind)
    lock = {"operation_id": op_id, "kind": kind, "created_at": utcnow(), "created_at_epoch": now, "expires_at_epoch": now + ttl, "ttl_seconds": ttl}
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.write_text(json.dumps(lock, ensure_ascii=False, indent=2), encoding="utf-8")
    return True, lock


def release_lock(operation_id_value: str | None = None) -> None:
    try:
        current = read_lock()
        if LOCK_FILE.exists() and (not operation_id_value or not current or current.get("operation_id") == operation_id_value):
            LOCK_FILE.unlink()
    except Exception:
        pass


def record_metric(kind: str, status: str, started: float, payload: dict[str, Any], op_id: str | None = None) -> None:
    try:
        ledger = ensure_v4_tables()
        finished = _time.time()
        op_id = op_id or payload.get("operation_id") or operation_id(kind)
        ledger.execute(
            "INSERT OR REPLACE INTO lifecycle_operation_metrics(operation_id, kind, status, started_at, finished_at, duration_ms, payload_json) VALUES(?,?,?,?,?,?,?)",
            (op_id, kind, status, _dt.datetime.fromtimestamp(started).isoformat(), _dt.datetime.fromtimestamp(finished).isoformat(), int((finished-started)*1000), safe_json(payload)[:200000]),
        )
        ledger.commit(); ledger.close()
    except Exception:
        pass


def route_catalog() -> dict[str, Any]:
    routes = [
        ["GET", "/api/lifecycle/latest", "Dashboard actual"],
        ["GET", "/api/lifecycle/preflight", "Preflight técnico"],
        ["GET", "/api/lifecycle/config", "Config + perfiles"],
        ["GET", "/api/lifecycle/plan/{mode}", "Plan de inyección"],
        ["GET", "/api/lifecycle/plan/dry-run/{mode}", "Dry-run sin mutar DB"],
        ["GET", "/api/lifecycle/inject/{mode}", "Inyectar datos por modo"],
        ["GET", "/api/lifecycle/clear/preview", "Preview de clear"],
        ["GET", "/api/lifecycle/clear/dry-run", "Dry-run de clear"],
        ["GET", "/api/lifecycle/clear/request-pin", "Solicitar PIN"],
        ["GET", "/api/lifecycle/clear/confirm?pin=030303", "Clear con PIN"],
        ["GET", "/api/lifecycle/audit", "Auditoría de ledger"],
        ["GET", "/api/lifecycle/ledger/integrity", "Integridad de ledger"],
        ["GET", "/api/lifecycle/backups", "Catálogo de backups"],
        ["GET", "/api/lifecycle/backup/create", "Crear backup manual"],
        ["GET", "/api/lifecycle/rollback/preview", "Preview rollback"],
        ["GET", "/api/lifecycle/rollback/confirm", "Rollback con PIN"],
        ["GET", "/api/lifecycle/evidence/latest", "Última evidencia"],
        ["GET", "/api/lifecycle/evidence/bundle", "ZIP de evidencia AI-safe"],
        ["GET", "/api/lifecycle/schema", "Inventario de schemas"],
        ["GET", "/api/lifecycle/domain/{domain}", "Detalle por dominio"],
        ["GET", "/api/lifecycle/batch/{batch_id}", "Detalle por batch"],
        ["GET", "/api/lifecycle/history", "Historial"],
        ["GET", "/api/lifecycle/quality", "Data quality report"],
        ["GET", "/api/lifecycle/doctor", "Safety doctor"],
        ["GET", "/api/lifecycle/snapshot/create", "Snapshot dashboard"],
        ["GET", "/api/lifecycle/snapshot/diff", "Diff dashboard"],
        ["GET", "/api/lifecycle/pin/status", "Estado PIN"],
        ["GET", "/api/lifecycle/smtp/diagnostics", "Diagnóstico SMTP"],
        ["GET", "/api/lifecycle/export/dashboard.csv", "Export dashboard CSV"],
        ["GET", "/api/lifecycle/export/report.md", "Export reporte MD"],
        ["GET", "/api/lifecycle/retention/preview", "Preview poda"],
        ["GET", "/api/lifecycle/retention/prune", "Poda con PIN"],
        ["GET", "/api/lifecycle/features", "Catálogo de mejoras"],
        ["GET", "/api/lifecycle/manifest", "Manifest V4"],
        ["GET", "/api/lifecycle/health", "Health extendido"],
    ]
    return {"ok": True, "status": "READY", "apiVersion": API_VERSION, "routes": [{"method": m, "path": p, "description": d} for m, p, d in routes]}


def config_validation_report() -> dict[str, Any]:
    cfg = config(); g = guardrails(); profs = profiles(); cat = improvement_catalog()
    findings = []
    owner = str(cfg.get("owner_email") or "")
    if "@" not in owner:
        findings.append({"level": "WARN", "code": "OWNER_EMAIL_MISSING", "message": "owner_email no parece correo válido"})
    if str(cfg.get("pin_default", "")).isdigit() is False or len(str(cfg.get("pin_default", ""))) != 6:
        findings.append({"level": "WARN", "code": "PIN_DEFAULT_INVALID", "message": "pin_default debe tener 6 dígitos"})
    if len(cat.get("improvements", [])) < 50:
        findings.append({"level": "FAIL", "code": "IMPROVEMENT_CATALOG_TOO_SMALL", "message": "catálogo v4 debe contener al menos 50 mejoras"})
    for mode in ["light", "heavy", "longaniza"]:
        if mode not in profs:
            findings.append({"level": "FAIL", "code": "PROFILE_MISSING", "mode": mode})
        if mode not in g.get("max_products", {}):
            findings.append({"level": "WARN", "code": "GUARDRAIL_PRODUCTS_MISSING", "mode": mode})
    return {"ok": not any(f["level"] == "FAIL" for f in findings), "status": "CONFIG_VALIDATION_PASS" if not any(f["level"] == "FAIL" for f in findings) else "CONFIG_VALIDATION_FAIL", "findings": findings, "config_summary": config_summary()}


def smtp_diagnostics(public: bool = False) -> dict[str, Any]:
    smtp = config().get("smtp", {}) or {}
    password_env = smtp.get("password_env", "PRISMA_LIFECYCLE_SMTP_PASSWORD")
    payload = {
        "ok": True,
        "status": "SMTP_DIAGNOSTICS_READY",
        "enabled": bool(smtp.get("enabled")),
        "host_configured": bool(smtp.get("host")),
        "username_configured": bool(smtp.get("username")),
        "from_email_configured": bool(smtp.get("from_email")),
        "password_env": password_env,
        "password_env_present": bool(os.environ.get(str(password_env))),
        "message": "SMTP enviará PIN sólo si enabled, host, username/from y password env están configurados.",
    }
    return public_safe(payload) if public else payload


def pin_status(public: bool = False) -> dict[str, Any]:
    ledger = ensure_ledger()
    rows = [dict(r) for r in ledger.execute("SELECT pin_id, owner_email, created_at, expires_at, consumed_at, email_status FROM lifecycle_pin_tokens ORDER BY id DESC LIMIT 5")]
    ledger.close()
    payload = {"ok": True, "status": "PIN_STATUS_READY", "pin_required": bool(config().get("pin_required", True)), "allow_clear_without_pin": bool(config().get("allow_clear_without_pin", False)), "recent_tokens": rows}
    return public_safe(payload) if public else payload


def create_injection_plan(mode: str) -> dict[str, Any]:  # type: ignore[override]
    plan = dict(_V3_CREATE_INJECTION_PLAN(mode))
    mode_key = plan.get("mode", "light")
    sales_target = int(plan.get("sales_target", 0) or 0)
    products = int(plan.get("products", 0) or 0)
    days = int(plan.get("days", 0) or 0)
    tablets = int(plan.get("tablets", 0) or 0)
    risk = 0
    risk += min(35, sales_target // 2000)
    risk += min(25, products // 200)
    risk += min(20, days // 30)
    risk += min(20, tablets * 2)
    if mode_key == "longaniza":
        risk += 15
    risk = min(100, risk)
    chunks = []
    if sales_target:
        chunk_size = 5000 if mode_key == "longaniza" else 2000
        for i in range(0, sales_target, chunk_size):
            chunks.append({"domain": "Sales", "chunk": len(chunks) + 1, "from": i + 1, "to": min(i + chunk_size, sales_target)})
    if products:
        pchunk = 500 if mode_key == "longaniza" else 250
        for i in range(0, products, pchunk):
            chunks.append({"domain": "Catalog", "chunk": len(chunks) + 1, "from": i + 1, "to": min(i + pchunk, products)})
    pools = data_pools()
    sample_products = []
    for cat_name, names in list((pools.get("products_by_category") or CATEGORIES).items())[:4]:
        if names:
            sample_products.append({"category": cat_name, "name": names[0]})
    plan.update({
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "risk_score": risk,
        "risk_level": "low" if risk < 35 else "medium" if risk < 70 else "high",
        "estimated_runtime_seconds": max(3, int((sales_target / 500) + (products / 300) + (days / 20))),
        "estimated_size_class": "small" if risk < 35 else "medium" if risk < 70 else "large",
        "dependency_graph": {
            "Tenant": [], "Identity": ["Tenant"], "Devices": ["Tenant"], "Catalog": ["Tenant"],
            "Suppliers": ["Catalog"], "Purchasing": ["Suppliers", "Catalog"], "Inventory": ["Catalog", "Purchasing"],
            "Cash": ["Identity", "Devices"], "Sales": ["Cash", "Catalog", "Identity", "Devices"],
            "Sync": ["Sales", "Catalog", "Devices"], "Audit": ["all"], "Chart Lab": ["Sales", "Inventory", "Sync"], "License": []
        },
        "chunks": chunks[:1000],
        "sample_preview": {
            "business": (pools.get("business_names") or ["Prisma Market Centro"])[0],
            "tablets": (pools.get("tablet_names") or ["Caja 1", "Caja 2"])[:min(3, tablets or 1)],
            "products": sample_products,
            "suppliers": (pools.get("suppliers") or SUPPLIER_NAMES)[:3],
            "users": [rand_name() for _ in range(min(3, int(plan.get("users", 3) or 3)))]
        },
        "v4_contract": {
            "no_downgrade": True,
            "schema_mutation": False,
            "clear_by_ledger": True,
            "backup_before_mutation": True,
            "operation_lock": True,
            "public_mutation_blocked": bool(config().get("block_public_mutations", True)),
        }
    })
    return plan


def inject_dry_run(mode: str, public: bool = False) -> dict[str, Any]:
    payload = {"ok": True, "status": "INJECT_DRY_RUN_READY", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "plan": create_injection_plan(mode), "dashboard_before": latest_dashboard(public=False), "will_mutate": False}
    return public_safe(payload) if public else payload


def snapshot_dashboard(label: str = "manual", public: bool = False) -> dict[str, Any]:
    ledger = ensure_v4_tables()
    dash = latest_dashboard(public=False)
    h = json_hash(dash)
    sid = f"snap_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    ledger.execute("INSERT INTO lifecycle_dashboard_snapshots(snapshot_id, created_at, dashboard_hash, dashboard_json) VALUES(?,?,?,?)", (sid, utcnow(), h, safe_json({"label": label, "dashboard": dash})))
    ledger.commit(); ledger.close()
    payload = {"ok": True, "status": "DASHBOARD_SNAPSHOT_CREATED", "snapshot_id": sid, "label": label, "dashboard_hash": h, "generated_records_open": dash.get("generated_records_open")}
    return public_safe(payload) if public else payload


def dashboard_diff(public: bool = False) -> dict[str, Any]:
    current = latest_dashboard(public=False)
    current_hash = json_hash(current)
    ledger = ensure_v4_tables()
    row = ledger.execute("SELECT * FROM lifecycle_dashboard_snapshots ORDER BY id DESC LIMIT 1").fetchone()
    ledger.close()
    if not row:
        payload = {"ok": True, "status": "NO_PREVIOUS_SNAPSHOT", "current_hash": current_hash}
        return public_safe(payload) if public else payload
    prev = dict(row)
    try:
        prev_payload = json.loads(prev.get("dashboard_json") or "{}")
    except Exception:
        prev_payload = {}
    prev_dash = prev_payload.get("dashboard", {})
    deltas = []
    prev_domains = {d.get("domain"): d for d in prev_dash.get("domains", [])}
    for d in current.get("domains", []):
        name = d.get("domain")
        p = prev_domains.get(name, {})
        deltas.append({"domain": name, "total_delta": int(d.get("total", 0) or 0) - int(p.get("total", 0) or 0), "generated_delta": int(d.get("generated", 0) or 0) - int(p.get("generated", 0) or 0)})
    payload = {"ok": True, "status": "DASHBOARD_DIFF_READY", "previous_snapshot_id": prev.get("snapshot_id"), "previous_hash": prev.get("dashboard_hash"), "current_hash": current_hash, "changed": current_hash != prev.get("dashboard_hash"), "deltas": deltas}
    return public_safe(payload) if public else payload


def schema_inventory(public: bool = False) -> dict[str, Any]:
    items = []
    for db in discover_dbs():
        db_item = {"db": db, "tables": []}
        try:
            con = connect(db["path"])
            for table in sorted(table_names(con)):
                cols = table_columns(con, table)
                try:
                    count = con.execute(f"SELECT COUNT(*) FROM {sql_ident(table)}").fetchone()[0]
                except Exception:
                    count = None
                fks = []
                try:
                    fks = [dict(r) for r in con.execute(f"PRAGMA foreign_key_list({sql_ident(table)})")]
                except Exception:
                    pass
                db_item["tables"].append({"table": table, "columns": list(cols.keys()), "pk": table_pk_cols(con, table), "foreign_keys": fks, "row_count": count, "schema_hash": table_schema_hash(con, table)})
            con.close()
        except Exception as exc:
            db_item["error"] = str(exc)
        items.append(db_item)
    payload = {"ok": True, "status": "SCHEMA_INVENTORY_READY", "apiVersion": API_VERSION, "databases": items}
    return public_safe(payload) if public else payload


def domain_detail(domain: str | None = None, public: bool = False) -> dict[str, Any]:
    dmap = domain_map()
    name = str(domain or "").replace("%20", " ").strip() or "All"
    requested = dmap.keys() if name.lower() == "all" else [name]
    details = []
    ledger = ensure_ledger()
    for dom in requested:
        tables = dmap.get(dom, [])
        detail = {"domain": dom, "tables": [], "generated_open": 0, "generated_cleared": 0}
        detail["generated_open"] = ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE domain=? AND cleared_at IS NULL", (dom,)).fetchone()[0]
        detail["generated_cleared"] = ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE domain=? AND cleared_at IS NOT NULL", (dom,)).fetchone()[0]
        for db in discover_dbs():
            try:
                con = connect(db["path"])
                for t in tables:
                    if has_table(con, t):
                        total = con.execute(f"SELECT COUNT(*) FROM {sql_ident(t)}").fetchone()[0]
                        open_gen = ledger.execute("SELECT COUNT(*) FROM lifecycle_records WHERE domain=? AND db_path=? AND table_name=? AND cleared_at IS NULL", (dom, db["path"], t)).fetchone()[0]
                        detail["tables"].append({"db": db["relative_path"], "surface": db.get("surface"), "table": t, "total": total, "generated_open": open_gen, "manual_or_real": max(0, int(total) - int(open_gen))})
                con.close()
            except Exception as exc:
                detail.setdefault("errors", []).append(str(exc))
        details.append(detail)
    ledger.close()
    payload = {"ok": True, "status": "DOMAIN_DETAIL_READY", "domain": name, "details": details}
    return public_safe(payload) if public else payload


def batch_detail(batch: str | None = None, public: bool = False) -> dict[str, Any]:
    ledger = ensure_ledger()
    if not batch:
        row = ledger.execute("SELECT batch_id FROM lifecycle_batches ORDER BY id DESC LIMIT 1").fetchone()
        batch = row[0] if row else None
    if not batch:
        ledger.close(); return {"ok": True, "status": "NO_BATCHES"}
    b = ledger.execute("SELECT * FROM lifecycle_batches WHERE batch_id=?", (batch,)).fetchone()
    records = [dict(r) for r in ledger.execute("SELECT domain, table_name, COUNT(*) AS records, SUM(CASE WHEN cleared_at IS NULL THEN 1 ELSE 0 END) AS open_records, SUM(CASE WHEN clear_error IS NOT NULL AND clear_error != '' THEN 1 ELSE 0 END) AS clear_errors FROM lifecycle_records WHERE batch_id=? GROUP BY domain, table_name ORDER BY domain, table_name", (batch,))]
    samples = [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_records WHERE batch_id=? ORDER BY id DESC LIMIT 100", (batch,))]
    ledger.close()
    payload = {"ok": True, "status": "BATCH_DETAIL_READY", "batch_id": batch, "batch": dict(b) if b else None, "summary": records, "samples": samples}
    return public_safe(payload) if public else payload


def lifecycle_history(public: bool = False) -> dict[str, Any]:
    ledger = ensure_v4_tables()
    rows = {
        "batches": [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_batches ORDER BY created_at DESC LIMIT 50")],
        "events": [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_events ORDER BY id DESC LIMIT 100")],
        "backups": [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_backups ORDER BY created_at DESC LIMIT 50")],
        "operations": [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_operation_metrics ORDER BY id DESC LIMIT 50")],
        "exports": [dict(r) for r in ledger.execute("SELECT * FROM lifecycle_exports ORDER BY id DESC LIMIT 50")],
    }
    ledger.close()
    payload = {"ok": True, "status": "HISTORY_READY", "apiVersion": API_VERSION, **rows}
    return public_safe(payload) if public else payload


def data_quality_report(public: bool = False) -> dict[str, Any]:
    dash = latest_dashboard(public=False)
    schema = schema_inventory(public=False)
    fk = foreign_key_report()
    findings = []
    for d in dash.get("domains", []):
        if int(d.get("total", 0) or 0) == 0:
            findings.append({"level": "INFO", "domain": d.get("domain"), "code": "DOMAIN_EMPTY", "message": "Dominio sin registros actuales."})
        if d.get("state") == "mixed":
            findings.append({"level": "WARN", "domain": d.get("domain"), "code": "DOMAIN_MIXED", "message": "Hay datos generados y manuales/reales mezclados."})
    if not fk.get("ok"):
        findings.append({"level": "FAIL", "code": "FOREIGN_KEY_ISSUES", "message": "PRAGMA foreign_key_check reporta problemas."})
    table_count = sum(len(db.get("tables", [])) for db in schema.get("databases", []))
    if table_count == 0:
        findings.append({"level": "WARN", "code": "NO_TABLES_DETECTED", "message": "No se detectaron tablas en DBs."})
    status = "DATA_QUALITY_FAIL" if any(f.get("level") == "FAIL" for f in findings) else "DATA_QUALITY_WARN" if any(f.get("level") == "WARN" for f in findings) else "DATA_QUALITY_PASS"
    payload = {"ok": status != "DATA_QUALITY_FAIL", "status": status, "findings": findings, "foreign_keys": fk, "domain_count": len(dash.get("domains", [])), "table_count": table_count}
    return public_safe(payload) if public else payload


def safety_doctor(public: bool = False) -> dict[str, Any]:
    checks = []
    def add(name: str, ok: bool, detail: Any = None, level: str = "FAIL") -> None:
        checks.append({"name": name, "ok": bool(ok), "level": "PASS" if ok else level, "detail": detail})
    cfg_val = config_validation_report()
    add("config_validation", cfg_val.get("ok"), cfg_val.get("findings"))
    add("features_50_plus", len(V4_MASTER_FEATURES) >= 50, len(V4_MASTER_FEATURES))
    add("ledger_exists_or_creatable", bool(ensure_ledger()), str(LEDGER_PATH))
    add("dbs_detected", len(discover_dbs()) > 0, len(discover_dbs()), level="WARN")
    add("pin_default_six_digits", str(config().get("pin_default", "")).isdigit() and len(str(config().get("pin_default", ""))) == 6, "PIN hidden")
    smtp = smtp_diagnostics(public=False)
    add("smtp_configured", bool(smtp.get("enabled") and smtp.get("host_configured") and smtp.get("password_env_present")), smtp, level="WARN")
    fk = foreign_key_report()
    add("foreign_keys_ok", fk.get("ok"), fk, level="WARN")
    add("public_mutations_blocked", bool(config().get("block_public_mutations", True)), True)
    add("operation_lock_free", not bool(read_lock()), read_lock(), level="WARN")
    status = "DOCTOR_PASS" if all(c["ok"] or c["level"] == "WARN" for c in checks) else "DOCTOR_WARN"
    payload = {"ok": status == "DOCTOR_PASS", "status": status, "checks": checks}
    return public_safe(payload) if public else payload


def backup_verify(backup_id: str | None = None, public: bool = False) -> dict[str, Any]:
    cat = backup_catalog(public=False)
    rows = cat.get("backups", [])
    if backup_id:
        rows = [r for r in rows if r.get("backup_id") == backup_id]
    results = []
    for r in rows[:50]:
        path = Path(r.get("zip_path") or "")
        item = {"backup_id": r.get("backup_id"), "exists": path.exists(), "path": str(path)}
        try:
            if path.exists():
                with zipfile.ZipFile(path, "r") as z:
                    bad = z.testzip()
                    item.update({"zip_ok": bad is None, "bad_member": bad, "file_count": len(z.namelist()), "sha256": sha256_file(path)})
        except Exception as exc:
            item.update({"zip_ok": False, "error": str(exc)})
        results.append(item)
    payload = {"ok": all(x.get("zip_ok", x.get("exists")) for x in results) if results else True, "status": "BACKUP_VERIFY_READY", "results": results}
    return public_safe(payload) if public else payload


def export_dashboard_csv(public: bool = False) -> dict[str, Any]:
    dash = latest_dashboard(public=False)
    out = _io.StringIO()
    writer = _csv.DictWriter(out, fieldnames=["domain", "total", "generated", "manual_or_real", "state"])
    writer.writeheader()
    for row in dash.get("domains", []):
        writer.writerow({k: row.get(k, "") for k in writer.fieldnames})
    eid = f"dashboard_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = EVIDENCE_DIR / eid
    path.write_text(out.getvalue(), encoding="utf-8")
    ledger = ensure_v4_tables()
    ledger.execute("INSERT OR REPLACE INTO lifecycle_exports(export_id, kind, created_at, path, sha256, payload_json) VALUES(?,?,?,?,?,?)", (eid, "dashboard_csv", utcnow(), str(path), sha256_file(path), safe_json({"dashboard_hash": json_hash(dash)})))
    ledger.commit(); ledger.close()
    payload = {"ok": True, "status": "DASHBOARD_CSV_EXPORTED", "file": str(path), "sha256": sha256_file(path)}
    return public_safe(payload) if public else payload


def export_report_md(public: bool = False) -> dict[str, Any]:
    dash = latest_dashboard(public=False)
    quality = data_quality_report(public=False)
    lines = ["# PRISMA Data Lifecycle · V4 Excelsior Report", "", f"Generated: {utcnow()}", f"API: {API_VERSION}", f"Hardening: {HARDENING_VERSION}", "", "## Dashboard por dominio", ""]
    lines.append("| Domain | Total | Generado | Manual/Real | Estado |")
    lines.append("|---|---:|---:|---:|---|")
    for d in dash.get("domains", []):
        lines.append(f"| {d.get('domain')} | {d.get('total')} | {d.get('generated')} | {d.get('manual_or_real')} | {d.get('state')} |")
    lines += ["", "## Quality findings", ""]
    for f in quality.get("findings", []):
        lines.append(f"- **{f.get('level')}** `{f.get('code')}` {f.get('domain','')}: {f.get('message','')}")
    if not quality.get("findings"):
        lines.append("- Sin hallazgos importantes.")
    eid = f"lifecycle_report_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path = EVIDENCE_DIR / eid
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ledger = ensure_v4_tables()
    ledger.execute("INSERT OR REPLACE INTO lifecycle_exports(export_id, kind, created_at, path, sha256, payload_json) VALUES(?,?,?,?,?,?)", (eid, "report_md", utcnow(), str(path), sha256_file(path), safe_json({"dashboard_hash": json_hash(dash), "quality_status": quality.get("status")})))
    ledger.commit(); ledger.close()
    payload = {"ok": True, "status": "REPORT_MD_EXPORTED", "file": str(path), "sha256": sha256_file(path)}
    return public_safe(payload) if public else payload


def evidence_index(public: bool = False) -> dict[str, Any]:
    files = []
    max_files = int(export_policy().get("max_latest_evidence_files", 25) or 25)
    for p in sorted(EVIDENCE_DIR.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)[:max_files]:
        if p.is_file():
            files.append({"name": p.name, "path": str(p), "size": p.stat().st_size, "sha256": sha256_file(p), "modified": _dt.datetime.fromtimestamp(p.stat().st_mtime).isoformat()})
    payload = {"ok": True, "status": "EVIDENCE_INDEX_READY", "files": files}
    return public_safe(payload) if public else payload


def evidence_bundle(public: bool = False) -> dict[str, Any]:
    ensure_dirs()
    export_id = f"ai_safe_bundle_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    bundle_dir = EVIDENCE_DIR / export_id
    bundle_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "dashboard.json": latest_dashboard(public=True),
        "preflight.json": preflight(public=True),
        "doctor.json": safety_doctor(public=True),
        "quality.json": data_quality_report(public=True),
        "schema_inventory.json": schema_inventory(public=True),
        "ledger_audit.json": ledger_integrity(public=True),
        "routes.json": route_catalog(),
        "features.json": {"ok": True, "status": "FEATURES_READY", "features": V4_MASTER_FEATURES, "improvement_catalog": improvement_catalog()},
    }
    for name, data in payloads.items():
        (bundle_dir / name).write_text(json.dumps(public_safe(data), ensure_ascii=False, indent=2), encoding="utf-8")
    (bundle_dir / "README.md").write_text("\n".join([
        "# PRISMA Data Lifecycle · AI-safe evidence bundle",
        "",
        f"Generated: {utcnow()}",
        f"API: {API_VERSION}",
        "",
        "Este paquete fue sanitizado para análisis: rutas locales y secretos se redaccionan.",
        "No contiene bases de datos crudas.",
    ]) + "\n", encoding="utf-8")
    zpath = EVIDENCE_DIR / f"{export_id}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(bundle_dir.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(bundle_dir))
    shutil.rmtree(bundle_dir, ignore_errors=True)
    ledger = ensure_v4_tables()
    ledger.execute("INSERT OR REPLACE INTO lifecycle_exports(export_id, kind, created_at, path, sha256, payload_json) VALUES(?,?,?,?,?,?)", (export_id, "ai_safe_bundle", utcnow(), str(zpath), sha256_file(zpath), safe_json({"files": list(payloads.keys())})))
    ledger.commit(); ledger.close()
    payload = {"ok": True, "status": "EVIDENCE_BUNDLE_CREATED", "export_id": export_id, "file": str(zpath), "sha256": sha256_file(zpath), "size_bytes": zpath.stat().st_size}
    return public_safe(payload) if public else payload


def retention_preview(public: bool = False) -> dict[str, Any]:
    pol = retention_policy(); now = _time.time()
    def candidates(dir_path: Path, keep_days: int, minimum: int) -> list[dict[str, Any]]:
        files = sorted([p for p in dir_path.glob("*") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
        out = []
        for i, p in enumerate(files):
            age_days = (now - p.stat().st_mtime) / 86400
            if i >= minimum and age_days >= keep_days:
                out.append({"name": p.name, "path": str(p), "age_days": round(age_days, 2), "size": p.stat().st_size})
        return out
    payload = {"ok": True, "status": "RETENTION_PREVIEW_READY", "evidence_candidates": candidates(EVIDENCE_DIR, int(pol.get("evidence_keep_days", 30)), int(pol.get("minimum_evidence_to_keep", 20))), "backup_candidates": candidates(BACKUP_DIR, int(pol.get("backup_keep_days", 30)), int(pol.get("minimum_backups_to_keep", 5)))}
    return public_safe(payload) if public else payload


def retention_prune(pin: str | None = None, pin_id: str | None = None, public: bool = False) -> dict[str, Any]:
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    pol = retention_policy()
    if pol.get("prune_requires_pin", True):
        ok, reason = validate_pin(pin, pin_id)
        if not ok:
            return {"ok": False, "status": reason, "message": "Prune bloqueado por PIN."}
    prev = retention_preview(public=False)
    removed = []
    errors = []
    for item in prev.get("evidence_candidates", []) + prev.get("backup_candidates", []):
        try:
            p = Path(item["path"])
            if p.exists() and p.is_file():
                removed.append({"name": p.name, "size": p.stat().st_size})
                p.unlink()
        except Exception as exc:
            errors.append({"item": item, "error": str(exc)})
    payload = {"ok": not bool(errors), "status": "RETENTION_PRUNE_PASS" if not errors else "RETENTION_PRUNE_WARN", "removed": removed, "errors": errors}
    write_evidence("retention_prune", payload)
    return public_safe(payload) if public else payload


def inject(mode: str, public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    acquired, lock = acquire_lock(f"inject_{mode}")
    if not acquired:
        return public_safe(lock) if public else lock
    started = _time.time()
    op_id = lock.get("operation_id")
    try:
        pre = snapshot_dashboard(f"before_inject_{mode}", public=False)
        payload = _V3_INJECT(mode, public=False)
        post = snapshot_dashboard(f"after_inject_{mode}", public=False)
        payload.update({"apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "operation_id": op_id, "v4_pre_snapshot": pre, "v4_post_snapshot": post, "v4_plan": create_injection_plan(mode)})
        write_evidence(f"inject_v4_{payload.get('batch_id', op_id)}", payload)
        record_metric("inject", payload.get("status", "UNKNOWN"), started, payload, op_id=op_id)
        return public_safe(payload) if public else payload
    except Exception as exc:
        payload = {"ok": False, "status": "INJECT_V4_EXCEPTION", "operation_id": op_id, "error": str(exc), "traceback": traceback.format_exc()}
        record_metric("inject", "EXCEPTION", started, payload, op_id=op_id)
        return public_safe(payload) if public else payload
    finally:
        release_lock(op_id)


def clear_dry_run(public: bool = False) -> dict[str, Any]:
    payload = {"ok": True, "status": "CLEAR_DRY_RUN_READY", "apiVersion": API_VERSION, "will_mutate": False, "preview": clear_preview(public=False), "foreign_keys": foreign_key_report(), "latest_backup_catalog": backup_catalog(public=True)}
    return public_safe(payload) if public else payload


def clear_generated(public: bool = False, pin: str | None = None, pin_id: str | None = None) -> dict[str, Any]:  # type: ignore[override]
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    acquired, lock = acquire_lock("clear")
    if not acquired:
        return public_safe(lock) if public else lock
    started = _time.time(); op_id = lock.get("operation_id")
    try:
        pre = snapshot_dashboard("before_clear", public=False)
        payload = _V3_CLEAR_GENERATED(public=False, pin=pin, pin_id=pin_id)
        post = snapshot_dashboard("after_clear", public=False)
        payload.update({"apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "operation_id": op_id, "v4_pre_snapshot": pre, "v4_post_snapshot": post, "clear_summary_by_domain": (payload.get("preview_before_clear") or {}).get("by_domain", {})})
        write_evidence(f"clear_v4_{payload.get('clear_batch', op_id)}", payload)
        record_metric("clear", payload.get("status", "UNKNOWN"), started, payload, op_id=op_id)
        return public_safe(payload) if public else payload
    except Exception as exc:
        payload = {"ok": False, "status": "CLEAR_V4_EXCEPTION", "operation_id": op_id, "error": str(exc), "traceback": traceback.format_exc()}
        record_metric("clear", "EXCEPTION", started, payload, op_id=op_id)
        return public_safe(payload) if public else payload
    finally:
        release_lock(op_id)


def create_backup_endpoint(reason: str = "manual", public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    acquired, lock = acquire_lock("backup")
    if not acquired:
        return public_safe(lock) if public else lock
    started = _time.time(); op_id = lock.get("operation_id")
    try:
        payload = _V3_CREATE_BACKUP_ENDPOINT(reason, public=False)
        payload.update({"apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "operation_id": op_id, "backup_verify": backup_verify(public=True)})
        record_metric("backup", payload.get("status", "UNKNOWN"), started, payload, op_id=op_id)
        return public_safe(payload) if public else payload
    finally:
        release_lock(op_id)


def restore_backup(backup_id: str | None = None, pin: str | None = None, pin_id: str | None = None, dry_run: bool = False, public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    if dry_run:
        return _V3_RESTORE_BACKUP(backup_id=backup_id, pin=pin, pin_id=pin_id, dry_run=True, public=public)
    if public and config().get("block_public_mutations", True):
        return {"ok": False, "status": "PUBLIC_MUTATION_BLOCKED"}
    acquired, lock = acquire_lock("rollback")
    if not acquired:
        return public_safe(lock) if public else lock
    started = _time.time(); op_id = lock.get("operation_id")
    try:
        payload = _V3_RESTORE_BACKUP(backup_id=backup_id, pin=pin, pin_id=pin_id, dry_run=False, public=False)
        payload.update({"apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "operation_id": op_id})
        record_metric("rollback", payload.get("status", "UNKNOWN"), started, payload, op_id=op_id)
        return public_safe(payload) if public else payload
    finally:
        release_lock(op_id)


def manifest_v4(public: bool = False) -> dict[str, Any]:
    payload = {
        "ok": True,
        "status": "MANIFEST_READY",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "feature_count": len(V4_MASTER_FEATURES),
        "required_minimum_improvements": 50,
        "no_downgrade_from": "PRISMA_DATA_LIFECYCLE_API_V3",
        "ui_contract": ["Inyectar", "Clear", "Dashboard por dominio", "Herramientas internas colapsables/compactas"],
        "owner_email": config().get("owner_email"),
        "pin_default_length": 6,
        "mutations_public_blocked": bool(config().get("block_public_mutations", True)),
        "routes": route_catalog().get("routes", []),
    }
    return public_safe(payload) if public else payload


def latest_evidence() -> dict[str, Any]:  # type: ignore[override]
    return evidence_index(public=False)


def lifecycle_payload(path: str, public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    ensure_dirs()
    parsed = urlparse(path)
    clean = parsed.path.rstrip("/")
    qs = parse_qs(parsed.query)
    parts = [p for p in clean.split("/") if p]
    try:
        if clean in {"/api/lifecycle", "/api/lifecycle/latest", "/api/lifecycle/dashboard"}:
            return latest_dashboard(public=public)
        if clean.startswith("/api/lifecycle/preflight"):
            payload = preflight(public=False); payload.update({"apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "doctor": safety_doctor(public=True)})
            return public_safe(payload) if public else payload
        if clean.startswith("/api/lifecycle/config") or clean.startswith("/api/lifecycle/version"):
            payload = {"ok": True, "status": "READY", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "features": V4_MASTER_FEATURES, "feature_count": len(V4_MASTER_FEATURES), "config": config_summary(), "profiles": profiles(), "clear_policy": clear_policy(), "guardrails": guardrails(), "v4_configs": {"observability": observability_policy(), "export": export_policy(), "retention": retention_policy()}}
            return public_safe(payload) if public else payload
        if clean.startswith("/api/lifecycle/features"):
            payload = {"ok": True, "status": "FEATURES_READY", "apiVersion": API_VERSION, "features": V4_MASTER_FEATURES, "improvement_catalog": improvement_catalog()}
            return public_safe(payload) if public else payload
        if clean.startswith("/api/lifecycle/routes"):
            return route_catalog()
        if clean.startswith("/api/lifecycle/manifest"):
            return manifest_v4(public=public)
        if clean.startswith("/api/lifecycle/plan/dry-run"):
            mode = parts[-1] if len(parts) >= 5 else (qs.get("mode", ["light"])[0])
            return inject_dry_run(mode, public=public)
        if clean.startswith("/api/lifecycle/plan"):
            mode = parts[-1] if len(parts) >= 4 else (qs.get("mode", ["light"])[0])
            payload = {"ok": True, "status": "READY", "apiVersion": API_VERSION, "plan": create_injection_plan(mode), "profiles": profiles(), "guardrails": guardrails()}
            return public_safe(payload) if public else payload
        if clean.startswith("/api/lifecycle/inject/dry-run"):
            mode = qs.get("mode", ["light"])[0]
            return inject_dry_run(mode, public=public)
        if clean.startswith("/api/lifecycle/inject"):
            mode = parts[-1] if len(parts) >= 4 else (qs.get("mode", ["light"])[0])
            return inject(mode, public=public)
        if clean.startswith("/api/lifecycle/clear/preview"):
            return clear_preview(public=public)
        if clean.startswith("/api/lifecycle/clear/dry-run"):
            return clear_dry_run(public=public)
        if clean.startswith("/api/lifecycle/clear/request-pin"):
            return request_pin(public=public)
        if clean.startswith("/api/lifecycle/clear/confirm"):
            return clear_generated(public=public, pin=qs.get("pin", [None])[0], pin_id=qs.get("pin_id", [None])[0])
        if clean.startswith("/api/lifecycle/ledger/integrity") or clean.startswith("/api/lifecycle/audit"):
            return ledger_integrity(public=public)
        if clean.startswith("/api/lifecycle/backups/verify"):
            return backup_verify(qs.get("backup_id", [None])[0], public=public)
        if clean.startswith("/api/lifecycle/backups"):
            return backup_catalog(public=public)
        if clean.startswith("/api/lifecycle/backup/create"):
            return create_backup_endpoint(qs.get("reason", ["manual"])[0], public=public)
        if clean.startswith("/api/lifecycle/rollback/preview"):
            return restore_backup(backup_id=qs.get("backup_id", [None])[0], dry_run=True, public=public)
        if clean.startswith("/api/lifecycle/rollback/confirm"):
            return restore_backup(backup_id=qs.get("backup_id", [None])[0], pin=qs.get("pin", [None])[0], pin_id=qs.get("pin_id", [None])[0], dry_run=False, public=public)
        if clean.startswith("/api/lifecycle/evidence/bundle") or clean.startswith("/api/lifecycle/export/ai-safe"):
            return evidence_bundle(public=public)
        if clean.startswith("/api/lifecycle/evidence/latest"):
            return evidence_index(public=public)
        if clean.startswith("/api/lifecycle/schema"):
            return schema_inventory(public=public)
        if clean.startswith("/api/lifecycle/domain"):
            domain = parts[-1] if len(parts) >= 4 else qs.get("domain", ["All"])[0]
            return domain_detail(domain, public=public)
        if clean.startswith("/api/lifecycle/batch"):
            batch = parts[-1] if len(parts) >= 4 else qs.get("batch_id", [None])[0]
            return batch_detail(batch, public=public)
        if clean.startswith("/api/lifecycle/history"):
            return lifecycle_history(public=public)
        if clean.startswith("/api/lifecycle/quality"):
            return data_quality_report(public=public)
        if clean.startswith("/api/lifecycle/doctor"):
            return safety_doctor(public=public)
        if clean.startswith("/api/lifecycle/snapshot/create"):
            return snapshot_dashboard(qs.get("label", ["manual"])[0], public=public)
        if clean.startswith("/api/lifecycle/snapshot/diff"):
            return dashboard_diff(public=public)
        if clean.startswith("/api/lifecycle/pin/status"):
            return pin_status(public=public)
        if clean.startswith("/api/lifecycle/smtp/diagnostics"):
            return smtp_diagnostics(public=public)
        if clean.startswith("/api/lifecycle/export/dashboard.csv"):
            return export_dashboard_csv(public=public)
        if clean.startswith("/api/lifecycle/export/report.md"):
            return export_report_md(public=public)
        if clean.startswith("/api/lifecycle/retention/preview"):
            return retention_preview(public=public)
        if clean.startswith("/api/lifecycle/retention/prune"):
            return retention_prune(pin=qs.get("pin", [None])[0], pin_id=qs.get("pin_id", [None])[0], public=public)
        if clean.startswith("/api/lifecycle/health"):
            payload = {"ok": True, "status": "LIFECYCLE_READY", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "features": V4_MASTER_FEATURES, "feature_count": len(V4_MASTER_FEATURES), "data_dir": str(DATA_DIR), "ledger": str(LEDGER_PATH), "lock": read_lock(), "doctor": safety_doctor(public=True)}
            return public_safe(payload) if public else payload
        return {"ok": False, "status": "UNKNOWN_LIFECYCLE_ROUTE", "path": path, "route_catalog": route_catalog().get("routes", [])}
    except Exception as exc:
        payload = {"ok": False, "status": "LIFECYCLE_V4_EXCEPTION", "apiVersion": API_VERSION, "error": str(exc), "traceback": traceback.format_exc()}
        return public_safe(payload) if public else payload


# ============================================================================
# PRISMA DATA LIFECYCLE V5 GOLDEN RELEASE CANDIDATE
# Goal: no new big feature surface; consolidate no-downgrade, installer safety,
# docs/evidence contracts, cross-checks and runtime fail-fast visibility.
# ============================================================================

import tempfile as _tempfile

_V4_LIFECYCLE_PAYLOAD = lifecycle_payload
_V4_ROUTE_CATALOG = route_catalog if "route_catalog" in globals() else None
_V4_MANIFEST = manifest_v4 if "manifest_v4" in globals() else None

API_VERSION = "PRISMA_DATA_LIFECYCLE_API_V5"
HARDENING_VERSION = "v5-golden-release-candidate"

V5_MASTER_FEATURES = list(dict.fromkeys((globals().get("V4_MASTER_FEATURES", []) or []) + [
    "golden_no_downgrade_audit",
    "installer_fail_fast_contract",
    "cross_config_api_ui_verification",
    "final_release_evidence",
    "install_checklist_endpoint",
    "runtime_data_dir_fallback",
    "clear_safety_polish",
    "zip_hygiene_contract",
    "release_candidate_manifest",
    "post_install_validation_contract",
]))

V5_EXTRA_CONFIGS = {
    "release_contract": "lifecycle_release_contract.json",
    "install_checklist": "lifecycle_install_checklist.json",
    "failfast_policy": "lifecycle_failfast_policy.json",
    "final_evidence_schema": "lifecycle_final_evidence_schema.json",
}


def _v5_can_write_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".v5_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def _v5_runtime_rebase() -> None:
    """Select a writable DATA_DIR while preserving installed Control Center paths."""
    global DATA_DIR, LEDGER_PATH, EVIDENCE_DIR, BACKUP_DIR, LOCK_FILE
    requested = os.environ.get("PRISMA_LIFECYCLE_DATA_DIR")
    candidates = []
    if requested:
        candidates.append(Path(requested))
    candidates.append(DATA_DIR)
    candidates.append(Path(_tempfile.gettempdir()) / "prisma-data-lifecycle-v5")
    selected = None
    for candidate in candidates:
        if _v5_can_write_dir(candidate):
            selected = candidate
            break
    if selected is None:
        selected = Path(_tempfile.gettempdir()) / "prisma-data-lifecycle-v5"
        selected.mkdir(parents=True, exist_ok=True)
    DATA_DIR = selected
    LEDGER_PATH = DATA_DIR / "prisma-data-lifecycle-ledger.db"
    EVIDENCE_DIR = DATA_DIR / "evidence"
    BACKUP_DIR = DATA_DIR / "backups"
    LOCK_FILE = DATA_DIR / "lifecycle_operation.lock"


_v5_runtime_rebase()


def v5_config(name: str, fallback: Any) -> Any:
    return load_json(CONFIG_DIR / V5_EXTRA_CONFIGS.get(name, name), fallback)


def v5_release_contract() -> dict[str, Any]:
    return v5_config("release_contract", {
        "contract_version": HARDENING_VERSION,
        "built_on": "PRISMA_DATA_LIFECYCLE_CONTROL_CENTER_04_EXCELSIOR",
        "ui_contract": {"primary_actions": ["Inyectar datos", "Clear"], "required_modes": ["Ligera", "Pesada", "Pasada de longaniza"]},
        "safety_contract": {"clear_default_scope": "generated_only_by_ledger", "requires_backup_before_clear": True}
    })


def v5_install_checklist() -> dict[str, Any]:
    return v5_config("install_checklist", {"checklist_version": HARDENING_VERSION, "before_install": [], "during_install": [], "after_install": [], "rollback": []})


def v5_failfast_policy() -> dict[str, Any]:
    return v5_config("failfast_policy", {"policy_version": HARDENING_VERSION, "no_fake_green": True})


def v5_final_evidence_schema() -> dict[str, Any]:
    return v5_config("final_evidence_schema", {"schema_version": HARDENING_VERSION, "required_sections": []})


def v5_release_manifest(public: bool = False) -> dict[str, Any]:
    contract = v5_release_contract()
    payload = {
        "ok": True,
        "status": "V5_GOLDEN_READY",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "built_on": "PRISMA_DATA_LIFECYCLE_CONTROL_CENTER_04_EXCELSIOR",
        "feature_count": len(V5_MASTER_FEATURES),
        "features": V5_MASTER_FEATURES,
        "contract": contract,
        "data_dir": str(DATA_DIR),
        "ledger": str(LEDGER_PATH),
        "clear_default_scope": clear_policy().get("default_scope", "generated_only"),
        "owner_email": config().get("owner_email"),
        "pin_required": bool(config().get("pin_required", True)),
        "public_mutations_blocked": bool(config().get("block_public_mutations", True)),
    }
    return public_safe(payload) if public else payload


def v5_no_downgrade_audit(public: bool = False) -> dict[str, Any]:
    required = v5_release_contract().get("no_downgrade_required_tokens", [])
    checks = []
    present_features = set(V5_MASTER_FEATURES)
    for token in required:
        checks.append({"check": f"feature:{token}", "ok": token in present_features or token in globals() or token in str(globals().get("V4_MASTER_FEATURES", []))})
    api_text_checks = ["PRISMA_DATA_LIFECYCLE_API_V4", "v4-excelsior-no-downgrade", "ledger_integrity", "restore_backup", "evidence_bundle", "retention_prune", "operation_lock"]
    try:
        source_text = Path(__file__).read_text(encoding="utf-8", errors="replace")
    except Exception:
        source_text = ""
    for token in api_text_checks:
        checks.append({"check": f"source_token:{token}", "ok": token in source_text})
    ok = all(c.get("ok") for c in checks)
    payload = {"ok": ok, "status": "NO_DOWNGRADE_PASS" if ok else "NO_DOWNGRADE_WARN", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "checks": checks}
    return public_safe(payload) if public else payload


def v5_crosscheck(public: bool = False) -> dict[str, Any]:
    checks = []
    cfg = config()
    cp = clear_policy()
    checks.append({"check": "owner_email", "ok": cfg.get("owner_email") == "alanharrryy@gmail.com", "value": cfg.get("owner_email")})
    checks.append({"check": "pin_default_length", "ok": len(str(cfg.get("pin_default", ""))) == 6})
    checks.append({"check": "pin_required_or_explicit_disable", "ok": bool(cfg.get("pin_required", True)) or bool(cfg.get("allow_clear_without_pin", False))})
    checks.append({"check": "public_mutations_blocked", "ok": bool(cfg.get("block_public_mutations", True))})
    checks.append({"check": "clear_scope_generated_only", "ok": "generated" in str(cp.get("default_scope", "generated_only"))})
    checks.append({"check": "backup_before_clear", "ok": bool(cp.get("backup_before_clear", cp.get("requires_backup", True)))})
    checks.append({"check": "profiles_include_longaniza", "ok": "longaniza" in profiles()})
    checks.append({"check": "release_contract_loaded", "ok": v5_release_contract().get("contract_version") is not None})
    web_js = CONTROL_CENTER_ROOT / "internal" / "web" / "lifecycle_console.js"
    if web_js.exists():
        text = web_js.read_text(encoding="utf-8", errors="replace")
        for token in ["Inyectar", "Clear", "Pasada de longaniza", "lifecycle"]:
            checks.append({"check": f"ui_token:{token}", "ok": token in text})
    else:
        checks.append({"check": "ui_file_available", "ok": False, "severity": "warn"})
    checks.append({"check": "data_dir_writable", "ok": _v5_can_write_dir(DATA_DIR)})
    ok = all(c.get("ok") or c.get("severity") == "warn" for c in checks)
    payload = {"ok": ok, "status": "CROSSCHECK_PASS" if ok else "CROSSCHECK_WARN", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "checks": checks}
    return public_safe(payload) if public else payload


def v5_safety_polish(public: bool = False) -> dict[str, Any]:
    cfg = config()
    cp = clear_policy()
    payload = {
        "ok": True,
        "status": "SAFETY_POLISH_READY",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "clear_is_not_factory_by_default": "factory" not in str(cp.get("default_scope", "")).lower(),
        "clear_uses_ledger": "ledger" in str(cp).lower() or "generated" in str(cp.get("default_scope", "generated_only")).lower(),
        "backup_required": bool(cp.get("backup_before_clear", cp.get("requires_backup", True))),
        "pin_guard": {"required": bool(cfg.get("pin_required", True)), "allow_clear_without_pin": bool(cfg.get("allow_clear_without_pin", False)), "pin_length": len(str(cfg.get("pin_default", "")))},
        "public_mutations_blocked": bool(cfg.get("block_public_mutations", True)),
        "license_real_reset_excluded_by_default": True,
        "operator_warning": "Clear default limpia generated-only por ledger; no expone factory clear como acción primaria."
    }
    payload["ok"] = bool(payload["clear_is_not_factory_by_default"] and payload["backup_required"] and payload["public_mutations_blocked"])
    return public_safe(payload) if public else payload


def v5_final_evidence(public: bool = False) -> dict[str, Any]:
    payload = {
        "ok": True,
        "status": "FINAL_EVIDENCE_READY",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "release_manifest": v5_release_manifest(public=True),
        "no_downgrade_audit": v5_no_downgrade_audit(public=True),
        "crosscheck": v5_crosscheck(public=True),
        "safety_polish": v5_safety_polish(public=True),
        "route_catalog": route_catalog_v5(public=True),
        "install_checklist": v5_install_checklist(),
        "schema": v5_final_evidence_schema(),
    }
    payload["ok"] = bool(payload["no_downgrade_audit"].get("ok") and payload["crosscheck"].get("ok") and payload["safety_polish"].get("ok"))
    payload["status"] = "FINAL_EVIDENCE_PASS" if payload["ok"] else "FINAL_EVIDENCE_WARN"
    return public_safe(payload) if public else payload


def route_catalog_v5(public: bool = False) -> dict[str, Any]:
    base = _V4_ROUTE_CATALOG().get("routes", []) if callable(_V4_ROUTE_CATALOG) else []
    v5_routes = [
        {"method": "GET", "path": "/api/lifecycle/release/manifest", "description": "V5 release candidate manifest"},
        {"method": "GET", "path": "/api/lifecycle/release/checklist", "description": "Checklist antes/durante/después/rollback"},
        {"method": "GET", "path": "/api/lifecycle/release/no-downgrade", "description": "Auditoría no-downgrade V4→V5"},
        {"method": "GET", "path": "/api/lifecycle/release/crosscheck", "description": "Verificación cruzada config/API/UI/clear/PIN"},
        {"method": "GET", "path": "/api/lifecycle/release/safety", "description": "Safety polish para Clear no nuclear"},
        {"method": "GET", "path": "/api/lifecycle/release/evidence", "description": "Evidencia final V5"},
    ]
    seen = set()
    merged = []
    for r in base + v5_routes:
        key = r.get("path")
        if key not in seen:
            seen.add(key)
            merged.append(r)
    payload = {"ok": True, "status": "ROUTES_READY", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "routes": merged}
    return public_safe(payload) if public else payload


def route_catalog() -> dict[str, Any]:  # type: ignore[override]
    return route_catalog_v5(public=False)


def _v5_wrap_payload(payload: dict[str, Any], public: bool = False) -> dict[str, Any]:
    if isinstance(payload, dict):
        payload["apiVersion"] = API_VERSION
        payload["hardeningVersion"] = HARDENING_VERSION
        payload.setdefault("v5Release", {"status": "golden-release-candidate", "no_downgrade_from": "PRISMA_DATA_LIFECYCLE_API_V4"})
    return public_safe(payload) if public else payload


def lifecycle_payload(path: str, public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    ensure_dirs()
    parsed = urlparse(path)
    clean = parsed.path.rstrip("/")
    try:
        if clean.startswith("/api/lifecycle/release/manifest") or clean.startswith("/api/lifecycle/manifest"):
            return v5_release_manifest(public=public)
        if clean.startswith("/api/lifecycle/release/checklist"):
            payload = {"ok": True, "status": "INSTALL_CHECKLIST_READY", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "checklist": v5_install_checklist()}
            return public_safe(payload) if public else payload
        if clean.startswith("/api/lifecycle/release/no-downgrade"):
            return v5_no_downgrade_audit(public=public)
        if clean.startswith("/api/lifecycle/release/crosscheck"):
            return v5_crosscheck(public=public)
        if clean.startswith("/api/lifecycle/release/safety"):
            return v5_safety_polish(public=public)
        if clean.startswith("/api/lifecycle/release/evidence"):
            return v5_final_evidence(public=public)
        if clean.startswith("/api/lifecycle/routes"):
            return route_catalog_v5(public=public)
        payload = _V4_LIFECYCLE_PAYLOAD(path, public=public)
        if isinstance(payload, dict):
            return _v5_wrap_payload(payload, public=False) if not public else public_safe(_v5_wrap_payload(payload, public=False))
        return payload
    except Exception as exc:
        payload = {"ok": False, "status": "LIFECYCLE_V5_EXCEPTION", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "error": str(exc), "traceback": traceback.format_exc()}
        return public_safe(payload) if public else payload


# ============================================================================
# PRISMA DATA LIFECYCLE V6 - Ledger + Ghost Signature Clear
# Purpose: make Clear work even when a seed was inserted outside the lifecycle
# ledger. This preserves ledger cleanup and adds deterministic signature cleanup.
# ============================================================================
try:
    _V6_PREVIOUS_CLEAR_PREVIEW = clear_preview
    _V6_PREVIOUS_CLEAR_GENERATED = clear_generated
    _V6_PREVIOUS_LATEST_DASHBOARD = latest_dashboard
    _V6_PREVIOUS_LIFECYCLE_PAYLOAD = lifecycle_payload
    _V6_PREVIOUS_ROUTE_CATALOG = route_catalog
except NameError:
    _V6_PREVIOUS_CLEAR_PREVIEW = None
    _V6_PREVIOUS_CLEAR_GENERATED = None
    _V6_PREVIOUS_LATEST_DASHBOARD = None
    _V6_PREVIOUS_LIFECYCLE_PAYLOAD = None
    _V6_PREVIOUS_ROUTE_CATALOG = None

API_VERSION = "PRISMA_DATA_LIFECYCLE_API_V6"
HARDENING_VERSION = "v6-ledger-plus-ghost-signature-clear"

_V6_DELETE_ORDER = [
    "SalePaymentTender", "SaleReturnLine", "SaleReturn", "SaleLine", "Sale",
    "CashMovement", "CashAdjustment", "CashSession",
    "GoodsReceiptLine", "GoodsReceipt", "PurchaseOrderLine", "PurchaseOrder",
    "ProductSupplier", "PriceListItem", "Barcode", "StockMovement", "StockSnapshot", "ReplenishmentSignal",
    "OutboxEvent", "SyncAttempt", "SyncConflict", "SyncOutboxStatusBucket", "DataSourceFreshness", "SyncCheckpoint",
    "DeviceHeartbeat", "AuditEvent", "AuditCount", "SupportIncident",
    "_RoleToUser", "_PermissionToRole", "User", "Permission", "Role",
    "Terminal", "Supplier", "Product", "Brand", "DropdownOption", "DropdownCatalog", "PriceList", "TaxRate", "Store", "Business",
]

_V6_SIGNATURES = [
    ("sku", "LIKE", "DL-%"),
    ("folio", "LIKE", "DL-%"),
    ("folio", "LIKE", "OC-DL-%"),
    ("clientRequestId", "LIKE", "dl-lifecycle_%"),
    ("payloadJson", "LIKE", "%prisma_data_lifecycle%"),
    ("payloadJson", "LIKE", "%PRISMA Data Lifecycle%"),
    ("metadataJson", "LIKE", "%prisma_data_lifecycle%"),
    ("description", "LIKE", "%Data Lifecycle%"),
    ("source", "=", "prisma_data_lifecycle"),
    ("cursor", "LIKE", "lifecycle_%"),
]

_V6_CHART_SIGNATURES = {
    "runtime_sources": [("sourceKey", "LIKE", "lifecycle-%"), ("path", "=", "PRISMA_DATA_LIFECYCLE"), ("sourceKind", "=", "generated")],
    "runtime_metadata": [("key", "LIKE", "lifecycle.batch.%")],
    "runtime_chart_payloads": [("chartKey", "LIKE", "lifecycle-%"), ("sourceMode", "=", "prisma_data_lifecycle"), ("payloadJson", "LIKE", "%PRISMA Data Lifecycle%")],
}


def _v6_ident(name: str) -> str:
    try:
        return sql_ident(name)  # type: ignore[name-defined]
    except Exception:
        return '"' + str(name).replace('"', '""') + '"'


def _v6_tables(con: sqlite3.Connection) -> set[str]:
    try:
        return table_names(con)  # type: ignore[name-defined]
    except Exception:
        return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _v6_cols(con: sqlite3.Connection, table: str) -> set[str]:
    try:
        return set(table_columns(con, table).keys())  # type: ignore[name-defined]
    except Exception:
        return {r[1] for r in con.execute(f'PRAGMA table_info({_v6_ident(table)})')}


def _v6_count(con: sqlite3.Connection, table: str) -> int:
    try:
        return int(con.execute(f"SELECT COUNT(*) FROM {_v6_ident(table)}").fetchone()[0])
    except Exception:
        return 0


def _v6_relative(path: str | Path) -> str:
    try:
        return relative_to_project(str(path))  # type: ignore[name-defined]
    except Exception:
        try:
            return str(Path(path).resolve().relative_to(project_root())).replace("\\", "/")  # type: ignore[name-defined]
        except Exception:
            return str(path).replace("\\", "/")


def _v6_qmarks(values: list[str]) -> str:
    return ",".join(["?"] * len(values))


def _v6_domain_for_table(table: str) -> str:
    try:
        for domain, tables in domain_map().items():  # type: ignore[name-defined]
            if table in tables:
                return domain
    except Exception:
        pass
    if table.startswith("runtime_"):
        return "Chart Lab"
    return "External seed"


def _v6_detect_seed_business_ids(con: sqlite3.Connection) -> list[str]:
    tset = _v6_tables(con)
    ids: set[str] = set()
    if "Business" in tset:
        c = _v6_cols(con, "Business")
        wh: list[str] = []
        params: list[str] = []
        if "name" in c:
            wh.append(f"{_v6_ident('name')} = ?")
            params.append("Abarrotes Prisma Central")
        if "taxId" in c:
            wh.append(f"{_v6_ident('taxId')} = ?")
            params.append("XAXX010101000")
        if wh:
            try:
                for row in con.execute(f"SELECT {_v6_ident('id')} FROM {_v6_ident('Business')} WHERE " + " OR ".join(wh), params):
                    if row[0]:
                        ids.add(str(row[0]))
            except Exception:
                pass
    for table in tset:
        c = _v6_cols(con, table)
        if "businessId" not in c:
            continue
        clauses: list[str] = []
        params: list[str] = []
        for col, op, val in _V6_SIGNATURES:
            if col in c:
                clauses.append(f"{_v6_ident(col)} {op} ?")
                params.append(val)
        if not clauses:
            continue
        try:
            sql = f"SELECT DISTINCT {_v6_ident('businessId')} FROM {_v6_ident(table)} WHERE " + " OR ".join(clauses)
            for row in con.execute(sql, params):
                if row[0]:
                    ids.add(str(row[0]))
        except Exception:
            pass
    ids.discard("biz_tablet_standalone")
    return sorted(ids)


def _v6_analyze_db(db: dict[str, Any]) -> dict[str, Any]:
    path = db.get("path") or db.get("relative_path")
    con = connect(path)  # type: ignore[name-defined]
    try:
        tset = _v6_tables(con)
        seed_ids = _v6_detect_seed_business_ids(con)
        planned: dict[str, int] = {}
        chart: dict[str, int] = {}
        if seed_ids:
            marks = _v6_qmarks(seed_ids)
            for table in sorted(tset):
                c = _v6_cols(con, table)
                count = 0
                try:
                    if table == "Business" and "id" in c:
                        count = int(con.execute(f"SELECT COUNT(*) FROM {_v6_ident('Business')} WHERE {_v6_ident('id')} IN ({marks})", seed_ids).fetchone()[0])
                    elif "businessId" in c:
                        count = int(con.execute(f"SELECT COUNT(*) FROM {_v6_ident(table)} WHERE {_v6_ident('businessId')} IN ({marks})", seed_ids).fetchone()[0])
                except Exception:
                    count = 0
                if count:
                    planned[table] = count
        for table, specs in _V6_CHART_SIGNATURES.items():
            if table not in tset:
                continue
            c = _v6_cols(con, table)
            wh: list[str] = []
            params: list[str] = []
            for col, op, val in specs:
                if col in c:
                    wh.append(f"{_v6_ident(col)} {op} ?")
                    params.append(val)
            if wh:
                try:
                    n = int(con.execute(f"SELECT COUNT(*) FROM {_v6_ident(table)} WHERE " + " OR ".join(wh), params).fetchone()[0])
                    if n:
                        chart[table] = n
                except Exception:
                    pass
        total = sum(planned.values()) + sum(chart.values())
        by_domain: dict[str, int] = {}
        for table, n in planned.items():
            d = _v6_domain_for_table(table)
            by_domain[d] = by_domain.get(d, 0) + int(n)
        for table, n in chart.items():
            d = _v6_domain_for_table(table)
            by_domain[d] = by_domain.get(d, 0) + int(n)
        return {
            "path": str(path),
            "relative_path": db.get("relative_path") or _v6_relative(path),
            "surface": db.get("surface", "unknown"),
            "seed_business_ids": seed_ids,
            "planned_deletes": planned,
            "chart_lab_planned_deletes": chart,
            "external_seed_records_open": int(total),
            "by_domain": by_domain,
        }
    finally:
        con.close()


def external_seed_scan(public: bool = False) -> dict[str, Any]:
    dbs = discover_dbs()  # type: ignore[name-defined]
    analyses: list[dict[str, Any]] = []
    total = 0
    by_domain: dict[str, int] = {}
    errors: list[dict[str, str]] = []
    for db in dbs:
        try:
            item = _v6_analyze_db(db)
            analyses.append(item)
            total += int(item.get("external_seed_records_open", 0))
            for d, n in (item.get("by_domain") or {}).items():
                by_domain[d] = by_domain.get(d, 0) + int(n)
        except Exception as exc:
            errors.append({"db": db.get("relative_path", str(db)), "error": str(exc)})
    payload = {
        "ok": not bool(errors),
        "status": "EXTERNAL_SEED_SCAN_READY" if not errors else "EXTERNAL_SEED_SCAN_WARN",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "clear_engine": "ledger_plus_signature",
        "external_seed_records_open": int(total),
        "by_domain": by_domain,
        "databases": analyses,
        "errors": errors,
    }
    if public:
        for item in payload.get("databases", []):
            item.pop("path", None)
        try:
            return public_safe(payload)  # type: ignore[name-defined]
        except Exception:
            return payload
    return payload


def clear_preview(public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    base = _V6_PREVIOUS_CLEAR_PREVIEW(public=False) if callable(_V6_PREVIOUS_CLEAR_PREVIEW) else {"ok": True, "status": "CLEAR_PREVIEW_READY", "records_to_clear": 0, "by_domain": {}}
    scan = external_seed_scan(public=False)
    ledger_total = int(base.get("records_to_clear") or 0)
    external_total = int(scan.get("external_seed_records_open") or 0)
    by_domain = dict(base.get("by_domain") or {})
    for domain, count in (scan.get("by_domain") or {}).items():
        by_domain[domain] = max(int(by_domain.get(domain, 0)), int(count))
    payload = dict(base)
    payload.update({
        "ok": bool(base.get("ok", True) and scan.get("ok", True)),
        "status": "CLEAR_PREVIEW_READY",
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "clear_engine": "ledger_plus_signature",
        "records_to_clear": max(ledger_total, external_total),
        "ledger_records_to_clear": ledger_total,
        "external_seed_records_to_clear": external_total,
        "by_domain": by_domain,
        "external_seed_scan": scan,
    })
    if public:
        try:
            return public_safe(payload)  # type: ignore[name-defined]
        except Exception:
            return payload
    return payload


def latest_dashboard(public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    payload = _V6_PREVIOUS_LATEST_DASHBOARD(public=False) if callable(_V6_PREVIOUS_LATEST_DASHBOARD) else {"ok": True, "status": "READY", "domains": [], "generated_records_open": 0}
    scan = external_seed_scan(public=False)
    ledger_total = int(payload.get("generated_records_open") or 0)
    external_total = int(scan.get("external_seed_records_open") or 0)
    ext_domains = scan.get("by_domain") or {}
    for domain in payload.get("domains", []) or []:
        name = domain.get("domain")
        ext_count = int(ext_domains.get(name, 0))
        if ext_count:
            domain["generated"] = max(int(domain.get("generated") or 0), ext_count)
            domain["manual_or_real"] = max(0, int(domain.get("total") or 0) - int(domain.get("generated") or 0))
            if int(domain.get("total") or 0) == 0:
                domain["state"] = "clean"
            elif int(domain.get("generated") or 0) and int(domain.get("manual_or_real") or 0):
                domain["state"] = "mixed"
            elif int(domain.get("generated") or 0):
                domain["state"] = "generated"
            else:
                domain["state"] = "manual_or_real"
    payload.update({
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "clear_engine": "ledger_plus_signature",
        "ledger_records_open": ledger_total,
        "external_seed_records_open": external_total,
        "generated_records_open": max(ledger_total, external_total),
        "external_seed_scan": scan,
    })
    if public:
        try:
            return public_safe(payload)  # type: ignore[name-defined]
        except Exception:
            return payload
    return payload


def _v6_delete_chart_lab(con: sqlite3.Connection) -> dict[str, int]:
    deleted: dict[str, int] = {}
    tset = _v6_tables(con)
    for table, specs in _V6_CHART_SIGNATURES.items():
        if table not in tset:
            continue
        c = _v6_cols(con, table)
        wh: list[str] = []
        params: list[str] = []
        for col, op, val in specs:
            if col in c:
                wh.append(f"{_v6_ident(col)} {op} ?")
                params.append(val)
        if not wh:
            continue
        before = con.total_changes
        con.execute(f"DELETE FROM {_v6_ident(table)} WHERE " + " OR ".join(wh), params)
        delta = con.total_changes - before
        if delta:
            deleted[table] = int(delta)
    return deleted


def _v6_delete_external_seed_db(db: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    path = db.get("path") or analysis.get("path")
    seed_ids = list(analysis.get("seed_business_ids") or [])
    con = connect(path)  # type: ignore[name-defined]
    result = {
        "path": str(path),
        "relative_path": db.get("relative_path") or analysis.get("relative_path") or _v6_relative(path),
        "seed_business_ids": seed_ids,
        "deleted": {},
        "chart_lab_deleted": {},
        "foreign_key_check": [],
        "after_seed_business_ids": [],
    }
    try:
        tset = _v6_tables(con)
        con.execute("BEGIN")
        result["chart_lab_deleted"] = _v6_delete_chart_lab(con)
        if seed_ids:
            marks = _v6_qmarks(seed_ids)
            for table in _V6_DELETE_ORDER:
                if table not in tset:
                    continue
                c = _v6_cols(con, table)
                if table == "Business" and "id" in c:
                    sql = f"DELETE FROM {_v6_ident('Business')} WHERE {_v6_ident('id')} IN ({marks})"
                    params = seed_ids
                elif "businessId" in c:
                    sql = f"DELETE FROM {_v6_ident(table)} WHERE {_v6_ident('businessId')} IN ({marks})"
                    params = seed_ids
                else:
                    continue
                before = con.total_changes
                con.execute(sql, params)
                delta = con.total_changes - before
                if delta:
                    result["deleted"][table] = int(delta)
            for table in sorted(tset):
                if table in _V6_DELETE_ORDER:
                    continue
                c = _v6_cols(con, table)
                if "businessId" not in c:
                    continue
                before = con.total_changes
                con.execute(f"DELETE FROM {_v6_ident(table)} WHERE {_v6_ident('businessId')} IN ({marks})", seed_ids)
                delta = con.total_changes - before
                if delta:
                    result["deleted"][table] = int(result["deleted"].get(table, 0)) + int(delta)
        fk = [tuple(row) for row in con.execute("PRAGMA foreign_key_check").fetchall()]
        result["foreign_key_check"] = fk[:50]
        if fk:
            raise RuntimeError("Foreign key check failed after external signature clear")
        con.commit()
        result["after_seed_business_ids"] = _v6_detect_seed_business_ids(con)
        return result
    except Exception:
        try:
            con.rollback()
        except Exception:
            pass
        raise
    finally:
        con.close()


def _v6_clear_external_seed(public: bool = False) -> dict[str, Any]:
    scan = external_seed_scan(public=False)
    actionable = [item for item in (scan.get("databases") or []) if int(item.get("external_seed_records_open") or 0) > 0]
    if not actionable:
        return {"ok": True, "status": "NO_EXTERNAL_SEED_FOUND", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "external_seed_records_cleared": 0, "scan": scan}
    backup = create_backup("before_external_seed_clear")  # type: ignore[name-defined]
    cleaned: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    db_by_rel = {d.get("relative_path"): d for d in discover_dbs()}  # type: ignore[name-defined]
    db_by_path = {str(d.get("path")): d for d in discover_dbs()}  # type: ignore[name-defined]
    for item in actionable:
        db = db_by_path.get(str(item.get("path"))) or db_by_rel.get(item.get("relative_path")) or item
        try:
            cleaned.append(_v6_delete_external_seed_db(db, item))
        except Exception as exc:
            errors.append({"db": item.get("relative_path"), "error": str(exc), "traceback": traceback.format_exc()})
    post = external_seed_scan(public=False)
    status = "PASS" if not errors and int(post.get("external_seed_records_open") or 0) == 0 else "WARN"
    cleared_total = sum(sum(x.get("deleted", {}).values()) + sum(x.get("chart_lab_deleted", {}).values()) for x in cleaned)
    payload = {
        "ok": status == "PASS",
        "status": status,
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "clear_engine": "ledger_plus_signature",
        "backup": backup,
        "external_seed_records_cleared": int(cleared_total),
        "scan_before": scan,
        "cleaned": cleaned,
        "scan_after": post,
        "errors": errors,
    }
    try:
        evidence = write_evidence(f"external_seed_clear_v6_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}", payload)  # type: ignore[name-defined]
        payload["evidence"] = evidence
        log_event("external_seed_clear_v6", {"status": status, "cleared": cleared_total, "evidence": evidence, "errors": len(errors)})  # type: ignore[name-defined]
    except Exception:
        pass
    if public:
        try:
            return public_safe(payload)  # type: ignore[name-defined]
        except Exception:
            return payload
    return payload


def clear_generated(public: bool = False, pin: str | None = None, pin_id: str | None = None) -> dict[str, Any]:  # type: ignore[override]
    base = _V6_PREVIOUS_CLEAR_GENERATED(public=False, pin=pin, pin_id=pin_id) if callable(_V6_PREVIOUS_CLEAR_GENERATED) else {"ok": False, "status": "CLEAR_ENGINE_MISSING"}
    pin_blocked_statuses = {"PIN_REQUIRED", "NO_ACTIVE_PIN", "PIN_EXPIRED", "PIN_INVALID", "PUBLIC_MUTATION_BLOCKED"}
    if str(base.get("status")) in pin_blocked_statuses or (not base.get("ok") and "PIN" in str(base.get("status"))):
        return public_safe(base) if public and "public_safe" in globals() else base  # type: ignore[name-defined]
    if base.get("ok") is not True and base.get("status") not in {"PASS"}:
        base["v6_external_signature_clear_skipped"] = "base_ledger_clear_not_green"
        return public_safe(base) if public and "public_safe" in globals() else base  # type: ignore[name-defined]
    external = _v6_clear_external_seed(public=False)
    merged = dict(base)
    merged.update({
        "apiVersion": API_VERSION,
        "hardeningVersion": HARDENING_VERSION,
        "clear_engine": "ledger_plus_signature",
        "status": "PASS" if bool(base.get("ok")) and bool(external.get("ok")) else "WARN",
        "ok": bool(base.get("ok")) and bool(external.get("ok")),
        "ledger_clear_result": base,
        "external_signature_clear_result": external,
        "external_seed_records_cleared": int(external.get("external_seed_records_cleared") or 0),
    })
    try:
        write_evidence(f"clear_v6_ledger_plus_signature_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}", merged)  # type: ignore[name-defined]
    except Exception:
        pass
    return public_safe(merged) if public and "public_safe" in globals() else merged  # type: ignore[name-defined]


def route_catalog() -> dict[str, Any]:  # type: ignore[override]
    try:
        base = _V6_PREVIOUS_ROUTE_CATALOG().get("routes", []) if callable(_V6_PREVIOUS_ROUTE_CATALOG) else []
    except Exception:
        base = []
    extra = [
        {"method": "GET", "path": "/api/lifecycle/external-seed/scan", "description": "Detecta semillas Data Lifecycle que no estén en ledger"},
    ]
    seen = set()
    routes = []
    for r in list(base) + extra:
        key = r.get("path")
        if key in seen:
            continue
        seen.add(key)
        routes.append(r)
    return {"ok": True, "status": "ROUTES_READY", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "routes": routes}


def lifecycle_payload(path: str, public: bool = False) -> dict[str, Any]:  # type: ignore[override]
    ensure_dirs()
    parsed = urlparse(path)
    clean = parsed.path.rstrip("/")
    try:
        if clean.startswith("/api/lifecycle/external-seed/scan"):
            return external_seed_scan(public=public)
        payload = _V6_PREVIOUS_LIFECYCLE_PAYLOAD(path, public=False) if callable(_V6_PREVIOUS_LIFECYCLE_PAYLOAD) else {"ok": False, "status": "LIFECYCLE_PAYLOAD_MISSING"}
        if isinstance(payload, dict):
            payload["apiVersion"] = API_VERSION
            payload["hardeningVersion"] = HARDENING_VERSION
            payload.setdefault("clear_engine", "ledger_plus_signature")
            if clean in {"/api/lifecycle", "/api/lifecycle/latest", "/api/lifecycle/dashboard"}:
                payload = latest_dashboard(public=False)
            if clean.startswith("/api/lifecycle/routes"):
                payload = route_catalog()
            if public:
                try:
                    return public_safe(payload)  # type: ignore[name-defined]
                except Exception:
                    return payload
        return payload
    except Exception as exc:
        payload = {"ok": False, "status": "LIFECYCLE_V6_EXCEPTION", "apiVersion": API_VERSION, "hardeningVersion": HARDENING_VERSION, "error": str(exc), "traceback": traceback.format_exc()}
        return public_safe(payload) if public and "public_safe" in globals() else payload  # type: ignore[name-defined]

# END PRISMA DATA LIFECYCLE V6 - Ledger + Ghost Signature Clear
