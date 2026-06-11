# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, concurrent.futures as futures, datetime as dt, json, socket, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

def progress(done,total,label):
    total=max(total,1)
    pct=int(round(done*100/total))
    filled=int(24*done/total)
    print(f"[{'#'*filled}{'.'*(24-filled)}] {pct:3d}% | queda {total-done:02d}/{total:02d} | {label}", flush=True)

def load_json(path, default):
    p=Path(path)
    if not p.exists():
        return default
    raw=p.read_text(encoding="utf-8-sig", errors="replace")
    return json.loads(raw) if raw.strip() else default

def save_json(path,data):
    p=Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def port_open(host,port,timeout=1.0):
    try:
        with socket.create_connection((host,int(port)),timeout=timeout):
            return True
    except OSError:
        return False

def wait_services(services,wait_seconds):
    deadline=time.time()+max(0,wait_seconds)
    found={}
    while True:
        for svc in services:
            sid=str(svc.get("id") or svc.get("name") or svc.get("port") or "unknown")
            port=svc.get("port")
            if port and sid not in found and port_open("127.0.0.1",int(port),0.8):
                found[sid]=svc
        if found or time.time()>=deadline:
            return list(found.values())
        time.sleep(2)

def join_url(base,path):
    base=str(base or "").rstrip("/")+"/"
    p="/"+str(path or "/").strip().lstrip("/")
    if p=="//":
        p="/"
    return urllib.parse.urljoin(base,p.lstrip("/"))

def fetch(url,timeout,retries):
    started=time.time()
    last=None
    for attempt in range(retries+1):
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"PRISMA-dev-route-warmer/2.0",
                "Accept":"text/html,application/xhtml+xml,application/json,*/*",
                "Cache-Control":"no-cache",
            })
            with urllib.request.urlopen(req,timeout=max(2,timeout)) as resp:
                status=int(getattr(resp,"status",200))
                return {"url":url,"ok":200<=status<400,"status":status,"ms":int((time.time()-started)*1000),"error":None}
        except urllib.error.HTTPError as exc:
            return {"url":url,"ok":False,"status":int(exc.code),"ms":int((time.time()-started)*1000),"error":f"HTTPError: {exc.code}"}
        except Exception as exc:
            last=f"{type(exc).__name__}: {exc}"
            if attempt<retries:
                time.sleep(1.5)
    return {"url":url,"ok":False,"status":None,"ms":int((time.time()-started)*1000),"error":last}

def sid(svc):
    return str(svc.get("id") or svc.get("name") or svc.get("port") or "unknown")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--wait-seconds",type=int,default=180)
    ap.add_argument("--timeout-seconds",type=int,default=25)
    ap.add_argument("--max-workers",type=int,default=14)
    args=ap.parse_args()

    root=Path(args.root)
    cfg=load_json(root/"internal/config/dev_warm_routes.json",{})
    services_cfg=load_json(root/"internal/config/services.json",{"services":[]})
    services=list(services_cfg.get("services",[]))
    logs=root/"internal/logs"
    logs.mkdir(parents=True, exist_ok=True)

    report={
        "status":"ok",
        "created_at":dt.datetime.now().isoformat(timespec="seconds"),
        "root":str(root),
        "rules":["no kill","no browser","no server start","no prisma regen"],
        "services_total":len(services),
        "services_reachable":[],
        "results":[],
        "warnings":[]
    }

    progress(1,5,"buscando servicios vivos")
    reachable=wait_services(services,args.wait_seconds)
    report["services_reachable"]=[sid(s) for s in reachable]

    if not reachable:
        report["warnings"].append("No hubo servicios vivos en 127.0.0.1 durante la ventana de espera.")
        save_json(logs/"warmup last.json",report)
        (logs/"warmup last.md").write_text("# PRISMA warmup\n\nNo hubo servicios vivos. No se toco nada.\n",encoding="utf-8")
        progress(5,5,"sin servicios vivos")
        print("No encontre servicios vivos. No se toco nada.")
        return 0

    urls=[]
    routes_by_id=dict(cfg.get("serviceRoutes",{}))
    global_paths=list(cfg.get("globalPaths",["/"]))
    for svc in reachable:
        service=sid(svc)
        base=svc.get("localUrl") or f"http://127.0.0.1:{svc.get('port')}/"
        paths=[]
        paths.extend(global_paths)
        if svc.get("healthPath"):
            paths.append(svc["healthPath"])
        paths.extend(svc.get("alternateHealthPaths") or [])
        paths.extend(routes_by_id.get(service,[]))
        seen=[]
        for p in paths:
            p=p or "/"
            if p not in seen:
                seen.append(p)
        for p in seen:
            urls.append({"service":service,"path":p,"url":join_url(base,p)})

    progress(2,5,f"{len(urls)} rutas preparadas")
    results=[]
    workers=max(1,min(int(args.max_workers),18,len(urls)))
    done=0
    with futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs={ex.submit(fetch,u["url"],args.timeout_seconds,int(cfg.get("retries",1))):u for u in urls}
        total=len(futs)
        for fut in futures.as_completed(futs):
            meta=futs[fut]
            item=fut.result()
            item.update({"service":meta["service"],"path":meta["path"]})
            results.append(item)
            done+=1
            progress(done,total,f"warm {meta['service']} {meta['path']}")

    report["results"]=sorted(results,key=lambda x:(x["service"],x["path"]))
    not_found=[r for r in results if r.get("status")==404]
    hard_fail=[r for r in results if not r["ok"] and r.get("status") not in (404,)]
    if not_found:
        report["warnings"].append(f"{len(not_found)} rutas dieron 404. Warning.")
    if hard_fail:
        report["warnings"].append(f"{len(hard_fail)} rutas fallaron por conexion/timeout/HTTP no permitido.")

    ok=len([r for r in results if r["ok"]])
    progress(5,5,f"terminado: {ok}/{len(results)} ok")
    save_json(logs/"warmup last.json",report)

    lines=[
        "# PRISMA warmup",
        "",
        f"- Servicios vivos: {', '.join(report['services_reachable'])}",
        f"- Rutas OK: {ok}/{len(results)}",
        f"- Warnings: {len(report['warnings'])}",
        "",
        "No mata procesos, no abre navegador, no levanta servidores, no toca Prisma.",
        ""
    ]
    for w in report["warnings"]:
        lines.append(f"- WARNING: {w}")
    (logs/"warmup last.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"Log: {logs / 'warmup last.md'}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
