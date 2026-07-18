from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def newest(root: Path, prefix: str) -> Path:
    hits = sorted(
        [p for p in root.glob(f"{prefix}*result.zip") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not hits:
        raise RuntimeError(f"Missing required authority result ZIP: {prefix}*result.zip")
    return hits[0]


def read_run(zip_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path) as archive:
        candidates = [
            name for name in archive.namelist()
            if name.replace("\\", "/").endswith("RUN_MANIFEST.json")
        ]
        if not candidates:
            raise RuntimeError(f"RUN_MANIFEST.json missing in {zip_path}")
        candidates.sort(key=lambda name: (name.count("/"), len(name)))
        return json.loads(archive.read(candidates[0]).decode("utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", default=r"F:\descargasf")
    parser.add_argument("--ndc-root", default=r"F:\PRISMA_CTX\NDC")
    parser.add_argument("--motors-root", default=r"F:\PRISMA_CTX\MOTORES")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    output_root = Path(args.output_root)
    ndc_root = Path(args.ndc_root)
    motors_root = Path(args.motors_root)
    out = Path(args.out)

    requirements = [
        ("legmesh1", "PASS_AUTHORITY_READY_FOR_PACKAGE_DESIGN"),
        ("ndclgl1", "PASS_NDC_LEGAL_EXTENSION_INSTALLED"),
        ("motlgl1", "PASS_MOTOR_LEGAL_ADAPTER_INSTALLED"),
    ]
    chain: dict[str, Any] = {}
    for prefix, expected in requirements:
        path = newest(output_root, prefix)
        run = read_run(path)
        actual = str(run.get("status", ""))
        if actual != expected:
            raise RuntimeError(f"{prefix} status mismatch: expected={expected} actual={actual} zip={path}")
        chain[prefix] = {
            "path": str(path),
            "sha256": sha256(path),
            "status": actual,
            "run": run,
        }

    required_files = [
        ndc_root / "matrix_substrate" / "schemas" / "legal-run-manifest.schema.json",
        ndc_root / "matrix_substrate" / "schemas" / "legal-input-package.schema.json",
        ndc_root / "matrix_substrate" / "schemas" / "legal-evidence.schema.json",
        motors_root / "MOTOR_LEGAL1_INSTALL_STATE.json",
        motors_root / "MOTOR_LEGAL_PROFILE_REGISTRY.json",
    ]
    missing = [str(path) for path in required_files if not path.is_file()]
    if missing:
        raise RuntimeError("Missing legal-readiness dependencies: " + "; ".join(missing))

    payload = {
        "schema": "PRISMA_MAM_LEGAL_AUTHORITY_CHAIN_V1",
        "status": "PASS",
        "authority_run_id": chain["legmesh1"]["run"].get("generated_at"),
        "started_at": chain["legmesh1"]["run"].get("generated_at"),
        "chain": chain,
        "ndc_root": str(ndc_root),
        "motors_root": str(motors_root),
        "no_touch": {
            "db_write": False,
            "git_write": False,
            "process_kill": False,
            "port_free": False,
            "server_start": False,
            "dependency_install": False,
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "out": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
