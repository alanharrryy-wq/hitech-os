#!/usr/bin/env python3
from __future__ import annotations
import argparse
import ctypes
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PACKAGE_ID = "PRISMA_APP_MOBILE_10C_CLOUDFLARE_DNS_FALLBACK_REPAIR"
DEFAULT_REPO_ROOT = r"F:\repos\hitech-os\apps\terminal-de-venta-system"
DEFAULT_HOSTNAME = "prisma.hitechrts.com"
DEFAULT_ORIGIN_URL = "http://127.0.0.1:3140"
DEFAULT_PUBLIC_PATHS = ["/prisma-app", "/prisma-app/install", "/.well-known/pwa-domain-check.json"]
DEFAULT_TUNNEL_NAME = "engine"
DEFAULT_CONFIG_PATH = r"C:\Users\alanh\.cloudflared\config.yml"
DEFAULT_LOG_DIR = r"F:\descargasf"
SERVICE_NAME = "cloudflared"

class RepairError(RuntimeError):
    pass

def timestamp() -> str:
    return dt.datetime.now().strftime("%y%m%d_%H%M")

def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")

def normalize_hostname(value: str) -> str:
    host = value.strip().lower().replace("https://", "").replace("http://", "").strip("/")
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*\.[a-z]{2,}", host):
        raise RepairError(f"Invalid hostname: {value}")
    return host

def normalize_url(value: str) -> str:
    url = value.strip().rstrip("/")
    if not re.match(r"^https?://[^\s/]+(?::\d+)?$", url):
        raise RepairError(f"Invalid origin URL: {value}")
    return url

def public_base(hostname: str) -> str:
    return f"https://{hostname}"

def public_urls(hostname: str) -> list[str]:
    return [public_base(hostname) + path for path in DEFAULT_PUBLIC_PATHS]

def run(cmd: list[str], lines: list[str], timeout: int = 180) -> tuple[int, str]:
    lines.append("run: " + " ".join(str(x) for x in cmd))
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout, check=False)
    except FileNotFoundError as err:
        raise RepairError(f"Command not found: {cmd[0]}") from err
    out = p.stdout or ""
    if out.strip():
        for line in out.strip().splitlines():
            lines.append("  " + line)
    else:
        lines.append("  <no output>")
    lines.append(f"exit={p.returncode}")
    return p.returncode, out

def http_status(url: str, timeout: int = 8) -> tuple[bool, int | None, str]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "prisma-mobile-cloudflare-repair/10c"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            code = int(res.status)
            return 200 <= code < 400, code, ""
    except urllib.error.HTTPError as err:
        return False, int(err.code), str(err)
    except Exception as err:
        return False, None, str(err)

def assert_local_origin(origin_url: str, lines: list[str]) -> None:
    url = origin_url.rstrip("/") + "/prisma-app"
    ok, code, err = http_status(url, timeout=6)
    lines.append(f"local-origin: {url} ok={ok} status={code} error={err}")
    if not ok:
        raise RepairError(f"Local PRISMA Mobile origin is not healthy at {url}. Start/build mobile before repairing Cloudflare.")

def cloudflared_exists(lines: list[str]) -> str:
    exe = shutil.which("cloudflared")
    if not exe:
        raise RepairError("cloudflared not found in PATH.")
    lines.append(f"cloudflared-path: {exe}")
    return exe

def _dns_success_text(text: str, hostname: str) -> bool:
    lower = text.lower()
    return (
        "already configured" in lower
        or "already exists" in lower
        or "created" in lower
        or "added" in lower
        or "success" in lower
        or (hostname.lower() in lower and "tunnel" in lower and "error" not in lower and "failed" not in lower)
    )

def ensure_dns_route(tunnel_name: str, hostname: str, lines: list[str], require_dns: bool) -> dict[str, object]:
    cloudflared_exists(lines)
    attempts: list[list[str]] = [
        ["cloudflared", "tunnel", "route", "dns", tunnel_name, hostname],
        ["cloudflared", "tunnel", "route", "dns", "--overwrite-dns", tunnel_name, hostname],
        ["cloudflared", "tunnel", "route", "dns", "-f", tunnel_name, hostname],
    ]
    outputs: list[dict[str, object]] = []
    for cmd in attempts:
        code, out = run(cmd, lines, timeout=240)
        ok = code == 0 or _dns_success_text(out, hostname)
        outputs.append({"cmd": cmd, "exit": code, "ok": ok, "tail": out[-1200:]})
        if ok:
            lines.append(f"dns-route: {hostname} -> tunnel {tunnel_name} ensured")
            return {"ok": True, "required": require_dns, "attempts": outputs, "warning": ""}

    message = (
        f"DNS route command did not succeed for {hostname}. Continuing because an existing DNS record may already point to the tunnel. "
        "The public smoke test is the source of truth. If smoke still fails, fix the DNS record in Cloudflare Dashboard."
    )
    lines.append("dns-route-warning: " + message)
    if require_dns:
        raise RepairError(message)
    return {"ok": False, "required": require_dns, "attempts": outputs, "warning": message}

def route_block(hostname: str, origin_url: str) -> str:
    return f"  - hostname: {hostname}\n    service: {origin_url}\n"

def route_present(text: str, hostname: str, origin_url: str) -> bool:
    return bool(re.search(rf"(?ms)^\s*-\s*hostname:\s*{re.escape(hostname)}\s*[\r\n]+\s*service:\s*{re.escape(origin_url)}\s*$", text))

def ensure_ingress_route(config_path: Path, hostname: str, origin_url: str, lines: list[str]) -> bool:
    if not config_path.exists():
        raise RepairError(f"cloudflared config not found: {config_path}")
    text = config_path.read_text(encoding="utf-8")
    if "ingress:" not in text:
        raise RepairError(f"cloudflared config has no ingress section: {config_path}")
    block = route_block(hostname, origin_url)
    same_host = re.compile(rf"(?ms)^\s*-\s*hostname:\s*{re.escape(hostname)}\s*[\r\n]+\s*service:\s*[^\r\n]+\s*", re.MULTILINE)
    if same_host.search(text):
        new_text = same_host.sub(block, text)
    else:
        fallback = re.search(r"(?mi)^\s*-\s*service:\s*http_status:404\s*$", text)
        if fallback:
            new_text = text[:fallback.start()] + block + text[fallback.start():]
        else:
            if not text.endswith("\n"):
                text += "\n"
            new_text = text + block + "  - service: http_status:404\n"
    if new_text != text:
        backup = config_path.with_name(config_path.name + f".prisma_mobile_10c_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
        shutil.copy2(config_path, backup)
        config_path.write_text(new_text, encoding="utf-8", newline="\n")
        lines.append(f"config-backup: {backup}")
        lines.append(f"config-updated: {hostname} -> {origin_url}")
        return True
    lines.append(f"config-ok: route already present {hostname} -> {origin_url}")
    return False

def is_windows_admin() -> bool:
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"

def get_service_snapshot(lines: list[str]) -> dict[str, object]:
    ps = "$s=Get-CimInstance Win32_Service -Filter \"Name='cloudflared'\" -ErrorAction SilentlyContinue; if($s){$s | Select-Object Name,State,StartMode,PathName,StartName,ProcessId | ConvertTo-Json -Compress}else{Write-Output '{}'}"
    code, out = run(["powershell", "-NoProfile", "-Command", ps], lines, timeout=60)
    if code != 0:
        return {}
    try:
        data = json.loads(out.strip() or "{}")
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}

def normalize_cmdline(text: str) -> str:
    return " ".join((text or "").strip().split()).lower().replace("/", "\\")

def ensure_service_image_path(tunnel_name: str, config_path: Path, lines: list[str], allow_elevation: bool) -> dict[str, object]:
    exe = cloudflared_exists(lines)
    desired = f'"{exe}" --config "{config_path}" tunnel run {tunnel_name}'
    snapshot = get_service_snapshot(lines)
    current = str(snapshot.get("PathName", "") or snapshot.get("path_name", "") or "")
    current_ok = normalize_cmdline(current) == normalize_cmdline(desired)
    lines.append(f"service-current-imagepath: {current}")
    lines.append(f"service-desired-imagepath: {desired}")
    if current_ok:
        lines.append("service-imagepath: OK")
        return {"changed": False, "current": current, "desired": desired, "ok": True}

    set_cmd = (
        "$desired = " + ps_quote(desired) + "; "
        "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\cloudflared' "
        "-Name ImagePath -Value $desired -ErrorAction Stop"
    )
    if os.name == "nt" and not is_windows_admin() and allow_elevation:
        command = (
            "$cmd = " + ps_quote(set_cmd) + "; "
            "$p = Start-Process -FilePath 'powershell' -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-Command',$cmd) -Verb RunAs -Wait -PassThru; "
            "if ($null -eq $p) { exit 9001 }; exit $p.ExitCode"
        )
        code, _ = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command], lines, timeout=600)
    else:
        code, _ = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", set_cmd], lines, timeout=120)
    if code != 0:
        raise RepairError("Unable to set cloudflared service ImagePath. Run PowerShell as Administrator and re-run repair.")
    lines.append("service-imagepath-updated: OK")
    return {"changed": True, "current": current, "desired": desired, "ok": True}

def restart_cloudflared(lines: list[str], allow_elevation: bool = True) -> None:
    direct = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "Restart-Service -Name 'cloudflared' -Force -ErrorAction Stop"]
    if os.name == "nt" and not is_windows_admin() and allow_elevation:
        command = (
            "$p = Start-Process -FilePath 'powershell' "
            "-ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-Command',\"Restart-Service -Name 'cloudflared' -Force -ErrorAction Stop\") "
            "-Verb RunAs -Wait -PassThru; if ($null -eq $p) { exit 9001 }; exit $p.ExitCode"
        )
        code, _ = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command], lines, timeout=600)
    else:
        code, _ = run(direct, lines, timeout=180)
    if code != 0:
        raise RepairError("cloudflared service restart failed. Open PowerShell as Administrator and run the repair again.")
    lines.append("cloudflared-restart: OK")
    time.sleep(8)

def smoke_public(hostname: str, lines: list[str], attempts: int = 6, delay: float = 3.0) -> bool:
    urls = public_urls(hostname)
    all_ok = False
    for attempt in range(1, attempts + 1):
        lines.append(f"public-smoke-attempt={attempt}/{attempts}")
        all_ok = True
        for url in urls:
            ok, code, err = http_status(url, timeout=8)
            lines.append(f"  public: {url} ok={ok} status={code} error={err}")
            if not ok:
                all_ok = False
        if all_ok:
            break
        time.sleep(delay)
    if all_ok:
        lines.append("public-smoke: OK")
    else:
        lines.append("public-smoke: FAIL")
        lines.append("diagnosis: If local origin is 200 and config contains the route, public 404 means the running cloudflared service still uses another config or Dashboard DNS does not point prisma.hitechrts.com to this tunnel.")
    return all_ok

def write_log(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Repair live Cloudflare route for PRISMA Mobile PWA domain with DNS fallback.")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--smoke", action="store_true")
    mode.add_argument("--diagnose", action="store_true")
    p.add_argument("--repo-root", default=DEFAULT_REPO_ROOT)
    p.add_argument("--hostname", default=DEFAULT_HOSTNAME)
    p.add_argument("--origin-url", default=DEFAULT_ORIGIN_URL)
    p.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME)
    p.add_argument("--config-path", default=DEFAULT_CONFIG_PATH)
    p.add_argument("--require-dns-bind", action="store_true")
    p.add_argument("--no-elevate", action="store_true")
    p.add_argument("--log", default=str(Path(DEFAULT_LOG_DIR) / f"prisma_mobile_cloudflare_live_route_repair_10c_int_{timestamp()}.log"))
    return p

def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    lines = [f"{PACKAGE_ID} started", f"generatedAt={now_iso()}"]
    try:
        hostname = normalize_hostname(args.hostname)
        origin_url = normalize_url(args.origin_url)
        config_path = Path(args.config_path)
        lines += [f"hostname={hostname}", f"originUrl={origin_url}", f"tunnelName={args.tunnel_name}", f"configPath={config_path}"]
        if args.diagnose:
            assert_local_origin(origin_url, lines)
            ensure_dns_route(args.tunnel_name, hostname, lines, require_dns=False)
            text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
            lines.append(f"config-route-present={route_present(text, hostname, origin_url)}")
            get_service_snapshot(lines)
            ok = smoke_public(hostname, lines, attempts=2, delay=2.0)
            write_log(Path(args.log), lines)
            print("DIAGNOSE OK" if ok else "DIAGNOSE WRITTEN")
            return 0 if ok else 2
        if args.smoke:
            assert_local_origin(origin_url, lines)
            ok = smoke_public(hostname, lines, attempts=3, delay=2.0)
            write_log(Path(args.log), lines)
            print("SMOKE OK" if ok else "SMOKE FAIL")
            return 0 if ok else 2
        if args.verify:
            text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
            cfg_ok = bool(text and route_present(text, hostname, origin_url) and "http_status:404" in text)
            assert_local_origin(origin_url, lines)
            public_ok = smoke_public(hostname, lines, attempts=2, delay=2.0)
            lines.append(f"verify-config-ok={cfg_ok}")
            write_log(Path(args.log), lines)
            print("VERIFY OK" if cfg_ok and public_ok else "VERIFY BLOCKED")
            return 0 if cfg_ok and public_ok else 2
        assert_local_origin(origin_url, lines)
        dns_result = ensure_dns_route(args.tunnel_name, hostname, lines, require_dns=args.require_dns_bind)
        ensure_ingress_route(config_path, hostname, origin_url, lines)
        ensure_service_image_path(args.tunnel_name, config_path, lines, allow_elevation=not args.no_elevate)
        restart_cloudflared(lines, allow_elevation=not args.no_elevate)
        get_service_snapshot(lines)
        ok = smoke_public(hostname, lines, attempts=10, delay=3.0)
        lines.append("dns-result-json=" + json.dumps(dns_result, ensure_ascii=False))
        write_log(Path(args.log), lines)
        print("APPLY OK" if ok else "APPLY NEEDS DNS/DASHBOARD ATTENTION")
        return 0 if ok else 2
    except Exception as err:
        lines.append("ERROR: " + str(err))
        write_log(Path(args.log), lines)
        print("ERROR: " + str(err))
        return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
