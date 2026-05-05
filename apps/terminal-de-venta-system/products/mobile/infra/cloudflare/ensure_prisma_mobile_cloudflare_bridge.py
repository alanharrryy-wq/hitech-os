#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess
from datetime import datetime
from pathlib import Path
DEFAULT_REPO_ROOT = r"F:\repos\hitech-os\apps\terminal-de-venta-system"
DEFAULT_HOSTNAME = "prisma.hitechrts.com"
DEFAULT_ORIGIN_URL = "http://127.0.0.1:3140"
DEFAULT_TUNNEL_NAME = "engine"
DEFAULT_CONFIG_PATH = r"C:\Users\alanh\.cloudflared\config.yml"
DEFAULT_LOG_DIR = r"F:\descargasf"
PACKAGE_ID = "PRISMA_APP_MOBILE_10_CLOUDFLARE_PWA_DOMAIN_BRIDGE"
class BridgeError(RuntimeError): pass
def now_token(): return datetime.now().strftime("%y%m%d_%H%M")
def write_log(lines, log_path):
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    Path(log_path).write_text("\n".join(lines)+"\n", encoding="utf-8")
def run(cmd, lines, timeout=180):
    lines.append("run: " + " ".join(str(x) for x in cmd))
    try:
        p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
    except FileNotFoundError as err:
        raise BridgeError(f"Command not found: {cmd[0]}") from err
    output = (p.stdout or "").strip()
    if output:
        for line in output.splitlines(): lines.append("  " + line)
    lines.append(f"exit={p.returncode}")
    return p.returncode, output
def normalize_hostname(value):
    host = value.strip().lower().replace("https://", "").replace("http://", "").strip("/")
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*\.[a-z]{2,}", host): raise BridgeError(f"Invalid hostname: {value}")
    return host
def validate_origin_url(value):
    value=value.strip().rstrip("/")
    if not re.match(r"^https?://[^\s/]+(?::\d+)?$", value): raise BridgeError(f"Invalid origin URL: {value}")
    return value
def read_text(path): return Path(path).read_text(encoding="utf-8") if Path(path).exists() else ""
def build_route_block(hostname, origin_url): return f"  - hostname: {hostname}\n    service: {origin_url}\n"
def has_route(text, hostname, origin_url):
    return bool(re.search(rf"(?ms)-\s*hostname:\s*{re.escape(hostname)}\s*[\r\n]+\s*service:\s*{re.escape(origin_url)}\s*", text))
def config_has_fallback(text): return bool(re.search(r"(?mi)^\s*-\s*service:\s*http_status:404\s*$", text))
def insert_or_update_route(text, hostname, origin_url):
    block = build_route_block(hostname, origin_url)
    same_host = re.compile(rf"(?ms)^\s*-\s*hostname:\s*{re.escape(hostname)}\s*[\r\n]+\s*service:\s*[^\r\n]+\s*", re.MULTILINE)
    if same_host.search(text): return same_host.sub(block, text)
    fallback = re.search(r"(?mi)^\s*-\s*service:\s*http_status:404\s*$", text)
    if not fallback:
        if not text.endswith("\n"): text += "\n"
        return text + block + "  - service: http_status:404\n"
    return text[:fallback.start()] + block + text[fallback.start():]
def ensure_dns_route(tunnel_name, hostname, lines):
    code, output = run(["cloudflared", "tunnel", "route", "dns", tunnel_name, hostname], lines, timeout=240)
    lower = output.lower()
    ok = code == 0 or "already configured" in lower or "already exists" in lower
    if not ok: raise BridgeError(f"Could not bind DNS route for {hostname}. cloudflared exit={code}")
def restart_cloudflared(lines):
    code, _ = run(["powershell", "-NoProfile", "-Command", "Restart-Service -Name 'cloudflared' -Force -ErrorAction Stop"], lines, timeout=180)
    if code != 0: lines.append("WARN: cloudflared restart failed. Run elevated PowerShell or restart service manually.")
def update_repo_configs(repo_root, hostname, origin_url, lines):
    repo = Path(repo_root); updates=[]
    specs=[("products/mobile/app/public/prisma-mobile-pwa.config.json","pwa"),("products/mobile/app/deploy/cloudflare-prisma-mobile-domain.json","deploy"),("products/mobile/infra/cloudflare/prisma-mobile-cloudflare.config.json","bridge")]
    for rel, kind in specs:
        path=repo/rel
        if not path.exists(): continue
        data=json.loads(path.read_text(encoding="utf-8"))
        if kind=="pwa": data.update({"contractId":PACKAGE_ID,"mode":"pwa-cloudflare-domain","domain":hostname,"origin":f"https://{hostname}","localOrigin":origin_url,"tunnelName":DEFAULT_TUNNEL_NAME,"cloudflareTunnelHostname":hostname,"supportContact":"soporte@hitechrts.com","lastConfiguredAt":datetime.now().isoformat(timespec="seconds")})
        if kind=="deploy": data.update({"domain":hostname,"publicUrl":f"https://{hostname}/prisma-app","installUrl":f"https://{hostname}/prisma-app/install","originUrl":origin_url})
        if kind=="bridge": data.update({"hostname":hostname,"originUrl":origin_url,"publicUrl":f"https://{hostname}/prisma-app"})
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8"); updates.append(rel)
    check=repo/"products/mobile/app/public/.well-known/pwa-domain-check.json"; check.parent.mkdir(parents=True, exist_ok=True)
    check.write_text(json.dumps({"ok":True,"contractId":PACKAGE_ID,"hostname":hostname,"publicUrl":f"https://{hostname}/prisma-app","originUrl":origin_url,"generatedAt":datetime.now().isoformat(timespec="seconds")}, indent=2)+"\n", encoding="utf-8"); updates.append(str(check))
    lines.append("updated repo configs: " + ", ".join(updates))
def verify(repo_root, hostname, origin_url, config_path, lines):
    repo=Path(repo_root)
    for rel in ["products/mobile/app/public/prisma-mobile-pwa.config.json","products/mobile/app/public/manifest.webmanifest","products/mobile/app/public/prisma-mobile-sw.js","products/mobile/infra/cloudflare/prisma-mobile-cloudflare.config.json"]:
        if not (repo/rel).exists(): raise BridgeError("Missing expected file: "+rel)
    cfg=json.loads((repo/"products/mobile/app/public/prisma-mobile-pwa.config.json").read_text(encoding="utf-8"))
    if cfg.get("domain") != hostname: raise BridgeError(f"PWA domain mismatch: {cfg.get('domain')} != {hostname}")
    text=read_text(config_path)
    if not text:
        lines.append(f"WARN: cloudflared config not found yet: {config_path}"); return False
    if not has_route(text, hostname, origin_url):
        lines.append(f"WARN: cloudflared config missing route {hostname} -> {origin_url}"); return False
    if not config_has_fallback(text): raise BridgeError("cloudflared config is missing fallback http_status:404")
    lines.append("verify ok: repo config and cloudflared route block are coherent"); return True
def main():
    ap=argparse.ArgumentParser(); mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true"); mode.add_argument("--apply", action="store_true"); mode.add_argument("--verify", action="store_true")
    ap.add_argument("--repo-root", default=DEFAULT_REPO_ROOT); ap.add_argument("--hostname", default=DEFAULT_HOSTNAME); ap.add_argument("--origin-url", default=DEFAULT_ORIGIN_URL); ap.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME); ap.add_argument("--config-path", default=DEFAULT_CONFIG_PATH); ap.add_argument("--log", default=str(Path(DEFAULT_LOG_DIR)/f"prisma_mobile_cloudflare_bridge_int_{now_token()}.log"))
    args=ap.parse_args(); lines=[f"{PACKAGE_ID} started", f"mode={'apply' if args.apply else 'verify' if args.verify else 'dry-run'}"]
    try:
        hostname=normalize_hostname(args.hostname); origin_url=validate_origin_url(args.origin_url); config_path=Path(args.config_path)
        if args.verify:
            ok=verify(args.repo_root, hostname, origin_url, config_path, lines); write_log(lines,args.log); print("VERIFY OK" if ok else "VERIFY PARTIAL"); return 0 if ok else 2
        lines += [f"hostname={hostname}", f"origin_url={origin_url}", f"cloudflared_config={config_path}"]
        update_repo_configs(args.repo_root, hostname, origin_url, lines)
        if args.dry_run:
            lines.append("dry-run: would ensure DNS route and insert route before fallback"); write_log(lines,args.log); print("DRY-RUN OK"); return 0
        ensure_dns_route(args.tunnel_name, hostname, lines)
        text=read_text(config_path)
        if not text: raise BridgeError(f"cloudflared config file not found: {config_path}")
        new_text=insert_or_update_route(text, hostname, origin_url)
        if new_text != text:
            backup=config_path.with_suffix(config_path.suffix+".prisma_mobile_10.bak"); shutil.copy2(config_path, backup); config_path.write_text(new_text, encoding="utf-8", newline="\n"); lines.append(f"backup config: {backup}"); lines.append("cloudflared config updated"); restart_cloudflared(lines)
        else: lines.append("cloudflared config already contains desired route")
        ok=verify(args.repo_root, hostname, origin_url, config_path, lines); write_log(lines,args.log); print("APPLY OK" if ok else "APPLY PARTIAL"); return 0 if ok else 2
    except Exception as err:
        lines.append("ERROR: "+str(err)); write_log(lines,args.log); print("ERROR: "+str(err)); return 2
if __name__ == "__main__": raise SystemExit(main())
