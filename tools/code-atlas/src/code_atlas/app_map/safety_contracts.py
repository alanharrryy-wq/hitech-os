# -*- coding: utf-8 -*-
from __future__ import annotations
import csv, json, re
from pathlib import Path
from typing import Any

STACKING_PROPS={"position","z-index","transform","filter","backdrop-filter","opacity","isolation","contain","will-change","perspective","mix-blend-mode"}
CLIPPING_PROPS={"overflow","overflow-x","overflow-y","clip-path","mask","mask-image"}
LAYOUT_PROPS={"display","grid","grid-template-columns","grid-template-rows","flex","flex-direction","align-items","justify-content","place-items","position"}
SPACING_PROPS={"padding","padding-left","padding-right","padding-top","padding-bottom","margin","gap","row-gap","column-gap"}
GLASS_HINTS=("glass","blur","frost","liquid","shine","specular","refraction","glow","aura")
LAYOUT_HINTS=("layout","grid","flex","row","column","cols","container","stack","rail","dock")
SPACING_HINTS=("space","spacing","gap","pad","padding","margin","spacer","gutter")
GROUP_HINTS=("wrap","wrapper","group","inner","outer","shell","box")
POS_HINTS=("/pos","checkout","cart","charge","payment","tender")
DO_NOT_TOUCH_PATTERNS=[
 ("POS_REAL",["/pos","checkout","cart","charge","payment","tender"],"operational sales surface"),
 ("PC",["products/pc","/pc/","backoffice"],"pc backoffice surface"),
 ("MOBILE",["products/mobile","/mobile/"],"mobile surface"),
 ("SHARED_CRITICAL",["/shared/","shared/","src/shared"],"shared code can affect multiple apps"),
 ("DB",["/prisma/","schema.prisma",".db",".sqlite","migrations/"],"database/schema/migration"),
 ("WORKER_API",["worker.js","/api/","route.ts"],"runtime api/worker"),
 ("PACKAGES_LOCKFILES",["package.json","pnpm-lock.yaml","package-lock.json","yarn.lock"],"package or lockfile"),
 ("GOVERNANCE",["governance/",".governance","docs/ops/","PRISMA_FIELD_MANUAL"],"governance/manual"),
]

def _read(path: Path)->str:
    try: return path.read_text(encoding='utf-8')
    except UnicodeDecodeError: return path.read_text(encoding='utf-8', errors='replace')
    except Exception: return ''

def _rel(repo: Path, path: Path)->str:
    try: return path.resolve().relative_to(repo.resolve()).as_posix()
    except Exception: return str(path).replace('\\','/')

def _write_json(path: Path, data: Any)->None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def _write_csv(path: Path, rows: list[dict[str, Any]])->None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with path.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=keys or ['empty']); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,'') for k in keys})

def _classes(attrs: str)->list[str]:
    out=[]
    for m in re.finditer(r"className\s*=\s*['\"]([^'\"]+)['\"]", attrs): out += [x for x in re.split(r"\s+", m.group(1).strip()) if x]
    for m in re.finditer(r"styles\.([A-Za-z0-9_]+)", attrs): out.append(m.group(1))
    return sorted(set(out))

def _css_index(repo: Path, targets: list[tuple[str, Path]])->dict[str,list[dict[str,Any]]]:
    idx={}
    for surface, root in targets:
        if not root.exists(): continue
        for css in root.rglob('*'):
            if not css.is_file() or css.suffix.lower() not in {'.css','.scss','.sass','.less'}: continue
            text=_read(css); rel=_rel(repo, css)
            for m in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_-]*)[^{}]{0,140}\{([^{}]*)\}", text, re.S):
                cls=m.group(1); body=m.group(2); props=sorted(set(re.findall(r"([a-zA-Z-]+)\s*:", body)))
                idx.setdefault(cls,[]).append({'surface':surface,'file':rel,'props':props,'body':body[:700]})
    return idx

def _purpose(attrs: str, classes: list[str], hits: list[dict[str,Any]], rel_file: str):
    blob=' '.join([attrs,' '.join(classes),' '.join(h.get('body','') for h in hits)]).lower()
    props={p for h in hits for p in h.get('props',[])}
    purpose=[]; evidence=[]
    if re.search(r"\bon[A-Z][A-Za-z]+\s*=", attrs): purpose.append('event-handler'); evidence.append('JSX on* handler')
    if 'ref=' in attrs: purpose.append('ref-measurement'); evidence.append('JSX ref')
    if 'aria-' in attrs or 'role=' in attrs or 'tabIndex' in attrs or 'tabindex' in attrs: purpose.append('focus-aria'); evidence.append('ARIA/focus attrs')
    if any(h in blob for h in GLASS_HINTS) or bool(props & {'backdrop-filter','filter'}): purpose.append('glass-blur-optical'); evidence.append('glass/blur/filter hint')
    if bool(props & STACKING_PROPS) or any(x in blob for x in ['z-index','overlay','absolute','fixed','sticky','stacking','isolation']): purpose.append('z-index-stacking'); evidence.append('stacking/position hint')
    if bool(props & CLIPPING_PROPS) or any(x in blob for x in ['overflow','clip','mask']): purpose.append('overflow-clipping'); evidence.append('overflow/clipping hint')
    if bool(props & LAYOUT_PROPS) or any(x in blob for x in LAYOUT_HINTS): purpose.append('layout'); evidence.append('layout hint')
    if bool(props & SPACING_PROPS) or any(x in blob for x in SPACING_HINTS): purpose.append('spacing-only'); evidence.append('spacing hint')
    if not purpose and (not attrs.strip() or any(x in blob for x in GROUP_HINTS)): purpose.append('grouping-only'); evidence.append('grouping/no structural attrs')
    if not purpose: purpose.append('probable-junk-or-unclassified'); evidence.append('no recognized purpose')
    if any(h in rel_file.lower() for h in POS_HINTS): purpose.append('protected-operational-pos-context'); evidence.append('protected POS path')
    return sorted(set(purpose)), evidence

def _risk_action(purposes:list[str]):
    p=set(purposes)
    if 'protected-operational-pos-context' in p: return 'blocked','BLOCKED_SHARED_SURFACE',False
    if 'focus-aria' in p: return 'high','KEEP_ACCESSIBILITY',False
    if 'event-handler' in p or 'ref-measurement' in p: return 'high','KEEP_REQUIRED',False
    if 'glass-blur-optical' in p: return 'high','KEEP_OPTICAL_GLASS',False
    if 'z-index-stacking' in p or 'overflow-clipping' in p: return 'high','KEEP_LAYOUT_ANCHOR',False
    if 'layout' in p: return 'medium','NEEDS_RUNTIME_PROBE',False
    if 'spacing-only' in p: return 'low','MERGE_WITH_PARENT',True
    if 'grouping-only' in p: return 'low','REPLACE_WITH_FRAGMENT',True
    return 'medium','NEEDS_RUNTIME_PROBE',False

def build_container_purpose_map(repo: Path, targets: list[tuple[str,Path]]):
    css_idx=_css_index(repo, targets); purpose_rows=[]; collapse_rows=[]
    tag_re=re.compile(r"<(?P<tag>div|section|article|main|aside|header|footer|nav|span)\b(?P<attrs>[^>]*)>", re.S)
    for surface, root in targets:
        if not root.exists(): continue
        for src in root.rglob('*'):
            if not src.is_file() or src.suffix.lower() not in {'.tsx','.jsx'}: continue
            rel_file=_rel(repo,src); text=_read(src)
            for i,m in enumerate(tag_re.finditer(text), start=1):
                attrs=m.group('attrs')[:900]; cls=_classes(attrs); hits=[h for c in cls for h in css_idx.get(c,[])]
                purposes,evidence=_purpose(attrs,cls,hits,rel_file); risk,action,can_remove=_risk_action(purposes)
                node=f"{rel_file}::{m.group('tag')}[{i}]"+(f".{'.'.join(cls[:3])}" if cls else '')
                row={'surface':surface,'node':node,'file':rel_file,'tag':m.group('tag'),'classes':'|'.join(cls),'purpose':purposes,'risk':risk,'safeAction':'merge-padding-to-parent' if action=='MERGE_WITH_PARENT' else action,'collapseClassification':action,'canRemove':can_remove,'evidence':evidence}
                purpose_rows.append(row)
                collapse_rows.append({'surface':surface,'node':node,'file':rel_file,'classification':action,'risk':risk,'canRemove':can_remove,'requires':'runtime visual diff' if risk=='medium' else ('explicit authorization' if risk=='blocked' else 'source review'),'notes':'; '.join(evidence[:4])})
    return purpose_rows, collapse_rows

def build_visual_diff_probe(collapse_rows):
    medium=[r for r in collapse_rows if r.get('risk')=='medium']
    candidate_limit=250
    candidates=medium[:candidate_limit]
    return {
        'status':'PLAN_ONLY_READ_ONLY',
        'reason':'Only medium-risk wrappers get before/after runtime probes.',
        'probeEngine':'Playwright toHaveScreenshot plus DOM depth, bounding boxes, computed styles, hover/focus/selected snapshots',
        'doesNotRunByDefault':True,
        'candidateCount':len(candidates),
        'candidateLimit':candidate_limit,
        'totalMediumRisk':len(medium),
        'candidates':candidates,
        'requiredCaptures':['domDepth','boundingBoxes','computedStyles','screenshotsBeforeAfter','hover','focus','selected','visualDiff']
    }

def build_zero_means_zero_gate(repo: Path, targets: list[tuple[str,Path]], token_rows:list[dict[str,Any]]):
    rows=[]; token_names={str(t.get('token','')) for t in token_rows}
    for token in sorted(t for t in token_names if t and any(x in t.lower() for x in ['blur','glow','border','alpha','shadow'])):
        low=token.lower(); expected='no residual visual effect when zero'
        if 'blur' in low: expected='backdrop-filter:none or filter:none when zero'
        elif 'glow' in low or 'shadow' in low: expected='box-shadow:none when zero'
        elif 'border' in low: expected='border-width:0 or border-color:transparent when zero'
        elif 'alpha' in low: expected='transparent background/no veil when zero'
        rows.append({'token':token,'expectedZeroBehavior':expected,'status':'STATIC_POLICY_RECORDED','runtimeRequiredForFinalCert':True})
    for surface, root in targets:
        if not root.exists(): continue
        for css in root.rglob('*'):
            if not css.is_file() or css.suffix.lower() not in {'.css','.scss','.sass','.less'}: continue
            text=_read(css).lower(); rel=_rel(repo,css)
            for prop, expected in [('backdrop-filter','none when blur token equals zero'),('box-shadow','none when glow/shadow token equals zero'),('border','0/transparent when border token equals zero'),('background','transparent when alpha token equals zero')]:
                if prop in text: rows.append({'surface':surface,'file':rel,'property':prop,'expectedZeroBehavior':expected,'status':'NEEDS_TOKEN_OR_RUNTIME_CONFIRMATION'})
    return rows[:5000]

def build_legacy_bridge(token_rows):
    tokens={str(r.get('token','')) for r in token_rows}; out=[]
    for token in sorted(t for t in tokens if 'tabctl3' in t):
        canonical=token.replace('tabctl3','tabctl7')
        out.append({'legacyToken':token,'canonicalToken':canonical,'canonicalPresent':canonical in tokens,'bridgeAction':'KEEP_ALIAS_AND_MAP_TO_CANONICAL' if canonical in tokens else 'CREATE_SAFE_ALIAS_BEFORE_RENAME','migrationPolicy':'bridge-first-clean-later-no-bulk-rename'})
    return out

def build_do_not_touch_map(repo, targets, file_index, route_component):
    rows=[]; seen=set(); candidates=[]
    for f in file_index: candidates.append((str(f.get('surface','')),str(f.get('file','')),'file'))
    for r in route_component: candidates.append((str(r.get('surface','')),str(r.get('file','')),'route'))
    for hp in ['package.json','pnpm-lock.yaml','apps/terminal-de-venta-system/prisma/schema.prisma','.governance/current/AUTHORITY_READSET.lock.json']:
        candidates.append(('repo',hp,'hard-blocker'))
    for surface,file,kind in candidates:
        low=file.lower().replace('\\','/')
        for zone,needles,reason in DO_NOT_TOUCH_PATTERNS:
            if any(n.lower() in low for n in needles):
                key=(surface,file,zone)
                if key in seen: continue
                seen.add(key); rows.append({'surface':surface,'file':file,'kind':kind,'zone':zone,'blocked':True,'reason':reason,'policy':'BLOCKED_FOR_CLEANUP_OR_PRESET_PROMOTION'})
    return rows[:5000]

def append_safety_contracts(atlas_dir: Path, repo_root: Path, targets: list[tuple[str,Path]], surface_registry, route_component, component_owner, selector_rows, token_rows, file_index):
    purpose_rows, collapse_rows=build_container_purpose_map(repo_root, targets)
    visual_probe=build_visual_diff_probe(collapse_rows)
    zero_rows=build_zero_means_zero_gate(repo_root, targets, token_rows)
    legacy_rows=build_legacy_bridge(token_rows)
    dnt_rows=build_do_not_touch_map(repo_root, targets, file_index, route_component)
    _write_json(atlas_dir/'21_CONTAINER_PURPOSE_MAP.json', purpose_rows); _write_csv(atlas_dir/'21_CONTAINER_PURPOSE_MAP.csv', purpose_rows)
    _write_json(atlas_dir/'22_WRAPPER_COLLAPSE_PLAN.json', collapse_rows); _write_csv(atlas_dir/'22_WRAPPER_COLLAPSE_PLAN.csv', collapse_rows)
    _write_json(atlas_dir/'23_VISUAL_DIFF_PROBE.json', visual_probe)
    _write_json(atlas_dir/'24_ZERO_MEANS_ZERO_REAL_GATE.json', zero_rows)
    _write_json(atlas_dir/'25_LEGACY_COMPAT_BRIDGE.json', legacy_rows)
    _write_json(atlas_dir/'26_DO_NOT_TOUCH_MAP.json', dnt_rows)
    blocked=[r for r in dnt_rows if r.get('blocked')]
    medium=[r for r in collapse_rows if r.get('risk')=='medium']
    removable=[r for r in collapse_rows if r.get('canRemove') is True and r.get('risk')=='low']
    visual_candidates=visual_probe.get('candidates', []) if isinstance(visual_probe, dict) else []
    visual_candidate_count=int(visual_probe.get('candidateCount', len(visual_candidates))) if isinstance(visual_probe, dict) else len(visual_candidates)
    visual_total_medium=int(visual_probe.get('totalMediumRisk', len(medium))) if isinstance(visual_probe, dict) else len(medium)
    visual_candidate_limit=int(visual_probe.get('candidateLimit', visual_candidate_count)) if isinstance(visual_probe, dict) else visual_candidate_count
    summary={
        'status':'PASS_APP_MAP_VISUAL_SAFETY_CONTRACTS_GENERATED',
        'containerPurposeRows':len(purpose_rows),
        'wrapperCollapseRows':len(collapse_rows),
        'visualDiffProbeCandidates':visual_candidate_count,
        'visualDiffProbeTotalMediumRisk':visual_total_medium,
        'visualDiffProbeCandidateLimit':visual_candidate_limit,
        'zeroMeansZeroRows':len(zero_rows),
        'legacyCompatRows':len(legacy_rows),
        'doNotTouchRows':len(dnt_rows),
        'lowRiskRemovableWrappers':len(removable),
        'blockedZones':len(blocked)
    }
    _write_json(atlas_dir/'27_VISUAL_SAFETY_SUMMARY.json', summary)
    (atlas_dir/'28_VISUAL_SAFETY_CONTRACT.md').write_text('# App Map Visual Safety Contract\n\nThis atlas is read-only. It may classify wrappers as removable candidates, but it does not remove them.\n\nHard rules:\n\n- Read broad, register strictly.\n- POS, checkout/cart, PC, Mobile, shared critical, DB, Worker/API, package/lockfiles, Prisma and governance are blocked for cleanup/preset promotion unless separately authorized.\n- Wrappers with z-index/stacking, containing-block, overflow/clipping, glass/blur, focus/aria, event handlers or refs are not safe removals.\n- Medium-risk wrappers require runtime visual diff before cleanup.\n- Zero means zero: blur/glow/border/alpha/shadow must produce no residual visual effect.\n- Legacy tabctl3 tokens must bridge to tabctl7 before any rename or cleanup.\n', encoding='utf-8')
    return summary
