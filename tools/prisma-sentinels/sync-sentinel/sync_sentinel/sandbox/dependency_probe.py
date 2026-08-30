from __future__ import annotations

import json
import subprocess
from pathlib import Path

APP_REL = Path("apps/terminal-de-venta-system")
TARGETS = {
    "pc": APP_REL / "products/pc/app",
    "tablet": APP_REL / "products/tablet/app",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _node_resolution(app_root: Path, package_name: str) -> dict[str, object]:
    script = r'''
const fs=require('node:fs');
const path=require('node:path');
const app=process.argv[1];
const pkg=process.argv[2];
try {
  const entry=require.resolve(pkg,{paths:[app]});
  let cur=path.dirname(entry), manifest=null;
  for (let i=0;i<12;i++) {
    const candidate=path.join(cur,'package.json');
    if (fs.existsSync(candidate)) {
      const data=JSON.parse(fs.readFileSync(candidate,'utf8'));
      if (data.name===pkg) { manifest={path:candidate,version:data.version}; break; }
    }
    const next=path.dirname(cur); if (next===cur) break; cur=next;
  }
  console.log(JSON.stringify({ok:true,entry,manifest}));
} catch (error) {
  console.log(JSON.stringify({ok:false,error:error instanceof Error?error.message:String(error)}));
  process.exitCode=2;
}
'''
    cp = subprocess.run(
        ["node", "-e", script, str(app_root), package_name],
        cwd=str(app_root), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=30, check=False,
    )
    raw = (cp.stdout or "").strip().splitlines()
    if not raw:
        return {"ok": False, "returncode": cp.returncode, "error": (cp.stderr or "")[-1000:]}
    try:
        data = json.loads(raw[-1])
    except json.JSONDecodeError:
        return {"ok": False, "returncode": cp.returncode, "error": raw[-1][-1000:]}
    data["returncode"] = cp.returncode
    if data.get("manifest") and isinstance(data["manifest"], dict):
        manifest_path = Path(str(data["manifest"].get("path", "")))
        try:
            data["manifest"]["path"] = manifest_path.relative_to(app_root).as_posix()
        except ValueError:
            data["manifest"]["path"] = manifest_path.name
    if data.get("entry"):
        try:
            data["entry"] = Path(str(data["entry"])).relative_to(app_root).as_posix()
        except ValueError:
            data["entry"] = Path(str(data["entry"])).name
    return data


def probe_dependencies(repo: Path) -> dict[str, object]:
    rows: dict[str, object] = {}
    all_ok = True
    for label, rel in TARGETS.items():
        app = repo / rel
        package_json = _load_json(app / "package.json")
        declared = {
            "@prisma/client": (package_json.get("dependencies") or {}).get("@prisma/client") or (package_json.get("devDependencies") or {}).get("@prisma/client"),
            "prisma": (package_json.get("dependencies") or {}).get("prisma") or (package_json.get("devDependencies") or {}).get("prisma"),
        }
        resolved = {name: _node_resolution(app, name) for name in ("@prisma/client", "prisma")}
        exact = True
        for name, expected in declared.items():
            actual = ((resolved.get(name) or {}).get("manifest") or {}).get("version") if isinstance(resolved.get(name), dict) else None
            if not expected or not actual or str(expected).lstrip("^~") != str(actual):
                exact = False
        row_ok = exact and all(bool((resolved[name] or {}).get("ok")) for name in resolved)
        all_ok = all_ok and row_ok
        rows[label] = {"declared": declared, "resolved": resolved, "versionsMatch": exact, "ok": row_ok}
    return {"schemaVersion": "prisma.sync-sentinel.dependency-resolution.v1", "targets": rows, "ok": all_ok}
