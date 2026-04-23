#!/usr/bin/env python3
import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path


def read_zip_text(zip_path: Path, entry: str) -> str:
    with zipfile.ZipFile(zip_path, "r") as zf:
        with zf.open(entry, "r") as fh:
            return fh.read().decode("utf-8")


def read_zip_json(zip_path: Path, entry: str):
    return json.loads(read_zip_text(zip_path, entry))


def check_procurement(zip_path: Path):
    entry_json = "prisma-procurement/seeds/procurement.seed.json"
    entry_sql = "prisma-procurement/sql/seed-procurement.sql"
    data = read_zip_json(zip_path, entry_json)
    sql = read_zip_text(zip_path, entry_sql)

    po_line_subtotal = sum(int(x["lineSubtotalCents"]) for x in data["purchaseOrderLines"])
    po_line_tax = sum(int(x["lineTaxCents"]) for x in data["purchaseOrderLines"])
    po_line_total = sum(int(x["lineTotalCents"]) for x in data["purchaseOrderLines"])
    gr_line_subtotal = sum(int(x["lineSubtotalCents"]) for x in data["goodsReceiptLines"])
    gr_line_tax = sum(int(x["lineTaxCents"]) for x in data["goodsReceiptLines"])
    gr_line_total = sum(int(x["lineTotalCents"]) for x in data["goodsReceiptLines"])

    po_header = data["purchaseOrders"][0]
    gr_header = data["goodsReceipts"][0]

    po_ok = (
        int(po_header["subtotalCents"]) == po_line_subtotal
        and int(po_header["taxCents"]) == po_line_tax
        and int(po_header["totalCents"]) == po_line_total
    )
    gr_ok = (
        int(gr_header["subtotalCents"]) == gr_line_subtotal
        and int(gr_header["taxCents"]) == gr_line_tax
        and int(gr_header["totalCents"]) == gr_line_total
    )

    po_sql_match = re.search(
        r"\('po_demo_001'.*?,(\d+),(\d+),(\d+),NOW\(\),NOW\(\)\);",
        sql,
        flags=re.DOTALL,
    )
    gr_sql_match = re.search(
        r"\('gr_demo_001'.*?,(\d+),(\d+),(\d+),NOW\(\),NOW\(\)\);",
        sql,
        flags=re.DOTALL,
    )

    sql_ok = False
    if po_sql_match and gr_sql_match:
        po_sql = tuple(int(x) for x in po_sql_match.groups())
        gr_sql = tuple(int(x) for x in gr_sql_match.groups())
        sql_ok = po_sql == (po_line_subtotal, po_line_tax, po_line_total) and gr_sql == (
            gr_line_subtotal,
            gr_line_tax,
            gr_line_total,
        )
    else:
        po_sql = None
        gr_sql = None

    return {
        "purchase_order": {
            "header": {
                "subtotalCents": int(po_header["subtotalCents"]),
                "taxCents": int(po_header["taxCents"]),
                "totalCents": int(po_header["totalCents"]),
            },
            "line_sums": {
                "subtotalCents": po_line_subtotal,
                "taxCents": po_line_tax,
                "totalCents": po_line_total,
            },
            "match": po_ok,
        },
        "goods_receipt": {
            "header": {
                "subtotalCents": int(gr_header["subtotalCents"]),
                "taxCents": int(gr_header["taxCents"]),
                "totalCents": int(gr_header["totalCents"]),
            },
            "line_sums": {
                "subtotalCents": gr_line_subtotal,
                "taxCents": gr_line_tax,
                "totalCents": gr_line_total,
            },
            "match": gr_ok,
        },
        "sql_headers_match_line_sums": sql_ok,
        "sql_headers": {
            "purchase_order": po_sql,
            "goods_receipt": gr_sql,
        },
        "pass": po_ok and gr_ok and sql_ok,
    }


def check_catalog_defaults(zip_path: Path):
    entry_json = "prisma-catalog-pricing/seeds/catalog-pricing.seed.json"
    entry_constraints = "prisma-catalog-pricing/sql/constraints-defaults.sql"
    data = read_zip_json(zip_path, entry_json)
    constraints_sql = read_zip_text(zip_path, entry_constraints)

    tax_defaults = Counter()
    for row in data["taxRates"]:
        if bool(row.get("isDefault")):
            tax_defaults[row["businessId"]] += 1

    price_defaults = Counter()
    for row in data["priceLists"]:
        if bool(row.get("isDefault")):
            price_defaults[row["businessId"]] += 1

    tax_seed_ok = all(v <= 1 for v in tax_defaults.values())
    price_seed_ok = all(v <= 1 for v in price_defaults.values())

    tax_index_ok = "uq_taxrate_single_default_per_business" in constraints_sql
    price_index_ok = "uq_pricelist_single_default_per_business" in constraints_sql

    return {
        "tax_rate_default_counts": dict(tax_defaults),
        "price_list_default_counts": dict(price_defaults),
        "seed_default_uniqueness_ok": tax_seed_ok and price_seed_ok,
        "constraints_sql_present": tax_index_ok and price_index_ok,
        "pass": tax_seed_ok and price_seed_ok and tax_index_ok and price_index_ok,
    }


def check_cash_open_session(zip_path: Path):
    entry_json = "prisma-cash-management/seeds/cash-management.seed.json"
    entry_constraints = "prisma-cash-management/sql/constraints-open-session.sql"
    data = read_zip_json(zip_path, entry_json)
    constraints_sql = read_zip_text(zip_path, entry_constraints)

    open_counts = Counter()
    for row in data["cashSessions"]:
        if row.get("status") == "OPEN":
            open_counts[row["terminalId"]] += 1

    seed_ok = all(v <= 1 for v in open_counts.values())
    index_ok = "uq_cashsession_single_open_per_terminal" in constraints_sql

    return {
        "open_session_counts_by_terminal": dict(open_counts),
        "seed_open_session_uniqueness_ok": seed_ok,
        "constraint_sql_present": index_ok,
        "pass": seed_ok and index_ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Prisma consistency guardrails for Terminal de Venta.")
    parser.add_argument(
        "--prisma-root",
        default=str(Path(__file__).resolve().parent),
        help="Path to apps/Terminal de Venta/PRISMA",
    )
    parser.add_argument("--out", default="", help="Optional output JSON report path")
    args = parser.parse_args()

    prisma_root = Path(args.prisma_root)
    procurement_zip = prisma_root / "prisma-procurement.zip"
    catalog_zip = prisma_root / "prisma-catalog-pricing.zip"
    cash_zip = prisma_root / "prisma-cash-management.zip"

    report = {
        "procurement": check_procurement(procurement_zip),
        "catalog_defaults": check_catalog_defaults(catalog_zip),
        "cash_open_session": check_cash_open_session(cash_zip),
    }
    report["pass"] = all(section.get("pass") for section in report.values())

    payload = json.dumps(report, indent=2, ensure_ascii=False)
    print(payload)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload + "\n", encoding="utf-8")

    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
