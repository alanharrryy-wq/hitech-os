# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import html
import json
import os
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any, Callable

try:
    from .strict_classifier import (
        SCAN_EXTENSIONS, STYLE_EXTENSIONS, COMPONENT_EXTENSIONS,
        classify_file, derive_route, extract_selectors, extract_tokens,
        is_route_file, is_valid_selector,
    )
except Exception:  # pragma: no cover
    from strict_classifier import (  # type: ignore
        SCAN_EXTENSIONS, STYLE_EXTENSIONS, COMPONENT_EXTENSIONS,
        classify_file, derive_route, extract_selectors, extract_tokens,
        is_route_file, is_valid_selector,
    )

EXCLUDE_PARTS = {'.git','node_modules','.next','dist','build','coverage','__pycache__','.prisma_backups','.prisma_installer_backups','tools/_local'}
TARGET_ROOTS = {
    'tablet': ['apps/terminal-de-venta-system/products/tablet', 'products/tablet'],
    'pc': ['apps/terminal-de-venta-system/products/pc', 'products/pc'],
    'mobile': ['apps/terminal-de-venta-system/products/mobile', 'products/mobile'],
    'web': ['apps/terminal-de-venta-system/products/web', 'apps/terminal-de-venta-system/products/prisma-web', 'products/web'],
    'cloud-center': ['apps/terminal-de-venta-system/Prisma Cloud Ctr', 'Prisma Cloud Ctr'],
    'control-center': ['apps/terminal-de-venta-system/Control Center', 'products/control-center'],
    'chart-lab': ['apps/terminal-de-venta-system/products/chart-lab', 'products/chart-lab'],
}
APP_LABELS = {
    'tablet': 'Tablet', 'pc': 'PC', 'mobile': 'Mobile', 'web': 'Web / EIT',
    'cloud-center': 'Cloud Center', 'control-center': 'Control Center', 'chart-lab': 'Chart Lab', 'all': 'Todas'
}


def _stamp() -> str:
    return _dt.datetime.now().strftime('%d%m %H%M')


def _safe_rel(root: Path, p: Path) -> str:
    try:
        return str(p.resolve().relative_to(root.resolve())).replace('\\','/')
    except Exception:
        return str(p).replace('\\','/')


def _excluded(p: Path) -> bool:
    return any(part in EXCLUDE_PARTS for part in p.parts)


def _find_repo_root(selected: Path) -> Path:
    cur = selected if selected.is_dir() else selected.parent
    for p in [cur, *cur.parents]:
        if (p / 'apps' / 'terminal-de-venta-system').exists() or (p / 'tools' / 'code-atlas').exists() or (p / '.git').exists():
            return p
    return cur


def _resolve_targets(repo: Path, target_app: str) -> list[tuple[str, Path]]:
    apps = [target_app] if target_app and target_app != 'all' else list(TARGET_ROOTS.keys())
    out: list[tuple[str, Path]] = []
    for app in apps:
        for raw in TARGET_ROOTS.get(app, []):
            p = repo / raw
            if p.exists():
                out.append((app, p))
                break
    return out


def _iter_files(root: Path):
    if not root.exists():
        return
    for p in root.rglob('*'):
        if p.is_file() and not _excluded(p) and p.suffix.lower() in SCAN_EXTENSIONS:
            yield p


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return p.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''


def _extract_routes(app_root: Path, files: list[Path]) -> list[dict[str, Any]]:
    rows=[]
    for p in files:
        if not is_route_file(p, app_root):
            continue
        rel = _safe_rel(app_root, p)
        stem = p.stem
        rows.append({
            'route': derive_route(app_root, p),
            'file': rel,
            'kind': 'api_route' if stem == 'route' else ('route_layout' if stem == 'layout' else 'route_' + stem),
            'fileKind': 'route',
        })
    return rows[:2000]


def _extract_class_usage(text: str) -> set[str]:
    found=set()
    for m in re.finditer(r'className\s*=\s*["\']([^"\']+)["\']', text):
        for c in re.split(r'\s+', m.group(1).strip()):
            if c:
                found.add(c)
    for m in re.finditer(r'styles\.([A-Za-z0-9_]+)', text):
        found.add(m.group(1))
    return found


def _token_type(name: str) -> str:
    low=name.lower()
    if any(x in low for x in ['color','bg','fill','stroke','ink','cyan','alpha']): return 'color'
    if any(x in low for x in ['space','gap','pad','margin','inset']): return 'spacing'
    if any(x in low for x in ['radius','round']): return 'radius'
    if any(x in low for x in ['shadow','glow','blur','filter']): return 'effect'
    if any(x in low for x in ['font','text','letter','line']): return 'typography'
    return 'unknown'


def _write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _write_csv(path: Path, rows: list[dict[str, Any]]):
    keys=[]
    for r in rows:
        for k in r.keys():
            if k not in keys:
                keys.append(k)
    with path.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=keys or ['empty'])
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,'') for k in keys})


def run_app_map(selected_path: str, target_app: str='all', output_root: str|None=None, notify: Callable[[str,str],None]|None=None) -> str:
    selected=Path(selected_path).expanduser().resolve()
    repo=_find_repo_root(selected)
    output=Path(output_root or os.environ.get('CODE_ATLAS_OUTPUT_ROOT', r'F:\descargasf'))
    output.mkdir(parents=True, exist_ok=True)
    stamp=_stamp()
    work=output / f'_appmap_work_{_dt.datetime.now().strftime("%Y%m%d_%H%M%S")}_{os.getpid()}'
    atlas=work / 'app_map_atlas'
    atlas.mkdir(parents=True, exist_ok=True)
    final_zip=output / f'appmap {stamp} result.zip'
    targets=_resolve_targets(repo, target_app or 'all')
    if notify:
        notify('App Map strict targets', ', '.join([a for a,_ in targets]) or 'none')

    surface_registry=[]; route_component=[]; component_owner=[]; selector_rows=[]; selector_usage=[]; token_rows=[]; pos_rows=[]; zero_rows=[]; layer_rows=[]; file_index=[]; config_doc=[]; quarantine=[]
    for app, root in targets:
        files=list(_iter_files(root))
        for p in files:
            rel = _safe_rel(root, p)
            kind = classify_file(p, root)
            file_index.append({'surface': app, 'file': rel, 'fileKind': kind, 'suffix': p.suffix.lower()})
            if kind in {'config', 'doc'}:
                config_doc.append({'surface': app, 'file': rel, 'fileKind': kind})
        css_files=[p for p in files if classify_file(p, root) == 'style']
        comp_files=[p for p in files if classify_file(p, root) in {'component','component_candidate'}]
        routes=_extract_routes(root, files)
        surface_registry.append({
            'surfaceId': app, 'label': APP_LABELS.get(app, app), 'root': _safe_rel(repo, root),
            'exists': root.exists(), 'fileCount': len(files), 'routeCount': len(routes),
            'isRuntime': app in {'tablet','pc','mobile','web'}, 'isProtected': app in {'tablet','pc','cloud-center'},
            'canReceivePreset': app not in {'cloud-center','control-center'},
            'riskLevel': 'critical' if app in {'tablet','pc','cloud-center'} else 'medium'
        })
        for r in routes:
            route_component.append({'surface': app, **r})
            if '/pos' in r.get('route','').lower():
                pos_rows.append({'surface':app,'route':r['route'],'file':r['file'],'protected':True,'reason':'operational-pos-route'})
        css_by_stem={p.stem.replace('.module',''): p for p in css_files}
        for p in comp_files:
            text=_read(p); rr=_safe_rel(root,p); stem=p.stem
            style_guess=''
            for s, sp in css_by_stem.items():
                if s.lower() in stem.lower() or stem.lower() in s.lower():
                    style_guess=_safe_rel(root,sp); break
            classes=sorted(_extract_class_usage(text))
            component_owner.append({'surface':app,'componentFile':rr,'componentId':stem,'styleOwner':style_guess,'classUsageCount':len(classes),'risk':'protected-pos' if '/pos' in rr.lower() else 'normal','fileKind':classify_file(p, root)})
            for c in classes:
                selector_usage.append({'surface':app,'classOrToken':c,'usedIn':rr,'usageKind':'className_or_cssModule'})
        for p in css_files:
            text=_read(p); rr=_safe_rel(root,p)
            selectors, rejected = extract_selectors(text)
            for item in rejected:
                quarantine.append({'surface': app, 'file': rr, **item})
            important_count = text.count('!important')
            for s in selectors:
                if not is_valid_selector(s):
                    quarantine.append({'surface': app, 'file': rr, 'candidate': s, 'reason': 'validator_reject_after_extract'})
                    continue
                states=[]
                for state in [':hover',':focus',':focus-visible',':disabled',':active','[aria-selected','[data-state']:
                    if state in s: states.append(state)
                selector_rows.append({'surface':app,'selector':s,'definedIn':rr,'states':'|'.join(states),'isGlobal':':global' in s,'isShared':False,'importantCount':important_count,'classification':'KEEP_CANONICAL' if not s.startswith('*') else 'NEEDS_HUMAN_REVIEW','fileKind':'style'})
                kind='panel'
                if 'button' in s.lower() or 'btn' in s.lower(): kind='button'
                elif 'text' in s.lower() or 'label' in s.lower(): kind='text'
                layer_rows.append({'surface':app,'component':'(css selector)','layer':s,'role':s,'kind':kind,'stateCount':len(states),'presetEligible': app not in {'cloud-center','control-center'}})
            seen=set()
            for t in extract_tokens(text):
                name=t['token']
                if (name, rr, t.get('kind')) in seen: continue
                seen.add((name,rr,t.get('kind')))
                typ=_token_type(name)
                token_rows.append({'surface':app,'token':name,'tokenType':typ,'definedOrUsedIn':rr,'tokenKind':t.get('kind','unknown'),'defaultValue':t.get('defaultValue',''),'canBePreset':typ in {'color','spacing','radius','effect','typography'},'legacyAlias':'tabctl3' in name,'zeroBehavior':'none' if typ=='effect' else 'default','fileKind':'style'})
                if any(x in name.lower() for x in ['blur','glow','shadow','alpha','border']):
                    zero_rows.append({'surface':app,'token':name,'file':rr,'zeroMeans':'none/transparent/0 as applicable','status':'CHECK_STATIC_TOKEN'})
    _write_json(atlas/'01_SURFACE_REGISTRY.json', surface_registry)
    _write_json(atlas/'02_ROUTE_COMPONENT_MAP.json', route_component)
    _write_json(atlas/'03_COMPONENT_OWNERSHIP_MAP.json', component_owner)
    _write_json(atlas/'04_LAYER_ROLE_KIND_MAP.json', layer_rows)
    _write_json(atlas/'05_SELECTOR_GRAPH.json', selector_rows)
    _write_csv(atlas/'06_SELECTOR_USAGE.csv', selector_usage)
    _write_json(atlas/'07_TOKEN_GRAPH.json', token_rows)
    _write_json(atlas/'08_LEGACY_TOKEN_ALIAS_MAP.json', [r for r in token_rows if r.get('legacyAlias')])
    _write_json(atlas/'09_STATE_MATRIX.json', {
        'button': {'requiredStates':['base','hover','focus-visible','pressed','disabled'], 'optionalStates':['selected','loading','success','error']},
        'text': {'requiredStates':['base','muted','selected','warning','error','disabled']},
        'panel': {'requiredStates':['base','hover','selected','dragging','empty','locked']},
    })
    _write_json(atlas/'10_CONTROL_APPLICABILITY_MATRIX.json', [
        {'control':'backdropBlur','appliesTo':['panel','modal','background'],'blockedFor':['text','numericText','buttonText','icon'],'zeroMeans':'backdrop-filter:none'},
        {'control':'glow','appliesTo':['button','panel','card'],'blockedFor':['text'],'zeroMeans':'box-shadow:none'},
        {'control':'radius','appliesTo':['button','panel','card','input'],'blockedFor':['plainText'],'zeroMeans':'border-radius:0'},
    ])
    _write_json(atlas/'11_PRESET_ELIGIBILITY_REGISTRY.json', [
        {'surface':s['surfaceId'],'eligible':s['canReceivePreset'],'riskLevel':s['riskLevel'],'blockedScopes':['global','pos-real'] if s['surfaceId']=='tablet' else ['global']} for s in surface_registry
    ])
    _write_json(atlas/'12_POS_PROTECTION_MAP.json', pos_rows)
    _write_json(atlas/'13_ZERO_MEANS_ZERO_AUDIT.json', zero_rows)
    (atlas/'14_IMPORTANT_AUDIT_FILTERED.md').write_text('# Important audit filtered\n\n' + '\n'.join(f"- {r['surface']} {r['definedIn']} important={r['importantCount']}" for r in selector_rows if r.get('importantCount')), encoding='utf-8')
    (atlas/'15_ORPHAN_DUPLICATE_SHARED_SELECTORS.md').write_text('# Selector audit\n\nStatic selector graph generated. Use runtime probe for definitive orphan confirmation. Declaration leaks are quarantined, not registered as selectors.\n', encoding='utf-8')
    (atlas/'16_PRESET_PROMOTION_CONTRACT.md').write_text('# Preset promotion contract\n\nRead-only map only. No preset can be promoted without explicit scope, token, state, contrast, zero, rollback and protected-surface gates. Route/config/doc/style classes are strictly separated.\n', encoding='utf-8')
    (atlas/'17_CONTINUATION.md').write_text('Next: inspect App Map outputs, then decide if runtime probe is needed. No app code was modified by this run. Strict classifier prevents CSS/JSON/docs/tokens from leaking into route or selector maps.\n', encoding='utf-8')
    _write_json(atlas/'18_FILE_CLASSIFICATION_INDEX.json', file_index)
    _write_json(atlas/'19_CONFIG_DOC_INDEX.json', config_doc)
    _write_json(atlas/'20_CLASSIFICATION_QUARANTINE.json', quarantine[:5000])
    # CODE_ATLAS_APP_MAP_SAFETY_CONTRACTS_V01
    try:
        from .safety_contracts import append_safety_contracts
    except Exception:  # pragma: no cover
        from safety_contracts import append_safety_contracts  # type: ignore
    safety_summary = append_safety_contracts(
        atlas_dir=atlas,
        repo_root=repo,
        targets=targets,
        surface_registry=surface_registry,
        route_component=route_component,
        component_owner=component_owner,
        selector_rows=selector_rows,
        token_rows=token_rows,
        file_index=file_index,
    )
    # /CODE_ATLAS_APP_MAP_SAFETY_CONTRACTS_V01
    # CODE_ATLAS_APP_MAP_TARGET_READINESS_V01
    try:
        from .target_readiness import append_target_readiness
    except Exception:  # pragma: no cover
        from target_readiness import append_target_readiness  # type: ignore
    target_summary = append_target_readiness(
        atlas_dir=atlas,
        repo_root=repo,
        targets=targets,
        surface_registry=surface_registry,
        route_component=route_component,
        component_owner=component_owner,
        selector_rows=selector_rows,
        token_rows=token_rows,
        file_index=file_index,
        config_doc=config_doc,
        layer_rows=layer_rows,
        zero_rows=zero_rows,
    )
    # /CODE_ATLAS_APP_MAP_TARGET_READINESS_V01
    summary={'ok': True, 'status':'PASS_APP_MAP_READONLY_GENERATED_STRICT_CLASSIFICATION_VISUAL_SAFETY', 'targetApp':target_app or 'all', 'repoRoot':str(repo), 'surfaceCount':len(surface_registry), 'routes':len(route_component), 'components':len(component_owner), 'selectors':len(selector_rows), 'tokens':len(token_rows), 'configsAndDocs':len(config_doc), 'quarantinedCandidates':len(quarantine), 'visualSafety': safety_summary, 'targetReadiness': target_summary}
    _write_json(atlas/'APP_MAP_SUMMARY.json', summary)
    html_body=''.join(f"<li><b>{html.escape(s['label'])}</b>: files {s['fileCount']}, routes {s['routeCount']}, risk {s['riskLevel']}</li>" for s in surface_registry)
    (atlas/'app_map_viewer.html').write_text(f"<!doctype html><meta charset='utf-8'><title>App Map</title><body style='font-family:system-ui;background:#111827;color:#e5f6ff;padding:24px'><h1>App Map</h1><p>Read-only app map with strict classification guard.</p><ul>{html_body}</ul><pre>{html.escape(json.dumps(summary, indent=2))}</pre></body>", encoding='utf-8')
    with zipfile.ZipFile(final_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in atlas.rglob('*'):
            if p.is_file(): z.write(p, p.relative_to(atlas.parent))
    try: shutil.rmtree(work)
    except Exception: pass
    return str(final_zip)
