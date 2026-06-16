from __future__ import annotations
import re
from pathlib import Path
from typing import Any
from .base import VerifierResultRow, existing_target_files
IMPORT_RE=re.compile(r"import\s+([A-Za-z_$][\w$]*)\s+from\s+['\"]([^'\"]+\.module\.css)['\"]")
CLASS_RE=re.compile(r'(?<![A-Za-z0-9_-])\.([A-Za-z_][A-Za-z0-9_-]*)')
def _classes(path:Path)->set[str]:
    return {m.group(1) for m in CLASS_RE.finditer(path.read_text(encoding='utf-8',errors='replace'))} if path.exists() else set()
def run_react_css_link(target_files:list[str], ctx:dict[str,Any])->list[dict[str,Any]]:
    rows=[]
    for path in existing_target_files(target_files,ctx):
        if path.suffix.lower() not in {'.tsx','.jsx','.ts','.js'}: continue
        try:
            text=path.read_text(encoding='utf-8',errors='replace')
            for m in IMPORT_RE.finditer(text):
                alias,rel=m.group(1),m.group(2); css=(path.parent/rel).resolve()
                used={x.group(1) for x in re.finditer(r'\b'+re.escape(alias)+r'\.([A-Za-z_$][\w$-]*)\b',text)}
                used |= {x.group(1) for x in re.finditer(r'\b'+re.escape(alias)+r"\[['\"]([^'\"]+)['\"]\]",text)}
                defined=_classes(css); missing=sorted(u for u in used if u not in defined); orphan=sorted(d for d in defined if d not in used)
                ok=css.exists() and not missing
                detail='React CSS module links passed' if ok else (f'CSS module import missing: {rel}' if not css.exists() else 'Missing CSS module classes used from TSX: '+', '.join(missing[:20]))
                rows.append(VerifierResultRow('react-css-link',ok,f"React CSS link {'OK' if ok else 'failed'}: {path.name} -> {Path(rel).name}",detail,metrics={'file':str(path),'css_file':str(css),'used_classes':sorted(used),'missing_classes':missing,'orphan_class_count':len(orphan),'orphan_classes_sample':orphan[:100]}).to_dict())
        except Exception as exc:
            rows.append(VerifierResultRow('react-css-link',False,f'React CSS link failed: {path.name}',f'{type(exc).__name__}: {exc}',metrics={'file':str(path)}).to_dict())
    if not rows: rows.append(VerifierResultRow('react-css-link',True,'React CSS link skipped','No React file with CSS module import was provided.',severity_if_failed='warning').to_dict())
    return rows
