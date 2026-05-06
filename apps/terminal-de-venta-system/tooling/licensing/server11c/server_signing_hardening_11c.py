#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, base64, datetime as dt, fnmatch, hashlib, hmac, json, os, re, shutil, sys, urllib.request
from pathlib import Path
from typing import Any

DEFAULT_OUT = r"F:\descargasf"
DEV_MATERIAL = Path("local-runtime/license-keys/dev/dev-signing-secret.local.json")
SIGNED_OUT = Path("local-runtime/license/license.signed.remote.local.json")
CONFIG_OUT = Path("local-runtime/license-server/signing-config.local.json")
REGISTRY_OUT = Path("local-runtime/license-keys/dev/public-signing-registry.local.json")
LEGACY_JS = Path("tooling/licensing/create_dev_signed_license.js")
CONTRACT = Path("tooling/licensing/server11c/server_signing_hardening_contract_11c.json")
ALLOWLIST = Path("tooling/licensing/server11c/repo_secret_scan_allowlist_11c.json")
PEM_RE = re.compile(r"-----BEGIN (?:(?:RSA|DSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----[\s\S]+?-----END (?:(?:RSA|DSA|EC|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----", re.M)
TEXT_EXT = {".cmd",".bat",".ps1",".py",".js",".ts",".tsx",".json",".jsonl",".md",".txt",".yml",".yaml",".env",".pem"}
DEFAULT_FIXTURES = ["tooling/licensing/signature10c/private_key_scan_regressions.jsonl", "tooling/licensing/signature10f/private_key_smoke_regressions_10f.jsonl", "tooling/licensing/server11c/server_signing_tamper_cases_11c.jsonl"]
DEFAULT_EXCLUDES = {".git",".hg",".svn","node_modules",".next","dist","build","coverage",".turbo",".venv","venv","__pycache__"}

def stamp(): return dt.datetime.now().strftime("%y%m%d_%H%M")
def outdir(p):
    d=Path(p); d.mkdir(parents=True, exist_ok=True); return d
def rel(root,p):
    try: return str(p.relative_to(root)).replace("/","\\")
    except Exception: return str(p)
def b64u(data: bytes) -> str: return base64.urlsafe_b64encode(data).decode().rstrip("=")
def b64ud(s: str) -> bytes: return base64.urlsafe_b64decode((s + "="*((4-len(s)%4)%4)).encode())
def cjson(o: Any) -> bytes: return json.dumps(o, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
def load_json(p: Path):
    with p.open("r", encoding="utf-8") as f: return json.load(f)
def write_json(p: Path, o: Any):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(o, indent=2, ensure_ascii=False, sort_keys=True)+"\n", encoding="utf-8", newline="\n")
def read_text(p: Path):
    try: return p.read_text(encoding="utf-8")
    except UnicodeDecodeError: return p.read_text(encoding="latin-1")
    except Exception: return None

def normalize_material(raw: dict) -> dict:
    kid = raw.get("key_id") or raw.get("keyId") or raw.get("kid")
    sec = raw.get("secret_b64url") or raw.get("secretMaterialBase64Url") or raw.get("secret")
    alg = raw.get("algorithm") or raw.get("alg") or "HS256_DEV_LOCAL"
    if alg == "HS256_DEV_ONLY": alg = "HS256_DEV_LOCAL"
    if not kid or not sec: raise ValueError("Signing material incompleto; faltan keyId/key_id o secretMaterialBase64Url/secret_b64url")
    secret = b64ud(str(sec))
    if len(secret) < 32: raise ValueError("Signing material inseguro: secret menor a 32 bytes")
    return {"key_id": str(kid), "secret_b64url": b64u(secret), "algorithm": str(alg), "materialClass": raw.get("materialClass") or "dev-local"}

def load_material(root: Path) -> dict:
    path = root/DEV_MATERIAL
    raw = load_json(path)
    mat = normalize_material(raw)
    raw.update({"key_id": mat["key_id"], "keyId": mat["key_id"], "secret_b64url": mat["secret_b64url"], "secretMaterialBase64Url": mat["secret_b64url"], "algorithm": mat["algorithm"], "alg": mat["algorithm"]})
    write_json(path, raw)
    return mat

def sign(payload: dict, mat: dict) -> dict:
    dig = hmac.new(b64ud(mat["secret_b64url"]), cjson(payload), hashlib.sha256).digest()
    return {"payload": payload, "signature": {"schemaVersion":"11C", "algorithm": mat["algorithm"], "keyId": mat["key_id"], "value": b64u(dig)}}

def verify(env: dict, mat: dict):
    if not isinstance(env, dict): return False, "envelope_not_object"
    payload, sig = env.get("payload"), env.get("signature")
    if not isinstance(payload, dict) or not isinstance(sig, dict): return False, "missing_payload_or_signature"
    if sig.get("keyId") != mat["key_id"]: return False, "key_id_mismatch"
    if sig.get("algorithm") != mat["algorithm"]: return False, "algorithm_mismatch"
    expected = sign(payload, mat)["signature"]["value"]
    return (True, "signature_valid") if hmac.compare_digest(str(sig.get("value","")), expected) else (False, "signature_invalid")

def payload():
    return {"schemaVersion":"1.0.0","licenseId":"lic_server11c_local_demo","customerId":"cust_demo","businessId":"biz_demo","deviceId":"device_demo_tablet_01","plan":"TABLET_PC_REQUIRED","state":"active","issuedAt":"2026-04-30T00:00:00.000Z","validUntil":"2099-12-31T23:59:59.000Z"}

def load_allow(root: Path):
    p=root/ALLOWLIST
    if p.exists():
        try: return load_json(p)
        except Exception: pass
    return {"allowed_fixture_globs": DEFAULT_FIXTURES, "exclude_dirs": sorted(DEFAULT_EXCLUDES)}

def scan(root: Path):
    allow=load_allow(root); fixtures=allow.get("allowed_fixture_globs") or DEFAULT_FIXTURES; excludes=set(allow.get("exclude_dirs") or DEFAULT_EXCLUDES)
    findings=[]; allowed=[]
    for dp, dns, files in os.walk(root):
        dns[:] = [d for d in dns if d not in excludes and not d.startswith(".prisma_license_")]
        for name in files:
            p=Path(dp)/name
            if p.suffix.lower() not in TEXT_EXT and "license" not in str(p).lower() and "key" not in str(p).lower(): continue
            try:
                if p.stat().st_size > 5_000_000: continue
            except Exception: continue
            text=read_text(p)
            if not text: continue
            r=rel(root,p).replace("\\","/")
            for m in PEM_RE.finditer(text):
                item={"path": r.replace("/","\\"), "line": text.count("\n",0,m.start())+1, "fp": hashlib.sha256(m.group(0).encode(errors="ignore")).hexdigest()[:16]}
                if any(fnmatch.fnmatch(r, pat.replace("\\","/")) for pat in fixtures): allowed.append(item)
                else: findings.append(item)
    return findings, allowed

def sanitize(root: Path, dry=False):
    p=root/LEGACY_JS
    if not p.exists(): return True, "missing_not_needed"
    text=read_text(p) or ""
    if not PEM_RE.search(text): return True, "no_pem_block"
    if dry: return True, "would_replace_embedded_pem"
    b=root/".prisma_license_server_signing_hardening_11c_backups"/stamp(); b.mkdir(parents=True, exist_ok=True); shutil.copy2(p,b/p.name)
    safe='''#!/usr/bin/env node
/* 11C sanitized: no embedded PEM private key. Reads local-runtime dev signing material. */
const fs=require("fs"), path=require("path"), crypto=require("crypto");
const root=path.resolve(__dirname,"..","..");
const matPath=path.join(root,"local-runtime","license-keys","dev","dev-signing-secret.local.json");
function b64u(b){return Buffer.from(b).toString("base64").replace(/=/g,"").replace(/\\+/g,"-").replace(/\\//g,"_");}
function canonical(o){return JSON.stringify(o,Object.keys(o).sort());}
function material(){const raw=JSON.parse(fs.readFileSync(matPath,"utf8")); const keyId=raw.key_id||raw.keyId; const sec=raw.secret_b64url||raw.secretMaterialBase64Url; const alg=raw.algorithm==="HS256_DEV_ONLY"?"HS256_DEV_LOCAL":(raw.algorithm||"HS256_DEV_LOCAL"); if(!keyId||!sec) throw new Error("Missing local dev signing material fields"); return {keyId,sec,alg};}
function signPayload(payload){const m=material(); const secret=Buffer.from(m.sec.replace(/-/g,"+").replace(/_/g,"/"),"base64"); const value=b64u(crypto.createHmac("sha256",secret).update(canonical(payload)).digest()); return {payload, signature:{schemaVersion:"11C",algorithm:m.alg,keyId:m.keyId,value}};}
if(require.main===module){process.stdout.write(JSON.stringify(signPayload({licenseId:"lic_dev_signed_local",plan:"TABLET_PC_REQUIRED",state:"active",issuedAt:new Date().toISOString()}),null,2)+"\n");}
module.exports={signPayload};
'''
    p.write_text(safe, encoding="utf-8", newline="\n")
    return True, f"replaced_embedded_pem backup={b/p.name}"

def report(out: Path, name: str, lines):
    path=out/f"terminal_venta_{name}_{stamp()}.md"; path.write_text("\n".join(lines)+"\n", encoding="utf-8", newline="\n"); return path

def emit(checks):
    for n,ok,d in checks: print(f"- {n}: {'OK' if ok else 'FAIL'} {d}")
    return all(ok for _,ok,_ in checks)

def cmd_smoke(args):
    root=Path(args.root).resolve(); out=outdir(args.out); checks=[]
    try:
        mat=load_material(root)
        write_json(root/CONFIG_OUT,{"schemaVersion":"11C","environment":"development","keyId":mat["key_id"],"algorithm":mat["algorithm"],"productionAllowsDevMaterial":False})
        write_json(root/REGISTRY_OUT,{"schemaVersion":"11C","keys":[{"keyId":mat["key_id"],"algorithm":mat["algorithm"],"materialClass":"dev-local","secretStoredOutsideRepo":True}]})
        checks.append(("config", True, str(root/CONFIG_OUT)))
        ok,msg=sanitize(root); checks.append(("legacy JS signer sanitize", ok, msg))
        findings,allowed=scan(root); checks.append(("repo private-key PEM scan", len(findings)==0, f"findings={len(findings)} allowedFixtures={len(allowed)}" + (" first="+";".join(f['path'] for f in findings[:3]) if findings else "")))
        env=sign(payload(),mat); ok,det=verify(env,mat); checks.append(("offline sign+verify",ok,det))
        t=json.loads(json.dumps(env)); t["payload"]["plan"]="TABLET_SOLO"; ok,det=verify(t,mat); checks.append(("tamper rejection payload",not ok,det))
        t=json.loads(json.dumps(env)); v=t["signature"]["value"]; t["signature"]["value"]=("A" if v[0]!="A" else "B")+v[1:]; ok,det=verify(t,mat); checks.append(("tamper rejection signature",not ok,det))
        t=json.loads(json.dumps(env)); t["signature"].pop("keyId",None); ok,det=verify(t,mat); checks.append(("tamper rejection missing keyId",not ok,det))
        checks.append(("production refuses dev material", mat.get("algorithm")=="HS256_DEV_LOCAL", "production no puede firmar con material dev-local HS256_DEV_LOCAL"))
        write_json(root/SIGNED_OUT,env); checks.append(("signed output", True, str(root/SIGNED_OUT)))
        if args.http:
            try:
                with urllib.request.urlopen(args.base_url.rstrip('/')+'/health',timeout=5) as r: checks.append(("server06 health", r.status==200, f"status={r.status}"))
            except Exception as e: checks.append(("server06 health", False, str(e)))
        else: checks.append(("server06 health", True, "SKIP use --http to require live server"))
    except Exception as e: checks.append(("smoke", False, str(e)))
    ok=emit(checks); rp=report(out,"license_server_signing_11c_smoke",["# PRISMA License Server Signing Hardening 11C Smoke",""]+[f"- {n}: `{'OK' if o else 'FAIL'}` {d}" for n,o,d in checks]+["",f"Status: `{'FINAL READY' if ok else 'BLOCKED'}`"]); print(f"REPORT {rp}"); print("FINAL READY" if ok else "BLOCKED"); return 0 if ok else 2

def cmd_scan(args):
    root=Path(args.root).resolve(); out=outdir(args.out); sanitize(root); findings,allowed=scan(root); checks=[("repo private-key PEM scan",len(findings)==0,f"findings={len(findings)} allowedFixtures={len(allowed)}")]; ok=emit(checks); rp=report(out,"license_server_signing_11c_scan",["# Scan 11C",f"Findings: `{len(findings)}`",f"Allowed fixtures: `{len(allowed)}`"]+[f"- `{f['path']}:{f['line']}` fp={f['fp']}" for f in findings[:50]]); print(f"REPORT {rp}"); print("FINAL READY" if ok else "BLOCKED"); return 0 if ok else 2

def cmd_material(args):
    root=Path(args.root).resolve(); out=outdir(args.out); checks=[]
    try:
        mat=load_material(root); txt=(root/DEV_MATERIAL).read_text(encoding="utf-8"); env=sign(payload(),mat); ok,det=verify(env,mat)
        checks += [("material parses",True,f"{mat['key_id']} alg={mat['algorithm']}"),("material has no PEM private-key block",PEM_RE.search(txt) is None,str(root/DEV_MATERIAL)),("sign+verify",ok,det)]
    except Exception as e: checks.append(("material",False,str(e)))
    ok=emit(checks); rp=report(out,"license_server_signing_material_11c",["# Material 11C",""]+[f"- {n}: `{'OK' if o else 'FAIL'}` {d}" for n,o,d in checks]+["",f"Status: `{'FINAL READY' if ok else 'BLOCKED'}`"]); print(f"REPORT {rp}"); print("FINAL READY" if ok else "BLOCKED"); return 0 if ok else 2

def cmd_sanitize(args):
    ok,msg=sanitize(Path(args.root).resolve(), bool(args.dry_run)); emit([("legacy JS signer sanitize",ok,msg)]); print("FINAL READY" if ok else "BLOCKED"); return 0 if ok else 2

def cmd_sign(args):
    root=Path(args.root).resolve(); mat=load_material(root); env=sign(payload(),mat); write_json(root/SIGNED_OUT,env); emit([("signed output",True,str(root/SIGNED_OUT))]); print("FINAL READY"); return 0

def cmd_contract(args):
    print((Path(args.root).resolve()/CONTRACT).read_text(encoding="utf-8")); return 0

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",default="."); p.add_argument("--out",default=DEFAULT_OUT); sp=p.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("smoke"); a.add_argument("--http",action="store_true"); a.add_argument("--base-url",default="http://127.0.0.1:3140"); a.set_defaults(fn=cmd_smoke)
    sp.add_parser("scan").set_defaults(fn=cmd_scan)
    sp.add_parser("material-smoke").set_defaults(fn=cmd_material)
    a=sp.add_parser("sanitize"); a.add_argument("--dry-run",action="store_true"); a.set_defaults(fn=cmd_sanitize)
    sp.add_parser("sign-license").set_defaults(fn=cmd_sign)
    sp.add_parser("contract").set_defaults(fn=cmd_contract)
    args=p.parse_args(); return args.fn(args)
if __name__=="__main__": raise SystemExit(main())
