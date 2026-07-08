# -*- coding: utf-8 -*-
from __future__ import annotations
import csv, json, re
from pathlib import Path
from typing import Any

CONTROL_SPECS = [
 ('backgroundColor','background',['panel','card','button','input','backgroundLayer','glassShell'],['text','priceText','icon','buttonText'],['base','hover','selected','disabled'],['color'],'transparent background if alpha=0','background-color','transparent',False),
 ('backgroundAlpha','background',['panel','card','button','modal','backgroundLayer','glassShell'],['text','icon','buttonText'],['base','hover','selected','disabled'],['color.alpha'],'background transparent/no veil','background-color','transparent',True),
 ('gradient','background',['panel','card','backgroundLayer','hero','glassShell'],['text','priceText','icon','buttonText'],['base','hover','selected'],['gradient','color'],'background-image:none','background-image','none',True),
 ('overlayImage','background',['backgroundLayer','hero','panel'],['text','buttonText','icon','priceText'],['base'],['image','color.alpha'],'background-image:none','background-image','none',True),
 ('backdropBlur','glass',['panel','modal','backgroundLayer','glassShell','surfaceShell'],['text','numericText','buttonText','icon','priceText'],['base','hover','selected'],['effect.blur'],'backdrop-filter:none; filter:none','backdrop-filter','none',True),
 ('glassSaturation','glass',['glassShell','panel','modal','backgroundLayer'],['text','icon','buttonText','priceText'],['base','hover','selected'],['effect.saturation'],'filter:none or saturate(1)','filter','none',True),
 ('refraction','glass',['glassShell','liquidLayer','edgeHighlight'],['text','buttonText','icon','priceText'],['base','hover'],['effect.refraction'],'transform/filter none','filter','none',True),
 ('specularHighlight','glass',['glassShell','edgeHighlight','button','card'],['text','priceText','buttonText'],['base','hover','selected'],['effect.highlight','color.alpha'],'opacity:0 or transparent','opacity','0',True),
 ('noise','glass',['glassShell','panel','backgroundLayer'],['text','icon','priceText','buttonText'],['base'],['effect.noise'],'background-image:none; opacity:0','background-image','none',True),
 ('borderWidth','border',['panel','card','button','input','modal','glassShell'],['text','icon','buttonText'],['base','hover','focus-visible','selected','disabled'],['border.width'],'border-width:0','border-width','0',False),
 ('borderColor','border',['panel','card','button','input','modal','glassShell'],['text','icon','buttonText'],['base','hover','focus-visible','selected','disabled'],['color','border.color'],'border-color:transparent','border-color','transparent',False),
 ('borderAlpha','border',['panel','card','button','input','modal','glassShell'],['text','icon','buttonText'],['base','hover','focus-visible','selected','disabled'],['border.alpha','color.alpha'],'border transparent/no residual stroke','border-color','transparent',True),
 ('radius','border',['panel','card','button','input','modal','image','glassShell'],['text','icon','buttonText'],['base','hover','selected'],['radius'],'border-radius:0','border-radius','0',False),
 ('innerStroke','border',['glassShell','panel','card','button'],['text','icon','buttonText','priceText'],['base','hover','selected'],['border.inner','shadow.inset'],'box-shadow:none','box-shadow','none',True),
 ('shadow','shadowGlow',['panel','card','button','modal','popover','glassShell'],['text','buttonText','priceText'],['base','hover','selected','disabled'],['effect.shadow'],'box-shadow:none','box-shadow','none',True),
 ('glow','shadowGlow',['button','panel','card','icon','glassShell','edgeHighlight'],['bodyText','priceText'],['base','hover','focus-visible','selected'],['effect.glow'],'box-shadow:none; filter:none','box-shadow','none',True),
 ('elevation','shadowGlow',['panel','card','modal','popover','button'],['text','icon','buttonText'],['base','hover','selected'],['effect.elevation'],'box-shadow:none; transform:none','box-shadow','none',True),
 ('ambientLight','shadowGlow',['glassShell','backgroundLayer','panel','card'],['text','icon','buttonText','priceText'],['base','hover'],['effect.light','color.alpha'],'opacity:0; box-shadow:none','box-shadow','none',True),
 ('pillness','shape',['button','badge','chip','input','pill'],['text','icon','priceText'],['base','hover','selected'],['radius'],'border-radius:0','border-radius','0',False),
 ('clip','shape',['image','card','panel','glassShell','backgroundLayer'],['text','buttonText','priceText'],['base'],['shape.clip'],'clip-path:none; mask:none','clip-path','none',True),
 ('padding','spacing',['panel','card','button','input','modal','listItem'],['text','icon','priceText'],['base','hover','selected'],['spacing'],'padding:0','padding','0',False),
 ('gap','spacing',['row','column','grid','stack','toolbar','actionArea'],['text','icon','buttonText'],['base'],['spacing'],'gap:0','gap','0',False),
 ('inset','spacing',['absoluteLayer','overlay','badge','edgeHighlight'],['text','priceText','buttonText'],['base'],['spacing'],'inset:0 or no offset','inset','0',True),
 ('margin','spacing',['panel','card','button','listItem','section'],['text','icon','buttonText'],['base'],['spacing'],'margin:0','margin','0',False),
 ('width','layout',['panel','card','button','input','image','container'],['inlineText','iconText'],['base'],['size'],'auto or 0 only if safe','width','auto',True),
 ('height','layout',['panel','card','button','input','image','container'],['inlineText','iconText'],['base'],['size'],'auto or 0 only if safe','height','auto',True),
 ('alignment','layout',['row','column','grid','container','toolbar','actionArea'],['text','buttonText','icon'],['base'],['layout.alignment'],'initial/default alignment','align-items/justify-content','initial',True),
 ('fontSize','typography',['text','buttonText','priceText','label','heading'],['panel','card','background','icon'],['base','hover','selected','disabled'],['typography.size'],'BLOCKED readable minimum','font-size','BLOCKED',False),
 ('fontWeight','typography',['text','buttonText','priceText','label','heading'],['panel','card','background','icon'],['base','hover','selected','disabled'],['typography.weight'],'normal/default','font-weight','normal',False),
 ('lineHeight','typography',['text','buttonText','priceText','label','heading'],['panel','card','background','icon'],['base'],['typography.lineHeight'],'normal/default','line-height','normal',False),
 ('letterSpacing','typography',['text','buttonText','priceText','label','heading'],['panel','card','background','icon'],['base','hover','selected'],['typography.letterSpacing'],'letter-spacing:0','letter-spacing','0',False),
 ('textColor','typography',['text','buttonText','priceText','label','heading','iconText'],['panel','backgroundLayer','glassShell'],['base','hover','focus-visible','selected','disabled','warning','error','success'],['color.text'],'BLOCKED unless target hidden','color','BLOCKED',False),
 ('iconSize','icon',['icon','buttonIcon','navIcon'],['text','panel','card','background'],['base','hover','selected','disabled'],['icon.size'],'BLOCKED unless hidden icon','width/height','BLOCKED',False),
 ('iconStroke','icon',['icon','buttonIcon','navIcon'],['text','panel','card','background'],['base','hover','selected','disabled'],['icon.stroke','color'],'stroke:none','stroke','none',False),
 ('iconFill','icon',['icon','buttonIcon','navIcon'],['text','panel','card','background'],['base','hover','selected','disabled'],['icon.fill','color'],'fill:none','fill','none',False),
 ('transitionDuration','motion',['button','panel','card','modal','popover','icon'],['staticText','priceText'],['hover','focus-visible','pressed','selected','disabled'],['motion.duration'],'transition-duration:0ms','transition-duration','0ms',False),
 ('easing','motion',['button','panel','card','modal','popover','icon'],['staticText'],['hover','pressed','selected'],['motion.easing'],'linear/default','transition-timing-function','linear',False),
 ('transformScale','motion',['button','card','icon','popover'],['text','priceText','layoutContainer'],['hover','pressed','selected'],['motion.transform'],'transform:none','transform','none',True),
 ('focusRing','accessibility',['button','input','select','link','tab','cardButton'],['nonInteractivePanel','background','staticText'],['focus-visible'],['focus.color','focus.width','focus.offset'],'BLOCKED: focus must remain visible','outline','BLOCKED',True),
 ('contrastGuard','accessibility',['text','buttonText','icon','border','focusRing'],['decorativeBackground'],['base','hover','focus-visible','selected','disabled'],['a11y.contrast'],'BLOCKED','guard','BLOCKED',True),
 ('disabledOpacity','accessibility',['button','input','select','tab','cardButton'],['background','staticText'],['disabled'],['state.disabled.opacity'],'BLOCKED if disabled indistinguishable','opacity','BLOCKED',True),
]

def _controls():
    return [{'control':c,'family':fam,'label':c,'appliesTo':ap,'blockedFor':bl,'allowedStates':st,'tokenTypes':tok,'zeroMeans':zero,'cssOutput':{'property':prop,'zero':zval},'requiresRuntimeCheck':rt} for c,fam,ap,bl,st,tok,zero,prop,zval,rt in CONTROL_SPECS]
CONTROL_FAMILIES=_controls()

KIND_ALIASES={'button':['button','btn','action','cta','tab','chip'],'buttonText':['buttontext','btntext','ctaText'],'priceText':['price','total','amount','money','currency'],'text':['text','label','title','heading','caption','copy'],'icon':['icon','glyph','svg'],'panel':['panel','card','modal','popover','shell','glass','surface','container','section'],'glassShell':['glass','blur','frost','liquid','shell'],'backgroundLayer':['background','backdrop','bg','overlay'],'row':['row','toolbar','rail','dock'],'column':['column','stack'],'grid':['grid'],'input':['input','select','field','search']}
PROTECTED_HINTS=('/pos','checkout','cart','charge','payment','tender','products/pc','products/mobile','shared/','/shared/','worker','/api/','route.ts','package.json','pnpm-lock','schema.prisma','governance')

def _write_json(p:Path,d:Any): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def _cell(v:Any)->str: return json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else ('' if v is None else str(v))
def _write_csv(p:Path, rows:list[dict[str,Any]]):
    p.parent.mkdir(parents=True,exist_ok=True); keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys or ['empty']); w.writeheader(); [w.writerow({k:_cell(r.get(k,'')) for k in keys}) for r in rows]
def _slug(s:str)->str: return (re.sub(r'[^A-Za-z0-9_.:-]+','-',str(s).strip()).strip('-') or 'unknown')[:140]
def _kind(blob:str)->str:
    low=blob.lower()
    for k,hints in KIND_ALIASES.items():
        if any(h.lower() in low for h in hints): return k
    return 'unknown'
def _states(blob:str)->list[str]:
    low=blob.lower(); out=['base']; checks={'hover':[':hover','hover'],'focus-visible':['focus-visible',':focus','focus'],'pressed':['pressed',':active','active'],'selected':['selected','aria-selected','data-state'],'disabled':['disabled','aria-disabled'],'loading':['loading','busy'],'error':['error','danger','invalid'],'success':['success','valid'],'warning':['warning','warn']}
    for k,hints in checks.items():
        if any(h in low for h in hints) and k not in out: out.append(k)
    return out
def _protected(surface:str,*parts:str):
    blob=' '.join([surface,*parts]).lower().replace('\\','/')
    if surface in {'pc','mobile','cloud-center','control-center'}: return True, f'{surface} blocked for visual preset promotion by default'
    for h in PROTECTED_HINTS:
        if h in blob: return True, f'protected hint {h}'
    return False,''
def _applies(ctrl:dict[str,Any], kind:str, state:str)->bool:
    k=kind.lower(); ap=[x.lower() for x in ctrl.get('appliesTo',[])]; bl=[x.lower() for x in ctrl.get('blockedFor',[])]
    if k in bl or any(b in k for b in bl): return False
    if k not in ap and not any(a in k or k in a for a in ap): return False
    states=[x.lower() for x in ctrl.get('allowedStates',[])]
    return state.lower() in states or 'base' in states

def build_preset_target_matrix(surface_registry, component_owner, selector_rows, layer_rows, token_rows):
    rows=[]
    for s in selector_rows:
        surface=str(s.get('surface','unknown')); selector=str(s.get('selector','')); defined=str(s.get('definedIn',''))
        kind=_kind(selector+' '+defined); protected, reason=_protected(surface,defined,selector)
        for state in _states(str(s.get('states',''))+' '+selector):
            allowed=[c['control'] for c in CONTROL_FAMILIES if _applies(c,kind,state)]
            rows.append({'targetId':f'{surface}.{_slug(Path(defined).stem)}.{_slug(selector)}.{state}','surface':surface,'route':'','component':Path(defined).stem if defined else '(css)','sourceFile':defined,'layer':selector,'role':selector,'kind':kind,'state':state,'eligible':bool((not protected) and kind!='unknown'),'eligibilityLevel':'TARGET_ROLE_STATE' if (not protected and kind!='unknown') else 'BLOCKED_OR_UNCLASSIFIED','allowedControls':allowed,'blockedControls':[],'blockedReason':reason if protected else ('' if kind!='unknown' else 'kind not recognized enough for preset'),'requires':['scopeGate','tokenGate','stateGate','zeroGate','doNotTouchGate','rollbackGate']+(['runtimeProbeGate'] if any(c for c in CONTROL_FAMILIES if c.get('requiresRuntimeCheck') and c['control'] in allowed) else [])})
    for c in component_owner:
        surface=str(c.get('surface','unknown')); src=str(c.get('componentFile','')); comp=str(c.get('componentId') or Path(src).stem); kind=_kind(comp+' '+src); protected,reason=_protected(surface,src,comp)
        rows.append({'targetId':f'{surface}.{_slug(comp)}.component.base','surface':surface,'route':'','component':comp,'sourceFile':src,'layer':'component','role':comp,'kind':kind,'state':'base','eligible':bool((not protected) and kind!='unknown'),'eligibilityLevel':'COMPONENT_FALLBACK_NEEDS_ROLE_CONFIRMATION','allowedControls':[x['control'] for x in CONTROL_FAMILIES if _applies(x,kind,'base')],'blockedControls':[],'blockedReason':reason,'requires':['roleGate','scopeGate','tokenGate','stateGate','zeroGate','doNotTouchGate','rollbackGate']})
    return rows[:25000]
def build_state_control_join(rows):
    out=[]
    for r in rows:
        for ctrl in r.get('allowedControls',[]) or []:
            meta=next((c for c in CONTROL_FAMILIES if c['control']==ctrl),{})
            out.append({'targetId':r['targetId'],'surface':r['surface'],'component':r['component'],'layer':r['layer'],'role':r['role'],'kind':r['kind'],'state':r['state'],'control':ctrl,'family':meta.get('family',''),'zeroMeans':meta.get('zeroMeans',''),'requiresRuntimeCheck':meta.get('requiresRuntimeCheck',False)})
    return out[:50000]
def append_target_readiness(atlas_dir:Path, repo_root:Path, targets, surface_registry, route_component, component_owner, selector_rows, token_rows, file_index, config_doc=None, layer_rows=None, zero_rows=None):
    targets_rows=build_preset_target_matrix(surface_registry,component_owner,selector_rows,layer_rows or [],token_rows); controls=CONTROL_FAMILIES; join=build_state_control_join(targets_rows)
    _write_json(atlas_dir/'29_PRESET_TARGET_ELIGIBILITY_MATRIX.json',targets_rows); _write_csv(atlas_dir/'29_PRESET_TARGET_ELIGIBILITY_MATRIX.csv',targets_rows)
    _write_json(atlas_dir/'30_CONTROL_APPLICABILITY_MATRIX_PLUS.json',controls); _write_csv(atlas_dir/'30_CONTROL_APPLICABILITY_MATRIX_PLUS.csv',controls)
    _write_json(atlas_dir/'31_TARGET_STATE_CONTROL_JOIN.json',join); _write_csv(atlas_dir/'31_TARGET_STATE_CONTROL_JOIN.csv',join)
    runtime_required=[r for r in targets_rows if 'runtimeProbeGate' in (r.get('requires') or [])]
    summary={'status':'PASS_APP_MAP_TARGET_READINESS_GENERATED','presetTargetRows':len(targets_rows),'eligibleTargetRows':len([r for r in targets_rows if r.get('eligible')]),'blockedOrFallbackTargetRows':len([r for r in targets_rows if not r.get('eligible')]),'controlCount':len(controls),'stateControlRows':len(join),'runtimeProbeDeferred':True,'mamastrophicIntegrated':False,'mamastrophicDeferredReason':'User explicitly deferred Mamastrophic/Playwright to next phase.','importantRule':'Eligibility is target/role/state-level, not surface-level.'}
    _write_json(atlas_dir/'32_PRESET_TARGET_SUMMARY.json',summary)
    (atlas_dir/'33_RUNTIME_PROBE_DEFERRED_MAMASTROPHIC.md').write_text('# Mamastrophic runtime probe deferred\n\nThis upgrade intentionally does not integrate or run Playwright/Mamastrophic. Static App Map now emits target-level preset eligibility and control applicability plus. Runtime probing remains next phase.\n\n- Runtime-probe candidate targets: '+str(len(runtime_required))+'\n- No browser, server, DB, or process was touched by this map generation.\n',encoding='utf-8')
    return summary
