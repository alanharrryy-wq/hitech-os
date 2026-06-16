from __future__ import annotations
import re
from typing import Any
from .base import VerifierResultRow, existing_target_files
CLASS_RE=re.compile(r'(?<![A-Za-z0-9_-])\.([A-Za-z_][A-Za-z0-9_-]*)')
RULE_RE=re.compile(r'(?s)([^{}]+)\{([^{}]*)\}')
COMMENT_RE=re.compile(r'(?s)/\*.*?\*/')
def run_css_module_sanity(target_files:list[str], ctx:dict[str,Any])->list[dict[str,Any]]:
    rows=[]
    for path in existing_target_files(target_files,ctx):
        if not path.name.lower().endswith('.module.css'): continue
        try:
            raw=path.read_bytes(); text=raw.decode('utf-8',errors='replace'); clean=COMMENT_RE.sub('',text)
            classes=sorted({m.group(1) for m in CLASS_RE.finditer(clean)}); issues=[]; counts={}; empty=[]
            for m in RULE_RE.finditer(clean):
                sel=' '.join(m.group(1).split()); body=m.group(2).strip()
                if not sel: issues.append('empty selector block'); continue
                counts[sel]=counts.get(sel,0)+1
                if not body or body==';': empty.append(sel)
            if empty: issues.append('empty CSS blocks: '+', '.join(empty[:8]))
            dup=sorted(k for k,v in counts.items() if v>1)
            ok=not issues; detail='CSS module sanity passed' if ok else '; '.join(issues[:8])
            if ok and dup: detail += '; duplicate top-level selectors for review: '+', '.join(dup[:8])
            rows.append(VerifierResultRow('css-module-sanity',ok,f"CSS module {'OK' if ok else 'failed'}: {path.name}",detail,metrics={'file':str(path),'class_count':len(classes),'classes':classes[:200],'duplicate_selectors':dup[:50]}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('css-module-sanity',False,f'CSS module failed: {path.name}',f'{type(exc).__name__}: {exc}',metrics={'file':str(path)}).to_dict())
    if not rows: rows.append(VerifierResultRow('css-module-sanity',True,'CSS module sanity skipped','No .module.css target files were provided.',severity_if_failed='warning').to_dict())
    return rows
