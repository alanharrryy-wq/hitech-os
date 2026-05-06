#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

TECHNICAL_VISIBLE_BANNED = ["checkout", "cart", "sync queue", "outbox", "payload", "endpoint", "runtime", "api"]
REQUIRED_KEYS = ["schemaVersion", "verticalId", "displayName", "capabilities", "surfaces", "offline"]


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"ERROR no se pudo leer JSON {path}: {exc}")


def validate_manifest(path: Path, known_caps: set[str]) -> list[str]:
    errors = []
    data = load_json(path)
    for key in REQUIRED_KEYS:
        if key not in data:
            errors.append(f"{path.name}: falta {key}")
    caps = data.get("capabilities", {})
    for bucket in ["required", "optional"]:
        for cap in caps.get(bucket, []):
            if cap not in known_caps and not any(cap.startswith(prefix) for prefix in ["sales.", "customer.", "delivery.", "hardware.", "restaurant.", "pharmacy.", "beauty.", "apparel.", "repair.", "field_route."]):
                errors.append(f"{path.name}: capacidad no registrada {cap}")
    for surface in ["tablet", "pc"]:
        routes = data.get("surfaces", {}).get(surface, {}).get("routes", [])
        for route in routes:
            low = route.lower()
            for banned in TECHNICAL_VISIBLE_BANNED:
                if banned in low:
                    errors.append(f"{path.name}: ruta visible tecnica '{route}'")
    offline = data.get("offline", {})
    for k in ["salesAllowed", "sensitiveActionsRequireConnection"]:
        if not isinstance(offline.get(k), bool):
            errors.append(f"{path.name}: offline.{k} debe ser booleano")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Valida contratos base de PRISMA verticals 00A")
    parser.add_argument("--root", default=".", help="Raiz del paquete instalado")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    cap_file = root / "shared/contracts/verticals/capabilities.contract.json"
    if not cap_file.exists():
        raise SystemExit(f"ERROR falta {cap_file}")
    cap_data = load_json(cap_file)
    known_caps = {c["id"] for c in cap_data.get("coreCapabilities", []) + cap_data.get("verticalCapabilities", [])}
    manifest_dir = root / "shared/verticals"
    errors = []
    for path in sorted(manifest_dir.glob("*.manifest.json")):
        errors.extend(validate_manifest(path, known_caps))
    if errors:
        print("BLOCKED PRISMA_VERTICALS_00A")
        for err in errors:
            print("-", err)
        return 1
    print("READY PRISMA_VERTICALS_00A: contratos y manifiestos validos")
    return 0

if __name__ == "__main__":
    sys.exit(main())
