#!/usr/bin/env python3
"""Operator CLI for selecting PRISMA identity authority profiles."""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from identity_dictionary_core import IDENTITY, ROOT, build_compilation, canonical_bytes, load_model, validate_model


def trash_root() -> Path:
    configured = os.environ.get("PRISMA_TRASH_ROOT")
    if configured:
        return Path(configured)
    default = Path(r"F:\Trash-old")
    if os.name == "nt":
        return default
    return ROOT / ".identity-local-trash"


def write_compiled() -> None:
    from identity_dictionary_core import COMPILED
    for relative, content in build_compilation().items():
        path = COMPILED / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def command_status(model) -> int:
    problems, warnings = validate_model(check_compiled=True)
    print(json.dumps({
      "status":"PASS" if not problems else "FAIL",
      "selectedProfileId":model["activation"]["selectedProfileId"],
      "runtimeProjection":False,
      "surfaceReadiness":{s:b["readiness"] for s,b in model["bindings"].items()},
      "warnings":warnings,"problems":problems
    }, indent=2, ensure_ascii=False))
    return 0 if not problems else 1


def command_activate(model, profile_id: str) -> int:
    if profile_id not in model["profiles"]:
        print(f"Unknown profile: {profile_id}", file=sys.stderr)
        return 2
    activation_path = IDENTITY / "activation" / "active.identity.json"
    compiled_path = IDENTITY / "compiled" / "current"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = trash_root() / f"identity_activation_{stamp}"
    backup.mkdir(parents=True, exist_ok=False)
    shutil.copy2(activation_path, backup / "active.identity.json")
    if compiled_path.exists():
        shutil.copytree(compiled_path, backup / "compiled-current")
    manifest = {
      "schema":"prisma.identity.activation-backup.v1","createdAt":datetime.now().astimezone().isoformat(),
      "reason":f"activate {profile_id}","originalActivation":activation_path.as_posix(),
      "compiledRoot":compiled_path.as_posix(),"runtimeMutationCount":0
    }
    (backup / "manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    try:
        activation = dict(model["activation"])
        activation["selectedProfileId"] = profile_id
        activation["selectedAt"] = datetime.now().astimezone().isoformat()
        activation["runtimeProjection"] = False
        activation["status"] = "AUTHORITY_SELECTED_SOURCE_ONLY"
        activation["reason"] = "Profile selected through governed CLI. Runtime projection remains separately gated."
        activation_path.write_bytes(canonical_bytes(activation))
        write_compiled()
        problems, warnings = validate_model(check_compiled=True)
        if problems:
            raise RuntimeError("; ".join(problems))
        print(json.dumps({
          "status":"PASS","selectedProfileId":profile_id,"runtimeMutationCount":0,
          "backup":str(backup),"warnings":warnings,
          "nextGate":"Fresh Authority Mesh required before runtime projection."
        },indent=2,ensure_ascii=False))
        return 0
    except Exception as exc:
        shutil.copy2(backup / "active.identity.json", activation_path)
        if (backup / "compiled-current").exists():
            if compiled_path.exists():
                failed = backup / "failed-compiled-current"
                if failed.exists(): shutil.rmtree(failed)
                shutil.move(str(compiled_path), str(failed))
            shutil.copytree(backup / "compiled-current", compiled_path)
        print(json.dumps({"status":"FAIL","error":str(exc),"restoredFrom":str(backup)},indent=2),file=sys.stderr)
        return 1


def main() -> int:
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("status")
    sub.add_parser("list")
    show=sub.add_parser("show"); show.add_argument("profile_id")
    activate=sub.add_parser("activate"); activate.add_argument("profile_id")
    args=parser.parse_args()
    model=load_model()
    if args.command=="status": return command_status(model)
    if args.command=="list":
        print(json.dumps([{"id":p["id"],"name":p["name"],"status":p["status"]} for p in model["profiles"].values()],indent=2,ensure_ascii=False)); return 0
    if args.command=="show":
        if args.profile_id not in model["profiles"]: return 2
        print(json.dumps(model["profiles"][args.profile_id],indent=2,ensure_ascii=False)); return 0
    if args.command=="activate": return command_activate(model,args.profile_id)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
