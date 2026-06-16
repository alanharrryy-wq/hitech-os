from __future__ import annotations
import re
from pathlib import Path
from .base import fail
def _span(text,selector):
    selector=str(selector or '').strip()
    if not selector: fail('selector no puede venir vacio')
    m=re.search(r'(?m)(^|\n)([^{}]*?'+re.escape(selector)+r'[^{}]*?)\s*\{',text)
    if not m: return None
    i=text.find('{',m.start()); depth=0
    while i<len(text):
        if text[i]=='{': depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:
                s=m.start(0)+(1 if text[m.start(0)]=='\n' else 0); return s,i+1
        i+=1
    return None
def _rule(selector,block):
    block=str(block or '').strip()
    if not block: fail('new_block/declarations no puede venir vacio')
    return block.rstrip()+'\n' if '{' in block and '}' in block else f'{selector} {{\n{block}\n}}\n'
def render_replace_css_rule_block(target:Path,text:str,selector:str,new_block:str,label:str)->str:
    sp=_span(text,selector); repl=_rule(selector,new_block)
    if sp is None: fail(f'No encontre bloque CSS para selector {selector!r} en {target} ({label})')
    s,e=sp; return text if text[s:e].strip()==repl.strip() else text[:s]+repl+text[e:]
def render_ensure_css_class(target:Path,text:str,selector:str,declarations:str,label:str)->str:
    sp=_span(text,selector); repl=_rule(selector,declarations)
    if sp is None: return text+('' if text.endswith('\n') or not text else '\n')+repl
    s,e=sp; return text if text[s:e].strip()==repl.strip() else text[:s]+repl+text[e:]
def render_remove_css_rule_block(target:Path,text:str,selector:str,label:str)->str:
    sp=_span(text,selector)
    if sp is None: return text
    s,e=sp
    if e<len(text) and text[e:e+1]=='\n': e+=1
    return text[:s]+text[e:]
def render_ensure_css_variable(target:Path,text:str,variable:str,value:str,selector:str=':root',label:str='EnsureCssVariable')->str:
    variable=str(variable or '').strip(); value=str(value or '').strip(); selector=str(selector or ':root').strip()
    if not variable.startswith('--'): fail(f'CSS variable invalida para {label}: {variable}')
    sp=_span(text,selector)
    if sp is None: return render_ensure_css_class(target,text,selector,f'  {variable}: {value};',label)
    s,e=sp; block=text[s:e]; rg=re.compile(r'(?m)(^\s*)'+re.escape(variable)+r'\s*:\s*[^;]+;')
    nb=rg.sub(lambda m:f'{m.group(1)}{variable}: {value};',block,1) if rg.search(block) else block[:-1].rstrip()+f'\n  {variable}: {value};\n}}'
    return text[:s]+nb+text[e:]
def render_replace_jsx_class_name(target,text,old_class,new_class,label):
    if old_class not in text:
        if new_class in text: return text
        fail(f'No encontre className {old_class!r} en {target} ({label})')
    return text.replace(old_class,new_class)
def render_replace_jsx_prop(target,text,component,prop,new_value,label):
    m=re.search(r'<'+re.escape(component)+r'\b(?P<body>[^<>]*?)(/?>)',text,re.S)
    if not m: fail(f'No encontre componente JSX <{component}> en {target} ({label})')
    body=m.group('body'); rg=re.compile(r'(\s'+re.escape(prop)+r'=)(\{[^}]*\}|"[^"]*"|\'[^\']*\')',re.S)
    nb=rg.sub(lambda x:x.group(1)+new_value,body,1) if rg.search(body) else body.rstrip()+f' {prop}={new_value}'
    return text[:m.start('body')]+nb+text[m.end('body'):]
def render_insert_jsx_child(target,text,anchor,insert_text,position,label):
    if insert_text in text: return text
    i=text.find(anchor)
    if i<0: fail(f'No encontre anchor JSX para {label} en {target}')
    return text[:i]+insert_text+text[i:] if str(position or 'after').lower()=='before' else text[:i+len(anchor)]+insert_text+text[i+len(anchor):]
def render_remove_legacy_layer(target,text,selector,old_text,label):
    if old_text: return text.replace(old_text,'',1) if old_text in text else text
    if selector: return render_remove_css_rule_block(target,text,selector,label)
    fail(f'RemoveLegacyLayer requiere selector u old_text para {label}')
