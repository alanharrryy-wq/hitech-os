from __future__ import annotations
import re
from dataclasses import dataclass
from .errors import AmbiguousTarget, TargetNotFound, PriorityOverrideForbidden, BlockedUnsupportedCss

_PROP=re.compile(r"^(?:--)?[A-Za-z_][A-Za-z0-9_-]*$")
_IMPORTANT=re.compile(r"!\s*important\b",re.I)

@dataclass(frozen=True)
class Decl:
    prop:str
    value_start:int
    value_end:int

def _strip_comments(text:str)->str:
    return re.sub(r"/\*.*?\*/","",text,flags=re.S)

def _lexical_important(text:str)->bool:
    quote=None; comment=False; escape=False; buf=[]; i=0
    while i<len(text):
        c=text[i]; n=text[i+1] if i+1<len(text) else ""
        if comment:
            if c=="*" and n=="/": comment=False; i+=2; continue
            i+=1; continue
        if quote:
            if escape: escape=False
            elif c=="\\": escape=True
            elif c==quote: quote=None
            i+=1; continue
        if c=="/" and n=="*": comment=True; i+=2; continue
        if c in ("'",'"'): quote=c; i+=1; continue
        buf.append(c); i+=1
    return bool(_IMPORTANT.search("".join(buf)))

def _top_level_blocks(text:str)->list[tuple[str,int,int]]:
    blocks=[]; depth=0; quote=None; comment=False; escape=False; block_start=-1; selector_start=0; i=0
    while i<len(text):
        c=text[i]; n=text[i+1] if i+1<len(text) else ""
        if comment:
            if c=="*" and n=="/": comment=False; i+=2; continue
            i+=1; continue
        if quote:
            if escape: escape=False
            elif c=="\\": escape=True
            elif c==quote: quote=None
            i+=1; continue
        if c=="/" and n=="*": comment=True; i+=2; continue
        if c in ("'",'"'): quote=c; i+=1; continue
        if c=="{":
            if depth==0:
                selector=_strip_comments(text[selector_start:i]).strip()
                if selector.startswith("@"): raise BlockedUnsupportedCss("top-level at-rule blocks are unsupported in V1")
                block_start=i+1
            else:
                raise BlockedUnsupportedCss("nested CSS is unsupported in V1")
            depth+=1
        elif c=="}":
            depth-=1
            if depth<0: raise BlockedUnsupportedCss("unbalanced CSS braces")
            if depth==0 and block_start>=0:
                selector=_strip_comments(text[selector_start:block_start-1]).strip()
                blocks.append((selector,block_start,i)); selector_start=i+1; block_start=-1
        i+=1
    if depth!=0 or quote or comment: raise BlockedUnsupportedCss("malformed CSS")
    if _strip_comments(text[selector_start:]).strip():
        raise BlockedUnsupportedCss("trailing CSS outside a rule is unsupported")
    return blocks

def _find_colon(segment:str)->int|None:
    quote=None; comment=False; escape=False; i=0
    while i<len(segment):
        c=segment[i]; n=segment[i+1] if i+1<len(segment) else ""
        if comment:
            if c=="*" and n=="/": comment=False; i+=2; continue
            i+=1; continue
        if quote:
            if escape: escape=False
            elif c=="\\": escape=True
            elif c==quote: quote=None
            i+=1; continue
        if c=="/" and n=="*": comment=True; i+=2; continue
        if c in ("'",'"'): quote=c; i+=1; continue
        if c==":": return i
        i+=1
    return None

def _declarations(body:str)->list[Decl]:
    decls=[]; quote=None; comment=False; escape=False; start=0; i=0
    while i<len(body):
        c=body[i]; n=body[i+1] if i+1<len(body) else ""
        if comment:
            if c=="*" and n=="/": comment=False; i+=2; continue
            i+=1; continue
        if quote:
            if escape: escape=False
            elif c=="\\": escape=True
            elif c==quote: quote=None
            i+=1; continue
        if c=="/" and n=="*": comment=True; i+=2; continue
        if c in ("'",'"'): quote=c; i+=1; continue
        if c in "{}": raise BlockedUnsupportedCss("nested braces in declaration body")
        if c==";":
            segment=body[start:i]
            colon=_find_colon(segment)
            cleaned=_strip_comments(segment).strip()
            if cleaned:
                if colon is None: raise BlockedUnsupportedCss("declaration missing colon")
                raw_prop=segment[:colon]
                prop=_strip_comments(raw_prop).strip()
                if not _PROP.fullmatch(prop): raise BlockedUnsupportedCss(f"unsupported declaration property: {prop}")
                raw_value=segment[colon+1:]
                lead=len(raw_value)-len(raw_value.lstrip())
                trail=len(raw_value)-len(raw_value.rstrip())
                vs=start+colon+1+lead
                ve=i-trail
                if vs>ve: raise BlockedUnsupportedCss("empty declaration value")
                decls.append(Decl(prop,vs,ve))
            start=i+1
        i+=1
    if quote or comment: raise BlockedUnsupportedCss("malformed CSS declaration body")
    if _strip_comments(body[start:]).strip():
        raise BlockedUnsupportedCss("V1 requires semicolon-terminated declarations")
    return decls

def patch_css(text:str, selector:str, declarations:dict[str,str])->str:
    if any(_lexical_important(str(v)) for v in declarations.values()):
        raise PriorityOverrideForbidden("priority override syntax is forbidden")
    matches=[row for row in _top_level_blocks(text) if row[0]==selector]
    if not matches: raise TargetNotFound(f"selector not found: {selector}")
    if len(matches)!=1: raise AmbiguousTarget(f"selector is not unique: {selector}")
    _,bs,be=matches[0]
    body=text[bs:be]
    parsed=_declarations(body)
    for d in parsed:
        if _lexical_important(body[d.value_start:d.value_end]):
            raise PriorityOverrideForbidden("priority override syntax is forbidden")
    replacements=[]
    for prop,desired in declarations.items():
        hits=[d for d in parsed if d.prop==prop]
        if not hits: raise TargetNotFound(f"declaration not found: {selector}:{prop}")
        if len(hits)!=1: raise AmbiguousTarget(f"declaration is not unique: {selector}:{prop}")
        d=hits[0]; replacements.append((d.value_start,d.value_end,desired))
    out=body
    for a,b,val in sorted(replacements,reverse=True):
        out=out[:a]+val+out[b:]
    return text[:bs]+out+text[be:]
