
from __future__ import annotations
import argparse
import datetime as _dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

PACKAGE = "PRISMA_VISUAL_OS_TREE_REORG_COMPAT_SHIMS_00ZB_20260504_v01"
VERSION = "20260504_v01"
SYSTEM_REL = Path("apps") / "terminal-de-venta-system"
VISUAL_REL = SYSTEM_REL / "tools" / "prisma-visual-os"
STATE_REL = SYSTEM_REL / ".prisma_install_state" / "visual-os-tree-reorg-00zb"
DEFAULT_OUT = Path(r"F:\descargasf")

MOVES = [
    {
        "name": "live-preview-server-00q.mjs",
        "category": "realtime",
        "target_dir": "realtime",
        "shim": "import './realtime/live-preview-server-00q.mjs';\n",
    },
    {
        "name": "score_prisma_studio_pro_00s.mjs",
        "category": "scoring",
        "target_dir": "scoring",
        "shim": "import './scoring/score_prisma_studio_pro_00s.mjs';\n",
    },
]

REQUIRED_DIRS = ["doctors", "launchers", "verifiers", "realtime", "scoring", "generators", "gates", "qa", "docs", "tree", "_plans"]


def now_stamp() -> str:
    return _dt.datetime.now().strftime("%y%m%d_%H%M%S")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_roots(target_root: str | None, out_dir: str | None) -> tuple[Path, Path, Path, Path]:
    root = Path(target_root or r"F:\repos\hitech-os").resolve()
    visual = root / VISUAL_REL
    state_dir = root / STATE_REL
    out = Path(out_dir or DEFAULT_OUT).resolve()
    return root, visual, state_dir, out


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def log_line(log: Path, text: str) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(text + "\n")


def analyze(visual: Path) -> list[dict]:
    items = []
    for spec in MOVES:
        source = visual / spec["name"]
        target = visual / spec["target_dir"] / spec["name"]
        shim_text = spec["shim"]
        source_text = source.read_text(encoding="utf-8", errors="ignore") if source.exists() and source.is_file() else ""
        target_exists = target.exists()
        source_exists = source.exists()
        source_is_shim = source_exists and shim_text.strip() in source_text
        if target_exists and source_is_shim:
            action = "already_applied"
            reason = "target exists and root shim points to it"
        elif source_exists and not target_exists:
            action = "move_with_shim"
            reason = "low-risk root file can move with compatibility shim"
        elif source_exists and target_exists and not source_is_shim:
            action = "blocked"
            reason = "source and target both exist; manual review required"
        elif not source_exists and target_exists:
            action = "repair_shim"
            reason = "target exists but root shim is missing"
        else:
            action = "missing"
            reason = "source and target missing"
        items.append({
            "name": spec["name"],
            "category": spec["category"],
            "source": str(source),
            "target": str(target),
            "sourceExists": source_exists,
            "targetExists": target_exists,
            "sourceIsShim": source_is_shim,
            "sourceSha256": sha256(source) if source_exists and source.is_file() else None,
            "targetSha256": sha256(target) if target_exists and target.is_file() else None,
            "action": action,
            "reason": reason,
        })
    return items


def latest_state(state_dir: Path) -> Path | None:
    if not state_dir.exists():
        return None
    states = sorted(state_dir.glob("prisma_visual_os_tree_reorg_00zb_state_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return states[0] if states else None


def make_index(visual: Path) -> None:
    tree_dir = visual / "tree"
    tree_dir.mkdir(parents=True, exist_ok=True)
    p = tree_dir / "PRISMA_VISUAL_OS_TREE_00ZB_INDEX.md"
    p.write_text("""# PRISMA Visual OS tree 00ZB\n\nEstado: compat shims para primeros movimientos low-risk.\n\n## Movidos por 00ZB\n\n- `live-preview-server-00q.mjs` -> `realtime/live-preview-server-00q.mjs` con shim en raíz.\n- `score_prisma_studio_pro_00s.mjs` -> `scoring/score_prisma_studio_pro_00s.mjs` con shim en raíz.\n\n## Regla\n\nLos launchers canónicos de raíz se conservan hasta que docs y verificadores dependientes sean actualizados formalmente.\n""", encoding="utf-8")


def do_apply(args: argparse.Namespace) -> int:
    root, visual, state_dir, out = resolve_roots(args.target_root, args.out_dir)
    stamp = now_stamp()
    log = out / f"prisma_visual_os_tree_reorg_00zb_int_{stamp}.log"
    plan_path = out / f"prisma_visual_os_tree_reorg_00zb_plan_{stamp}.json"
    state_path = state_dir / f"prisma_visual_os_tree_reorg_00zb_state_{stamp}.json"
    backup_root = visual / ".prisma_tree_backups" / PACKAGE / stamp
    log_line(log, f"START {PACKAGE} apply target={root}")
    if not visual.exists():
        log_line(log, f"FAIL visual root missing: {visual}")
        return 2
    for d in REQUIRED_DIRS:
        (visual / d).mkdir(parents=True, exist_ok=True)
    plan = analyze(visual)
    write_json(plan_path, {"package": PACKAGE, "mode": "apply-plan", "visualRoot": str(visual), "files": plan})
    operations = []
    try:
        for item, spec in zip(plan, MOVES):
            src = Path(item["source"])
            dst = Path(item["target"])
            shim_text = spec["shim"]
            op = {"name": item["name"], "source": str(src), "target": str(dst), "action": item["action"], "backups": {}}
            if item["action"] == "move_with_shim":
                backup_src = backup_root / "source" / item["name"]
                backup_src.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, backup_src)
                op["backups"]["source"] = str(backup_src)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                src.write_text(shim_text, encoding="utf-8")
                op["applied"] = True
                log_line(log, f"MOVED {src} -> {dst}; shim created")
            elif item["action"] == "repair_shim":
                src.write_text(shim_text, encoding="utf-8")
                op["applied"] = True
                log_line(log, f"SHIM repaired {src}")
            elif item["action"] == "already_applied":
                op["applied"] = False
                log_line(log, f"SKIP already applied {src}")
            else:
                op["applied"] = False
                log_line(log, f"SKIP {item['action']} {src}: {item['reason']}")
            operations.append(op)
        make_index(visual)
        state = {
            "package": PACKAGE,
            "version": VERSION,
            "mode": "apply",
            "visualRoot": str(visual),
            "backupRoot": str(backup_root),
            "planPath": str(plan_path),
            "logPath": str(log),
            "operations": operations,
            "status": "applied",
            "createdAt": _dt.datetime.now().isoformat(timespec="seconds"),
        }
        write_json(state_path, state)
        write_json(out / f"prisma_visual_os_tree_reorg_00zb_int_{stamp}.json", {"status": "applied", "statePath": str(state_path), "planPath": str(plan_path), "log": str(log)})
        log_line(log, f"STATE {state_path}")
        return 0
    except Exception as exc:
        log_line(log, f"ERROR {exc}")
        return 3


def do_dry_run(args: argparse.Namespace) -> int:
    root, visual, state_dir, out = resolve_roots(args.target_root, args.out_dir)
    stamp = now_stamp()
    out.mkdir(parents=True, exist_ok=True)
    plan_path = out / f"prisma_visual_os_tree_reorg_00zb_plan_{stamp}.json"
    log = out / f"prisma_visual_os_tree_reorg_00zb_int_{stamp}.log"
    if not visual.exists():
        log_line(log, f"FAIL visual root missing: {visual}")
        return 2
    plan = analyze(visual)
    summary = {"total": len(plan), "byAction": {}}
    for item in plan:
        summary["byAction"][item["action"]] = summary["byAction"].get(item["action"], 0) + 1
    data = {"package": PACKAGE, "mode": "dry-run", "visualRoot": str(visual), "summary": summary, "files": plan, "notes": ["dry-run does not move files", "00ZB only handles low-risk realtime/scoring files"]}
    write_json(plan_path, data)
    write_json(out / f"prisma_visual_os_tree_reorg_00zb_int_{stamp}.json", {"status": "ready", "planPath": str(plan_path), "summary": summary, "log": str(log)})
    log_line(log, f"DRY-RUN plan={plan_path}")
    print(json.dumps({"status": "ready", "planPath": str(plan_path), "summary": summary}, indent=2, ensure_ascii=False))
    return 0


def do_verify(args: argparse.Namespace) -> int:
    root, visual, state_dir, out = resolve_roots(args.target_root, args.out_dir)
    stamp = now_stamp()
    log = out / f"prisma_visual_os_tree_reorg_00zb_int_{stamp}.log"
    checks = []
    for spec in MOVES:
        src = visual / spec["name"]
        dst = visual / spec["target_dir"] / spec["name"]
        shim_ok = src.exists() and spec["shim"].strip() in src.read_text(encoding="utf-8", errors="ignore")
        checks.append({"name": f"target {spec['name']}", "ok": dst.exists(), "path": str(dst)})
        checks.append({"name": f"shim {spec['name']}", "ok": shim_ok, "path": str(src)})
    checks.append({"name": "index", "ok": (visual / "tree" / "PRISMA_VISUAL_OS_TREE_00ZB_INDEX.md").exists(), "path": str(visual / "tree" / "PRISMA_VISUAL_OS_TREE_00ZB_INDEX.md")})
    ok = all(c["ok"] for c in checks)
    result = {"package": PACKAGE, "mode": "verify", "status": "verified" if ok else "blocked", "checks": checks, "log": str(log)}
    write_json(out / f"prisma_visual_os_tree_reorg_00zb_int_{stamp}.json", result)
    log_line(log, f"VERIFY {'OK' if ok else 'BLOCKED'}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if ok else 4


def do_rollback(args: argparse.Namespace) -> int:
    root, visual, state_dir, out = resolve_roots(args.target_root, args.out_dir)
    stamp = now_stamp()
    log = out / f"prisma_visual_os_tree_reorg_00zb_int_{stamp}.log"
    state_path = latest_state(state_dir)
    if not state_path:
        log_line(log, "ROLLBACK no state found")
        return 5
    state = json.loads(state_path.read_text(encoding="utf-8"))
    for op in reversed(state.get("operations", [])):
        src = Path(op["source"])
        dst = Path(op["target"])
        backup_src = op.get("backups", {}).get("source")
        if backup_src and Path(backup_src).exists():
            if src.exists():
                src.unlink()
            shutil.copy2(backup_src, src)
            if dst.exists():
                dst.unlink()
            log_line(log, f"RESTORED {src}")
    write_json(out / f"prisma_visual_os_tree_reorg_00zb_int_{stamp}.json", {"package": PACKAGE, "mode": "rollback", "status": "rolled_back", "state": str(state_path), "log": str(log)})
    print(json.dumps({"status": "rolled_back", "state": str(state_path)}, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA Visual OS tree reorg 00ZB compatibility shims")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--rollback", action="store_true")
    parser.add_argument("--target-root", default=r"F:\repos\hitech-os")
    parser.add_argument("--out-dir", default=r"F:\descargasf")
    args = parser.parse_args()
    if args.dry_run:
        return do_dry_run(args)
    if args.apply:
        return do_apply(args)
    if args.verify:
        return do_verify(args)
    if args.rollback:
        return do_rollback(args)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
