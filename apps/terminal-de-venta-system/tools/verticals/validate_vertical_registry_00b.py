#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REG = ROOT/'shared'/'verticals'/'registry'/'vertical-registry.v0.json'
CAP_RE = re.compile(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$')
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def main():
    if not REG.exists():
        print('ERROR missing registry')
        return 1
    reg=load(REG); seen=set(); errors=[]
    for item in reg.get('verticals',[]):
        vid=item['id']
        if vid in seen: errors.append('duplicate '+vid)
        seen.add(vid)
        prof=ROOT/item['profilePath']
        if not prof.exists(): errors.append('missing profile '+vid); continue
        p=load(prof)
        if p.get('id')!=vid: errors.append('id mismatch '+vid)
        for key in ['capabilities','events','permissions','tabletBlockedCapabilities']:
            vals=p.get(key,[])
            if len(vals)!=len(set(vals)): errors.append('duplicates in '+vid+' '+key)
            for val in vals:
                if not CAP_RE.match(val): errors.append('bad namespace '+vid+' '+key+' '+val)
        if not p.get('tabletNavigation'): errors.append('empty tablet nav '+vid)
        if not p.get('pcNavigation'): errors.append('empty pc nav '+vid)
        if set(p.get('capabilities',[])) & set(p.get('tabletBlockedCapabilities',[])): errors.append('blocked capability active '+vid)
        if len(p.get('acceptanceCriteria',[]))<3: errors.append('few acceptance '+vid)
    if errors:
        for e in errors: print('ERROR:',e)
        return 1
    print(f'OK vertical registry: {len(seen)} verticals validated')
    return 0
if __name__=='__main__': raise SystemExit(main())
