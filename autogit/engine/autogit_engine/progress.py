from __future__ import annotations
import shutil, sys, time
_last_len=0; _last_emit=0.0
def line(text: str = "") -> None:
    global _last_len
    if _last_len: sys.stdout.write("\n"); sys.stdout.flush(); _last_len=0
    if text: print(text, flush=True)
def bar(phase: str, current: int, total: int, detail: str = "", *, force: bool = False) -> None:
    global _last_len, _last_emit
    total=max(int(total or 1),1); current=max(0,min(int(current or 0),total)); pct=int(round(current*100/total))
    now=time.time()
    if not force and pct<100 and now-_last_emit<0.08: return
    _last_emit=now
    width=max(80,min(160,shutil.get_terminal_size((120,24)).columns)); bar_width=32
    filled=int(round(bar_width*pct/100)); meter="#"*filled+"."*(bar_width-filled)
    detail=str(detail or "").replace("\r"," ").replace("\n"," ")
    max_detail=max(10,width-bar_width-len(phase)-25)
    if len(detail)>max_detail: detail="..."+detail[-(max_detail-3):]
    msg=f"\r[{meter}] {pct:3d}% | faltante {100-pct:3d}% | {phase} | {detail}"
    sys.stdout.write(msg+(" "*max(0,_last_len-len(msg)))); sys.stdout.flush(); _last_len=len(msg)
def phase(title: str) -> None: line(f"\n=== {title} ===")
