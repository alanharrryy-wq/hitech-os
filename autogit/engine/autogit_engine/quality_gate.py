from __future__ import annotations
def pass_fail(name,ok,detail=""): return {"gate":name,"ok":bool(ok),"detail":detail}
def require_all(gates):
    failed=[g for g in gates if not g.get("ok")]
    if failed: raise RuntimeError("Quality gates failed: "+", ".join(g["gate"] for g in failed))
