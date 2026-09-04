from __future__ import annotations
import argparse, json
from pathlib import Path
from .contracts import load_request
from .engine import preview,apply,verify,rollback_transaction
from .target_index import build_index
from .errors import GVAEError, ContractError

ROOT=Path(__file__).resolve().parents[2]
REPO_ROOT=ROOT.parent

def _blocked(exc:Exception)->dict:
    if isinstance(exc,GVAEError):
        return {"status":"BLOCKED","error":exc.code,"message":str(exc),"details":exc.details}
    return {"status":"BLOCKED","error":"INPUT_ERROR","message":str(exc),"details":{}}

def main(argv=None)->int:
    p=argparse.ArgumentParser(description="PRISMA Generic Visual Application Engine V1")
    p.add_argument("request"); p.add_argument("--transactions",default=".gvae-transactions")
    a=p.parse_args(argv)
    try:
        request=load_request(a.request)
        provider=lambda:build_index(ROOT)
        tx_root=Path(a.transactions)
        tx_root=tx_root if tx_root.is_absolute() else ROOT/tx_root
        mode=request["mode"]
        if mode=="PREVIEW": result=preview(request,provider,REPO_ROOT)
        elif mode=="APPLY": result=apply(request,provider,REPO_ROOT,tx_root)
        elif mode=="VERIFY": result=verify(request,provider,REPO_ROOT)
        elif mode=="ROLLBACK": result=rollback_transaction(request["transactionId"],request["targetId"],REPO_ROOT,tx_root)
        else: raise ContractError("unsupported mode")
        print(json.dumps(result,indent=2,ensure_ascii=False)); return 0
    except (GVAEError,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps(_blocked(exc),indent=2,ensure_ascii=False)); return 2

if __name__=="__main__": raise SystemExit(main())
