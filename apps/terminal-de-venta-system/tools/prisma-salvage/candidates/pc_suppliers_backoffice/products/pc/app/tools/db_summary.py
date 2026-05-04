import sqlite3, sys, json
from pathlib import Path

path = Path(sys.argv[1])
conn = sqlite3.connect(path)
cur = conn.cursor()
summary = {}
for table in ["Product", "Barcode", "StockSnapshot", "StockMovement", "PurchaseOrder", "GoodsReceipt", "AuditCount", "ReplenishmentSignal", "OutboxEvent"]:
    try:
        summary[table] = cur.execute(f"select count(*) from {table}").fetchone()[0]
    except sqlite3.Error:
        summary[table] = None
print(json.dumps(summary, ensure_ascii=False, indent=2))
