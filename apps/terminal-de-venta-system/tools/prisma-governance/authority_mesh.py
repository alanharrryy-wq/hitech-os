#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRISMA Authority Mesh
GovMesh3 all-phases Visual Exploitation Contract preflight. Read-mostly that resolves live governance authority for all PRISMA apps/surfaces.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

EXCLUDE_DIRS_DEFAULT = {'.git','node_modules','.next','dist','build','coverage','.prisma_installer_backups','__pycache__'}
TEXT_EXTS = {'.md','.json','.jsonc','.txt','.yaml','.yml','.mjs','.js','.ts','.tsx','.py','.ps1','.cmd','.prisma','.sql','.css'}


def norm(p: Path) -> str:
    return p.as_posix().replace('\\','/')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Dict[str, Any]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def read_text_maybe(path: Path, limit: int = 120000) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')[:limit]
    except Exception:
        return ''


def discover_repo(start: Path) -> Path:
    cur = start.resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate/'package.json').exists() or (candidate/'pnpm-workspace.yaml').exists() or (candidate/'docs').exists():
            return candidate
    default = Path(r'F:\repos\hitech-os\apps\terminal-de-venta-system')
    if default.exists():
        return default
    return cur


def walk_files(repo: Path, excludes: Iterable[str]) -> List[Path]:
    excludes_set = set(excludes) | EXCLUDE_DIRS_DEFAULT
    out: List[Path] = []
    for root, dirs, files in os.walk(repo):
        rootp = Path(root)
        rel_parts = rootp.relative_to(repo).parts if rootp != repo else ()
        if any(part in excludes_set for part in rel_parts):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in excludes_set]
        for f in files:
            p = rootp/f
            out.append(p)
    return out


def match_glob(repo: Path, all_files: List[Path], pattern: str, max_items: int = 1000) -> List[Path]:
    # pathlib.glob handles ** but can be slow; use cached all_files and fnmatch.
    pat = pattern.replace('\\','/')
    res = []
    for p in all_files:
        rel = norm(p.relative_to(repo))
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch('/'+rel, pat):
            res.append(p)
            if len(res) >= max_items:
                break
    return sorted(res, key=lambda x: norm(x.relative_to(repo)))


def classify_task(task: str, rules: Dict[str, Any], full: bool) -> Tuple[List[str], List[str]]:
    text = task.lower()
    all_signal = full or any(w in text for w in ['todas','todos','all apps','all surfaces','global','todas las superficies','todas las apps','todo todo'])
    apps = []
    if all_signal:
        apps = list(rules.get('apps', {}).keys())
    else:
        for app, cfg in rules.get('apps', {}).items():
            kws = cfg.get('keywords', [])
            if any(k.lower() in text for k in kws):
                apps.append(app)
        if not apps:
            apps = ['quality']
    types = []
    for typ, cfg in rules.get('change_types', {}).items():
        if any(k.lower() in text for k in cfg.get('keywords', [])):
            types.append(typ)
    if all_signal and 'visual' not in types:
        # full preflight should include visual because visual governors span surfaces.
        types.append('visual')
    return sorted(set(apps)), sorted(set(types))


def authority_entry(repo: Path, path: Path) -> Dict[str, Any]:
    rel = norm(path.relative_to(repo))
    info = {
        'path': rel,
        'bytes': path.stat().st_size,
        'sha256': sha256_file(path),
        'extension': path.suffix.lower(),
    }
    return info


def add_matches(bucket: List[Dict[str, Any]], repo: Path, matches: List[Path], source_id: str, reason: str) -> None:
    seen = {b['path'] for b in bucket}
    for m in matches:
        entry = authority_entry(repo, m)
        if entry['path'] in seen:
            continue
        entry['source_id'] = source_id
        entry['reason'] = reason
        bucket.append(entry)
        seen.add(entry['path'])


def scan_text_patterns(repo: Path, all_files: List[Path], patterns: List[str], rules: Dict[str, Any]) -> Dict[str, Any]:
    max_items = int(rules.get('max_runtime_matches_per_pattern', 200))
    out: Dict[str, Any] = {}
    for pat in patterns:
        matches = []
        for p in match_glob(repo, all_files, pat, max_items=max_items+1):
            rel = norm(p.relative_to(repo))
            if len(matches) < max_items:
                matches.append({'path': rel, 'bytes': p.stat().st_size, 'sha256': sha256_file(p) if p.suffix.lower() in TEXT_EXTS and p.stat().st_size < 2_000_000 else None})
        out[pat] = {'matches': matches, 'truncated': len(matches) >= max_items}
    return out


def find_unmapped_and_excluded(repo: Path, all_files: List[Path]) -> Dict[str, Any]:
    candidates = []
    for p in all_files:
        rel = norm(p.relative_to(repo)).lower()
        name = p.name.lower()
        if name.startswith('unmapped_') or name.startswith('excluded_') or 'unmapped' in rel or 'excluded' in rel:
            if p.suffix.lower() in TEXT_EXTS and p.stat().st_size < 5_000_000:
                candidates.append(p)
    parsed = []
    for p in candidates[:50]:
        text = read_text_maybe(p, 200000)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip().startswith('- ')]
        parsed.append({'path': norm(p.relative_to(repo)), 'bytes': p.stat().st_size, 'sha256': sha256_file(p), 'sample_items': lines[:80], 'item_count_estimate': len(lines)})
    return {'candidate_files': parsed, 'candidate_count': len(candidates)}


# --- PRISMA GOVMESH2: native Visual Capability Resolver ----------------------

PACKAGE_CAPABILITY_ALIASES = {
    '@radix-ui/react-dialog': ('radix-dialog','radix','Accessible dialog/confirmation surfaces for checkout and guarded actions.','low'),
    '@radix-ui/react-dropdown-menu': ('radix-dropdown-menu','radix','Accessible command/menu surfaces for structured actions.','low'),
    '@radix-ui/react-scroll-area': ('radix-scroll-area','radix','Controlled scroll for product grids, carts and dense touch regions.','low'),
    '@radix-ui/react-select': ('radix-select','radix','Accessible selects for filters, variants and checkout options.','low'),
    '@radix-ui/react-tabs': ('radix-tabs','radix','Accessible tabbed segmentation for categories or payment modes.','low'),
    '@radix-ui/react-tooltip': ('radix-tooltip','radix','Non-blocking help for secondary controls when touch UX stays clear.','medium'),
    '@radix-ui/react-slot': ('radix-slot','radix','Composition primitive for PRISMA buttons/panels without DOM noise.','low'),
    '@vanilla-extract/css': ('vanilla-extract','styling','Static governed tokens/styles when repo pattern already exists.','medium'),
    'ogl': ('ogl','webgl','Bounded ambient/background WebGL only when layer budget allows.','high'),
    'framer-motion': ('framer-motion','motion','Bounded microinteractions: tap feedback, panel reveal, cart/payment transitions.','medium'),
    'motion': ('motion','motion','Bounded microinteractions if compatible with current import style.','medium'),
    'gsap': ('gsap','motion','Timeline animation only when already used safely and not overkill.','high'),
    'three': ('three','webgl','3D/WebGL for lab/background use, rarely for operational POS.','high'),
    'react-spring': ('react-spring','motion','Spring microinteractions if target surface already uses it.','medium'),
    '@react-spring/web': ('react-spring-web','motion','Spring microinteractions if target surface already uses it.','medium'),
    'lucide-react': ('lucide-react','icons','Lightweight governed icons for actions/status/navigation clarity.','low'),
    'class-variance-authority': ('class-variance-authority','variants','Typed class variants for governed component states.','low'),
    'clsx': ('clsx','class-composition','Safe local class composition.','low'),
    'tailwind-merge': ('tailwind-merge','class-composition','Conflict-aware utility class merge if Tailwind utilities are in use.','low')
}

PRISMA_VISUAL_CAPABILITY_GLOBS = [
    ('prisma-components','prisma-shared-ui',['products/shared-ui/prisma/components/Prisma*.tsx','products/shared-ui/prisma/components/*.tsx'],'Governed PRISMA surfaces, cards, panels, action buttons and product/cart/checkout components.','low','prefer'),
    ('prisma-visual-os','visual-os',['products/shared-ui/prisma/visual-os/**','config/prisma-visual-os/**'],'Governed controls, layers, presets, recipes and release gates.','low','prefer'),
    ('prisma-recipes','recipes',['config/prisma-visual/recipe-map.json','config/prisma-visual-system/**','config/prisma-visual/**recipes*.json','products/shared-ui/prisma/recipes/**'],'Approved visual recipes including liquid/glass/pill/cloudglass where authorized.','low','prefer'),
    ('prisma-tokens','tokens',['products/shared-ui/prisma/tokens/**','config/prisma-visual/**tokens*','**/*tokens*.css','**/*tokens*.ts'],'Governed spacing, color, radius, shadow, typography and state primitives.','low','prefer'),
    ('layer-budget','governance',['config/prisma-visual/layer-budget.json','docs/visual-layer-map/**'],'Limits visual depth/effects so premium layers do not crush performance or clarity.','low','mandatory'),
    ('authority-map','governance',['config/prisma-visual/authority-map.json','config/prisma-visual/surface-adapters.json'],'Connects recipes/components to allowed surfaces and authority constraints.','low','mandatory'),
    ('background-catalog','backgrounds',['products/0.backgrounds/**','products/*/app/public/visual-backgrounds/**','**/*background*.json'],'Governed atmospheric/background assets per surface.','medium','review'),
    ('cloudglass-assets','liquid-glass',['**/*cloudglass*','**/*glass*','**/*liquid*','**/*pill*','**/*capsule*'],'Liquid/Pill/Cloudglass references, assets, docs, runtime implementations and candidates.','medium','review')
]

APP_VISUAL_PROFILES = {
    'tablet': {
        'style':'light, tactile, high-contrast-soft, touch-first, operational clarity',
        'prefer':['prisma-components','prisma-visual-os','prisma-recipes','prisma-tokens','layer-budget','authority-map','background-catalog','radix-scroll-area','radix-dialog','radix-select','framer-motion','motion','lucide-react','clsx','class-variance-authority'],
        'cautious':['ogl','three','gsap','react-spring','cloudglass-assets','vanilla-extract'],
        'forbid':['dark/obsidian dominant Tablet theme','global CSS blast','background layer that blocks selling flow']
    },
    'pc': {
        'style':'desktop-grade, dense but readable, controlled glass/graphite only if PC governor allows',
        'prefer':['prisma-components','prisma-visual-os','prisma-recipes','prisma-tokens','layer-budget','authority-map','radix-tabs','radix-tooltip','radix-dialog','lucide-react','clsx'],
        'cautious':['ogl','three','gsap','cloudglass-assets','background-catalog','vanilla-extract'],
        'forbid':['Tablet-only visuals copied blindly','unbounded WebGL in operational surfaces']
    },
    'mobile': {
        'style':'thin, fast, truthful, compact, low-overhead touch',
        'prefer':['prisma-tokens','prisma-recipes','radix-slot','lucide-react','clsx'],
        'cautious':['framer-motion','motion','background-catalog','cloudglass-assets','vanilla-extract'],
        'forbid':['heavy WebGL','large atmospheric backgrounds','desktop/tablet density']
    },
    'chart-lab': {
        'style':'visual experimentation with evidence and lab boundaries',
        'prefer':['prisma-visual-os','prisma-recipes','background-catalog','framer-motion','motion','ogl','three','lucide-react'],
        'cautious':['gsap','cloudglass-assets'],
        'forbid':['promoting lab visuals to production without governor/evidence']
    },
    'web': {
        'style':'public/portal appropriate, lightweight, governed branding',
        'prefer':['prisma-tokens','prisma-recipes','background-catalog','lucide-react','clsx'],
        'cautious':['framer-motion','motion','ogl','three','gsap','cloudglass-assets'],
        'forbid':['POS operational assumptions in public surfaces']
    },
    'shared-ui': {
        'style':'cross-surface primitives and recipes with strict compatibility',
        'prefer':['prisma-components','prisma-visual-os','prisma-recipes','prisma-tokens','layer-budget','authority-map','radix-slot','class-variance-authority','clsx','tailwind-merge'],
        'cautious':['framer-motion','motion','vanilla-extract','cloudglass-assets'],
        'forbid':['breaking changes without tri-surface evidence']
    },
    'backgrounds': {
        'style':'governed atmosphere assets, manifests and per-surface adapters',
        'prefer':['background-catalog','cloudglass-assets','layer-budget','authority-map'],
        'cautious':['ogl','three','gsap'],
        'forbid':['using excluded/heavy assets without manifest']
    }
}


def read_package_names(repo: Path, all_files: List[Path]) -> Dict[str, Dict[str, Any]]:
    found: Dict[str, Dict[str, Any]] = {}
    package_files = [p for p in all_files if p.name == 'package.json' and p.stat().st_size < 2_000_000]
    for p in package_files[:100]:
        try:
            data = json.loads(read_text_maybe(p, 2_000_000))
        except Exception:
            continue
        rel = norm(p.relative_to(repo))
        for sec in ['dependencies','devDependencies','peerDependencies','optionalDependencies']:
            deps = data.get(sec, {}) or {}
            if isinstance(deps, dict):
                for name, version in deps.items():
                    found.setdefault(name, {'name': name, 'evidence': [], 'versions': []})
                    found[name]['evidence'].append({'path': rel, 'section': sec, 'version': str(version)})
                    if str(version) not in found[name]['versions']:
                        found[name]['versions'].append(str(version))
    lock_candidates = [p for p in all_files if p.name in ['pnpm-lock.yaml','package-lock.json','yarn.lock','bun.lockb','bun.lock'] and p.stat().st_size < 15_000_000]
    for lock in lock_candidates[:8]:
        text = read_text_maybe(lock, 2_000_000)
        rel = norm(lock.relative_to(repo))
        for name in PACKAGE_CAPABILITY_ALIASES:
            if name in text:
                found.setdefault(name, {'name': name, 'evidence': [], 'versions': []})
                found[name]['evidence'].append({'path': rel, 'section': 'lockfile', 'version': 'lock-evidence'})
                if 'lock-evidence' not in found[name]['versions']:
                    found[name]['versions'].append('lock-evidence')
    return found


def collect_visual_evidence(repo: Path, all_files: List[Path], patterns: List[str], max_items: int = 40) -> List[Dict[str, Any]]:
    evidence = []
    seen = set()
    for pat in patterns:
        for p in match_glob(repo, all_files, pat, max_items=max_items):
            rel = norm(p.relative_to(repo))
            if rel in seen:
                continue
            seen.add(rel)
            item = {'path': rel, 'bytes': p.stat().st_size, 'extension': p.suffix.lower()}
            if p.suffix.lower() in TEXT_EXTS and p.stat().st_size < 2_000_000:
                item['sha256'] = sha256_file(p)
            evidence.append(item)
            if len(evidence) >= max_items:
                return evidence
    return evidence


def find_candidate_target_files(repo: Path, all_files: List[Path], apps: List[str], task: str, max_items: int = 80) -> List[Dict[str, Any]]:
    text = task.lower()
    task_tokens = [tok for tok in ['pos','sell','venta','vender','cart','carrito','checkout','payment','cobrar','home','inicio','dashboard','chart','background','liquid','glass','pill','mobile','pc','tablet'] if tok in text]
    if not task_tokens:
        task_tokens = ['pos','checkout','cart','home','dashboard','visual']
    roots = []
    root_map = {
        'tablet':['products/tablet/app'],
        'pc':['products/pc/app'],
        'mobile':['products/mobile/app'],
        'chart-lab':['products/chart-lab/app'],
        'web':['products/web/app'],
        'shared-ui':['products/shared-ui/prisma'],
        'backgrounds':['products/0.backgrounds']
    }
    for app in apps:
        roots.extend(root_map.get(app, []))
    if not roots:
        roots = ['products']
    candidates = []
    for p in all_files:
        if p.suffix.lower() not in {'.tsx','.ts','.css','.md','.json'}:
            continue
        rel = norm(p.relative_to(repo))
        if not any(rel.startswith(r) for r in roots):
            continue
        low = rel.lower()
        score = sum(50 for tok in task_tokens if tok in low)
        if 'components' in low: score += 20
        if p.suffix.lower() in {'.tsx','.ts'}: score += 10
        if score:
            candidates.append({'path': rel, 'score': score, 'bytes': p.stat().st_size})
    return sorted(candidates, key=lambda x: (-x['score'], x['path']))[:max_items]


def build_visual_capability_data(repo: Path, all_files: List[Path], apps: List[str], types: List[str], task: str, rules: Dict[str, Any]) -> Dict[str, Any]:
    task_l = task.lower()
    visual_required = bool(set(types) & {'visual','liquid_glass'}) or any(w in task_l for w in ['premium','visual','ui','ux','glass','liquid','pill','cloudglass','background','interfaz','diseño'])
    packages = read_package_names(repo, all_files)
    capabilities: List[Dict[str, Any]] = []

    for pkg_name, meta in PACKAGE_CAPABILITY_ALIASES.items():
        cap_id, family, contribution, risk = meta
        available = pkg_name in packages
        rec = 'use_if_relevant' if risk in ['low','medium'] else 'review_only'
        if cap_id in ['ogl','three','gsap']:
            rec = 'bounded_optional_high_risk'
        capabilities.append({
            'id': cap_id,
            'kind': 'package',
            'package': pkg_name,
            'family': family,
            'available': available,
            'evidence': packages.get(pkg_name, {}).get('evidence', []),
            'versions': packages.get(pkg_name, {}).get('versions', []),
            'visual_contribution': contribution,
            'risk': risk,
            'default_decision': rec if available else 'not_available',
            'use_rule': 'Use only when it improves this app/surface and passes governance, performance and layer budget. If available but unused in a premium task, justify rejection.'
        })

    for cap_id, family, patterns, contribution, risk, rec in PRISMA_VISUAL_CAPABILITY_GLOBS:
        evidence = collect_visual_evidence(repo, all_files, patterns)
        capabilities.append({
            'id': cap_id,
            'kind': 'repo_capability',
            'family': family,
            'available': bool(evidence),
            'evidence': evidence,
            'patterns': patterns,
            'visual_contribution': contribution,
            'risk': risk,
            'default_decision': rec if evidence else 'not_available',
            'use_rule': 'Governed PRISMA capability. Prefer/require according to app profile and task type; justify if not used.'
        })

    app_matrix = []
    for app in apps:
        prof = APP_VISUAL_PROFILES.get(app, {'style':'general governed PRISMA surface','prefer':['prisma-tokens','prisma-recipes'], 'cautious':[], 'forbid':[]})
        available_ids = {c['id'] for c in capabilities if c.get('available')}
        recommended = [cid for cid in prof.get('prefer', []) if cid in available_ids]
        cautious = [cid for cid in prof.get('cautious', []) if cid in available_ids]
        missing_preferred = [cid for cid in prof.get('prefer', []) if cid not in available_ids]
        app_matrix.append({
            'app': app,
            'style_profile': prof.get('style',''),
            'recommended_to_exploit': recommended,
            'available_but_cautious': cautious,
            'missing_preferred': missing_preferred,
            'forbidden_or_guardrails': prof.get('forbid', []),
            'rule': 'Exploit recommended capabilities when they fit the concrete screen. Do not use cautious capabilities unless bounded and justified. Every unused available premium capability needs a reason in result evidence.'
        })

    candidates = find_candidate_target_files(repo, all_files, apps, task)
    decision = {
        'visual_required': visual_required,
        'principle': 'Exploit the maximum safe/governed visual stack per app/surface, not every library blindly.',
        'mandatory_when_visual_or_premium': [
            'VISUAL_CAPABILITY_MATRIX.json',
            'VISUAL_CAPABILITY_MATRIX.md',
            'VISUAL_STACK_DECISION.md',
            'APP_VISUAL_EXPLOITATION_MATRIX.md',
            'Per-result used/rejected capability rationale',
            'Layer budget notes',
            'Performance risk notes',
            'Visual evidence or explicit pending visual verification'
        ],
        'hard_rules': [
            'Prefer PRISMA governed components/recipes/tokens before raw libraries.',
            'Use Liquid/Pill/Cloudglass only when allowed by recipe map, authority map, surface adapter and layer budget.',
            'Do not install new dependencies.',
            'Do not claim premium visual exploitation unless used/rejected decisions are documented.',
            'Do not let visual atmosphere block operational clarity or touch flow.'
        ]
    }
    return {
        'schema_version': '2.0.0',
        'generated_by': 'PRISMA Authority Mesh Visual Capability Resolver',
        'task': task,
        'visual_required': visual_required,
        'apps': apps,
        'change_types': types,
        'capabilities': sorted(capabilities, key=lambda c: (str(c.get('family')), str(c.get('id')))),
        'app_visual_exploitation': app_matrix,
        'candidate_target_files': candidates,
        'decision': decision
    }


def _task_focus(task: str, apps: List[str]) -> Dict[str, Any]:
    text = task.lower()
    focus = {
        'primary_app': apps[0] if apps else 'quality',
        'screen_type': 'general',
        'signals': [],
        'premium_requested': any(w in text for w in ['premium','ultra','visual','interfaz','ui','ux','liquid','glass','cloudglass','pill']),
        'operational_surface': False,
    }
    signal_map = {
        'tablet_pos_sell': ['vender','venta','sell','pos','carrito','cart','checkout','cobrar','payment','pago'],
        'home_start': ['inicio','home','start','landing'],
        'dashboard': ['dashboard','panel','metric','kpi','report','reporte'],
        'background_atmosphere': ['background','backgrounds','fondo','fondos','atmosphere','atmósfera','cloudglass','liquid','glass'],
        'component_system': ['shared-ui','component','components','tokens','recipe','recipes','visual os','visual-os'],
    }
    for name, kws in signal_map.items():
        hits = [k for k in kws if k in text]
        if hits:
            focus['screen_type'] = name
            focus['signals'].extend(hits)
    if any(w in text for w in ['pos','vender','venta','sell','checkout','cobrar','payment','pago','sync','database','operational','operacion','operación']):
        focus['operational_surface'] = True
    if 'tablet' in apps and any(w in text for w in ['tablet','pos','vender','venta','checkout','carrito','cobrar']):
        focus['primary_app'] = 'tablet'
    elif 'pc' in apps and 'pc' in text:
        focus['primary_app'] = 'pc'
    elif 'mobile' in apps and any(w in text for w in ['mobile','movil','móvil']):
        focus['primary_app'] = 'mobile'
    elif 'shared-ui' in apps and any(w in text for w in ['shared-ui','visual os','component','recipe','tokens']):
        focus['primary_app'] = 'shared-ui'
    return focus


def _cap_lookup(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(c.get('id')): c for c in data.get('capabilities', [])}


def _requirement_level(app: str, cap_id: str, cap: Dict[str, Any], task: str, focus: Dict[str, Any]) -> str:
    if not cap.get('available'):
        return 'not_available'
    risk = str(cap.get('risk','')).lower()
    family = str(cap.get('family','')).lower()
    task_l = task.lower()
    primary = app == focus.get('primary_app')
    screen = focus.get('screen_type')
    premium = focus.get('premium_requested')

    mandatory_global = {'layer-budget','authority-map'}
    foundation = {'prisma-tokens','prisma-recipes','prisma-visual-os'}
    structure = {'prisma-components'}
    atmosphere = {'background-catalog','cloudglass-assets'}
    motion = {'framer-motion','motion'}
    radix = {'radix-dialog','radix-dropdown-menu','radix-scroll-area','radix-select','radix-tabs','radix-tooltip','radix-slot'}
    high_risk = {'ogl','three','gsap','react-spring','react-spring-web'}

    if cap_id in mandatory_global:
        return 'must_use'
    if premium and primary and cap_id in foundation:
        return 'must_use'
    if premium and primary and cap_id in structure:
        return 'should_use'
    if app == 'shared-ui' and cap_id in {'class-variance-authority','clsx','tailwind-merge','radix-slot'}:
        return 'should_use'
    if app == 'tablet' and screen == 'tablet_pos_sell':
        if cap_id in {'radix-scroll-area','radix-dialog','radix-select','lucide-react','clsx','class-variance-authority'}:
            return 'should_use'
        if cap_id in motion:
            return 'should_use'
        if cap_id in atmosphere:
            return 'consider_required'
        if cap_id in high_risk:
            return 'high_risk_optional'
    if app == 'pc':
        if cap_id in {'radix-tabs','radix-tooltip','radix-dialog','lucide-react','clsx'}:
            return 'should_use'
        if cap_id in atmosphere or cap_id in high_risk:
            return 'bounded_optional'
    if app == 'mobile':
        if cap_id in {'lucide-react','clsx','radix-slot'}:
            return 'should_use'
        if cap_id in high_risk or cap_id in {'cloudglass-assets','background-catalog'}:
            return 'forbidden_for_scope' if focus.get('operational_surface') else 'bounded_optional'
    if app == 'chart-lab':
        if cap_id in high_risk or cap_id in motion or cap_id in atmosphere:
            return 'should_use'
    if cap_id in high_risk:
        return 'high_risk_optional'
    if cap_id in atmosphere:
        return 'consider_required'
    if cap_id in radix or cap_id in motion:
        return 'consider_required'
    if risk == 'high' or family in {'webgl'}:
        return 'high_risk_optional'
    return 'consider_required'


def _requirement_reason(app: str, cap_id: str, level: str, focus: Dict[str, Any]) -> str:
    if level == 'must_use':
        return 'Foundational governed capability for premium work; use unless blocked and documented.'
    if level == 'should_use':
        return 'Expected to improve this app/screen when compatible; rejection needs explicit rationale.'
    if level == 'consider_required':
        return 'Must be evaluated for this task; use if it improves outcome without breaking guardrails.'
    if level == 'bounded_optional':
        return 'Available but must stay bounded to a safe surface/layer with evidence.'
    if level == 'high_risk_optional':
        return 'High-risk visual/power capability; use only with strong benefit, layer budget and performance rationale.'
    if level == 'forbidden_for_scope':
        return 'Blocked for this app/scope unless a stronger authority explicitly overrides it.'
    return 'Capability not detected in current repo scan.'


def build_visual_exploitation_contract(data: Dict[str, Any], task: str, now: str) -> Dict[str, Any]:
    apps = list(data.get('apps', []))
    focus = _task_focus(task, apps)
    caps = _cap_lookup(data)
    requirements: Dict[str, Any] = {}
    for app in apps:
        profile = APP_VISUAL_PROFILES.get(app, {'style':'general governed PRISMA surface','forbid':[]})
        rows = []
        for cap_id, cap in sorted(caps.items()):
            level = _requirement_level(app, cap_id, cap, task, focus)
            rows.append({
                'capability': cap_id,
                'available': bool(cap.get('available')),
                'level': level,
                'risk': cap.get('risk'),
                'family': cap.get('family'),
                'default_decision': cap.get('default_decision'),
                'visual_contribution': cap.get('visual_contribution'),
                'evidence_count': len(cap.get('evidence', [])),
                'reason': _requirement_reason(app, cap_id, level, focus),
            })
        requirements[app] = {
            'style_profile': profile.get('style','general governed PRISMA surface'),
            'guardrails': profile.get('forbid', []),
            'capabilities': rows,
        }

    hard_gates = [
        'visual_exploitation_contract_required',
        'app_capability_requirements_required',
        'screen_visual_stack_plan_required',
        'premium_acceptance_bar_required',
        'used_rejected_capability_matrix_required',
        'layer_budget_decision_required',
        'visual_evidence_or_pending_verification_required',
    ]
    premium_bar = {
        'minimum': [
            'Must show material visual transformation, not only blur/shadow/radius tweaks.',
            'Must use governed PRISMA foundations: tokens, recipes, Visual OS and layer budget when available.',
            'Must protect operational clarity, touch flow and performance for the target app/screen.',
            'Must include used/rejected capability rationale for every available visual capability relevant to the app.',
            'Must include visual evidence or explicitly mark visual PASS as pending user/browser verification.',
        ],
        'rejection_triggers': [
            'Claims premium without VISUAL_EXPLOITATION_CONTRACT.',
            'Available high-value PRISMA components/recipes ignored without reason.',
            'Global CSS blast or uncontrolled carpet-bombing.',
            'Heavy atmosphere/WebGL blocking an operational selling/payment flow.',
            'Functional smoke test used as visual PASS.',
            'Cross-surface mutation without app matrix and evidence.',
        ],
    }
    if focus.get('primary_app') == 'tablet':
        premium_bar['tablet_specific'] = [
            'Light, luminous, tactile, high-contrast-soft UI; no dark/obsidian dominant shell.',
            'Exploit PRISMA components/recipes/tokens first; raw libs must support the governed design, not replace it.',
            'Motion is for bounded tactile feedback and payment/cart state transitions, not spectacle.',
            'Atmospheric/background treatment must not compete with product/cart/checkout readability.',
        ]
    if focus.get('primary_app') == 'pc':
        premium_bar['pc_specific'] = [
            'Dense but readable desktop-grade surfaces; glass/graphite only if PC governor allows.',
            'Radix tabs/dialogs/tooltips may support richer control surfaces when useful.',
        ]
    if focus.get('primary_app') == 'mobile':
        premium_bar['mobile_specific'] = [
            'Premium means thin, fast, truthful and compact; avoid heavy atmosphere and WebGL.',
        ]

    used_rejected_template = [
        {'column':'capability','description':'Capability/library/component id.'},
        {'column':'available','description':'Was it detected in repo/package/lock/catalog evidence?'},
        {'column':'required_level','description':'must_use, should_use, consider_required, bounded_optional, high_risk_optional, forbidden_for_scope, not_available.'},
        {'column':'used','description':'yes/no.'},
        {'column':'where_used','description':'Changed file(s), component(s), layer(s), or n/a.'},
        {'column':'why_used_or_rejected','description':'Concrete task-specific rationale, not generic filler.'},
        {'column':'governance_evidence','description':'Recipe/map/component/contract/atlas/layer-budget evidence consulted.'},
        {'column':'performance_layer_risk','description':'Risk and mitigation.'},
        {'column':'visual_evidence','description':'Screenshot/video/manual pending marker.'},
    ]
    screen_plan = {
        'task_focus': focus,
        'candidate_target_files': data.get('candidate_target_files', [])[:80],
        'required_order': [
            'Read Authority Mesh files and Field Manual.',
            'Identify exact target screen from Atlas/docs/repo evidence; do not guess.',
            'Apply app capability requirements and Visual Exploitation Contract.',
            'Select minimal safe mutation set.',
            'Implement using must_use/should_use capabilities unless blocked with evidence.',
            'Fill used/rejected capability matrix in result package.',
            'Validate without process/port/dev-server/Prisma-hot manipulation.',
        ],
    }
    return {
        'schema_version':'3.0.0',
        'generated_by':'PRISMA GovMesh3 Visual Exploitation Resolver',
        'generated_at': now,
        'task': task,
        'mode':'ALL_PHASES_HARD_GATE_DECLARED',
        'phase_policy': {
            'phase_1_read_only_artifacts':'enabled',
            'phase_2_soft_gate_risks':'enabled',
            'phase_3_hard_gate_premium':'enabled',
            'phase_4_app_surface_profiles':'enabled',
            'single_iteration_install':'true',
        },
        'focus': focus,
        'hard_gates': hard_gates,
        'app_capability_requirements': requirements,
        'screen_visual_stack_plan': screen_plan,
        'premium_acceptance_bar': premium_bar,
        'used_rejected_requirement_template': used_rejected_template,
    }


def write_visual_exploitation_outputs(outdir: Path, data: Dict[str, Any], task: str, status: str, now: str) -> Dict[str, Any]:
    contract = build_visual_exploitation_contract(data, task, now)
    write_json(outdir/'VISUAL_EXPLOITATION_CONTRACT.json', contract)
    write_json(outdir/'APP_CAPABILITY_REQUIREMENTS.json', contract['app_capability_requirements'])

    md = ['# PRISMA Visual Exploitation Contract', '', f'- Status: `{status}`', f'- Task: `{task}`', f"- Mode: `{contract['mode']}`", f"- Generated: `{now}`", '', '## Phase policy', '']
    for k,v in contract['phase_policy'].items():
        md.append(f'- {k}: `{v}`')
    md += ['', '## Focus', '']
    for k,v in contract['focus'].items():
        md.append(f'- {k}: `{v}`')
    md += ['', '## Hard gates now required for premium/visual work', '']
    for gate in contract['hard_gates']:
        md.append(f'- {gate}')
    md += ['', '## Meaning', '', 'The Mesh does not merely report availability. It declares what must be exploited, what should be exploited, what must be considered, and what is bounded/high-risk/forbidden per app and task.']
    (outdir/'VISUAL_EXPLOITATION_CONTRACT.md').write_text('\n'.join(md)+'\n', encoding='utf-8')

    plan = contract['screen_visual_stack_plan']
    smd = ['# PRISMA Screen Visual Stack Plan', '', f'- Task: `{task}`', '', '## Required order', '']
    for item in plan['required_order']:
        smd.append(f'- {item}')
    smd += ['', '## Candidate target files', '']
    for cand in plan.get('candidate_target_files', [])[:60]:
        smd.append(f"- score={cand.get('score')} `{cand.get('path')}`")
    smd += ['', '## Focus', '']
    for k,v in plan['task_focus'].items():
        smd.append(f'- {k}: `{v}`')
    (outdir/'SCREEN_VISUAL_STACK_PLAN.md').write_text('\n'.join(smd)+'\n', encoding='utf-8')

    amd = ['# PRISMA Premium Acceptance Bar', '', f'- Task: `{task}`', '', '## Minimum bar', '']
    for item in contract['premium_acceptance_bar'].get('minimum', []):
        amd.append(f'- {item}')
    for key, items in contract['premium_acceptance_bar'].items():
        if key in {'minimum','rejection_triggers'}:
            continue
        amd += ['', f'## {key}', '']
        for item in items:
            amd.append(f'- {item}')
    amd += ['', '## Rejection triggers', '']
    for item in contract['premium_acceptance_bar'].get('rejection_triggers', []):
        amd.append(f'- {item}')
    (outdir/'PREMIUM_ACCEPTANCE_BAR.md').write_text('\n'.join(amd)+'\n', encoding='utf-8')

    rmd = ['# PRISMA Used / Rejected Capability Requirement', '', 'Every visual/premium result package must include a completed table with these columns:', '', '| Column | Description |', '|---|---|']
    for row in contract['used_rejected_requirement_template']:
        rmd.append(f"| {row['column']} | {row['description']} |")
    rmd += ['', '## Gate', '', 'No premium/visual PASS is valid unless this used/rejected table is completed with concrete file-level and governance-level rationale.']
    (outdir/'USED_REJECTED_REQUIREMENT.md').write_text('\n'.join(rmd)+'\n', encoding='utf-8')

    req_md = ['# PRISMA App Capability Requirements', '', f'- Task: `{task}`', '', '| App | must_use | should_use | consider_required | bounded_optional | high_risk_optional | forbidden_for_scope |', '|---|---|---|---|---|---|---|']
    for app, payload in contract['app_capability_requirements'].items():
        grouped: Dict[str, List[str]] = {k: [] for k in ['must_use','should_use','consider_required','bounded_optional','high_risk_optional','forbidden_for_scope']}
        for c in payload.get('capabilities', []):
            if c.get('level') in grouped:
                grouped[c['level']].append(c['capability'])
        req_md.append('| ' + app + ' | ' + ' | '.join(', '.join(grouped[k]) or '—' for k in ['must_use','should_use','consider_required','bounded_optional','high_risk_optional','forbidden_for_scope']) + ' |')
    (outdir/'APP_CAPABILITY_REQUIREMENTS.md').write_text('\n'.join(req_md)+'\n', encoding='utf-8')
    return contract


def write_visual_capability_outputs(outdir: Path, data: Dict[str, Any], task: str, status: str, now: str) -> None:
    write_json(outdir/'VISUAL_CAPABILITY_MATRIX.json', data)

    caps = data.get('capabilities', [])
    md = ['# PRISMA Visual Capability Matrix', '', f'- Task: `{task}`', f'- Status: `{status}`', f'- Generated: `{now}`', f"- Visual required: `{data.get('visual_required')}`", '', '| Capability | Kind | Available | Risk | Default decision | Evidence count | Contribution |', '|---|---|---:|---|---|---:|---|']
    for c in caps:
        contrib = str(c.get('visual_contribution','')).replace('|','/')
        md.append(f"| {c.get('id')} | {c.get('kind')} | {'yes' if c.get('available') else 'no'} | {c.get('risk')} | {c.get('default_decision')} | {len(c.get('evidence', []))} | {contrib} |")
    md += ['', '## Rule', '', 'For premium/visual work, the result package must list which available capabilities were used, which were rejected, and why. No blind all-library usage; no tiny cosmetic fake-premium.']
    (outdir/'VISUAL_CAPABILITY_MATRIX.md').write_text('\n'.join(md)+'\n', encoding='utf-8')

    stack = ['# PRISMA Visual Stack Decision', '', f'- Task: `{task}`', f"- Visual required: `{data.get('visual_required')}`", '', '## Principle', '', data.get('decision', {}).get('principle',''), '', '## Mandatory outputs when visual/premium', '']
    for item in data.get('decision', {}).get('mandatory_when_visual_or_premium', []):
        stack.append(f'- {item}')
    stack += ['', '## Hard rules', '']
    for item in data.get('decision', {}).get('hard_rules', []):
        stack.append(f'- {item}')
    stack += ['', '## Candidate target files', '']
    for cand in data.get('candidate_target_files', [])[:40]:
        stack.append(f"- score={cand.get('score')} `{cand.get('path')}`")
    stack += ['', '## GovMesh3 escalation', '', '- Also obey `VISUAL_EXPLOITATION_CONTRACT.md`.', '- Also obey `APP_CAPABILITY_REQUIREMENTS.json` / `.md`.', '- Also obey `SCREEN_VISUAL_STACK_PLAN.md`.', '- Also obey `PREMIUM_ACCEPTANCE_BAR.md`.', '- Result packages must complete `USED_REJECTED_REQUIREMENT.md`.']
    (outdir/'VISUAL_STACK_DECISION.md').write_text('\n'.join(stack)+'\n', encoding='utf-8')

    appmd = ['# PRISMA App Visual Exploitation Matrix', '', f'- Task: `{task}`', f'- Generated: `{now}`', '', '| App | Style profile | Recommended to exploit | Cautious/high-risk available | Guardrails |', '|---|---|---|---|---|']
    for row in data.get('app_visual_exploitation', []):
        appmd.append(f"| {row.get('app')} | {row.get('style_profile')} | {', '.join(row.get('recommended_to_exploit', [])) or '—'} | {', '.join(row.get('available_but_cautious', [])) or '—'} | {'; '.join(row.get('forbidden_or_guardrails', [])) or '—'} |")
    appmd += ['', '## Result requirement', '', 'Each visual/premium implementation must include a used/rejected capability decision table. Available capability does not mean mandatory use; it means mandatory consideration and justification.', '', '## GovMesh3 requirement', '', 'For premium/visual work, this matrix is not enough by itself. Use `VISUAL_EXPLOITATION_CONTRACT.md` and `APP_CAPABILITY_REQUIREMENTS.md` to determine must/should/consider/bounded/high-risk/forbidden obligations.']
    (outdir/'APP_VISUAL_EXPLOITATION_MATRIX.md').write_text('\n'.join(appmd)+'\n', encoding='utf-8')

    write_visual_exploitation_outputs(outdir, data, task, status, now)

# --- END PRISMA GOVMESH2 -----------------------------------------------------


def build_outputs(repo: Path, task: str, outdir: Path, full: bool, rules_path: Path) -> Dict[str, Any]:
    rules = load_json(rules_path)
    all_files = walk_files(repo, rules.get('runtime_scan_excludes', []))
    apps, types = classify_task(task, rules, full)
    now = _dt.datetime.now().astimezone().isoformat(timespec='seconds')

    readset: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    gate_requirements: List[str] = []
    forbidden = list(rules.get('forbidden_default_actions', []))

    # Global required
    for req in rules.get('global_required', []):
        matches = match_glob(repo, all_files, req['glob'])
        if matches:
            add_matches(readset, repo, matches, req['id'], 'global_required')
        else:
            missing.append({'id': req['id'], 'glob': req['glob'], 'critical': bool(req.get('critical')), 'reason': 'global_required_missing'})

    # Apps
    app_matrix = []
    for app, cfg in rules.get('apps', {}).items():
        applies = app in apps
        mutation_allowed = applies and app not in ['quality']
        found_count = 0
        missing_for_app = []
        if applies:
            for pat in cfg.get('authority', []):
                matches = match_glob(repo, all_files, pat)
                found_count += len(matches)
                if matches:
                    add_matches(readset, repo, matches, f'app:{app}', f'{app}_authority')
                else:
                    missing_for_app.append(pat)
                    missing.append({'id': f'app:{app}', 'glob': pat, 'critical': False, 'reason': f'{app}_authority_missing'})
        app_matrix.append({
            'app': app,
            'applies': applies,
            'roots': cfg.get('roots', []),
            'authority_files_found': found_count,
            'missing_patterns': missing_for_app,
            'mutation_allowed': mutation_allowed,
            'exclusion_reason': '' if applies else 'Not directly selected by task classifier; still can be promoted by shared/runtime impact.'
        })

    # Change types
    runtime_scans = {}
    for typ in types:
        cfg = rules.get('change_types', {}).get(typ, {})
        for gate in cfg.get('required_gates', []):
            if gate not in gate_requirements:
                gate_requirements.append(gate)
        for act in cfg.get('forbidden_actions', []):
            if act not in forbidden:
                forbidden.append(act)
        for pat in cfg.get('authority', []):
            matches = match_glob(repo, all_files, pat)
            if matches:
                add_matches(readset, repo, matches, f'type:{typ}', f'{typ}_authority')
            else:
                missing.append({'id': f'type:{typ}', 'glob': pat, 'critical': False, 'reason': f'{typ}_authority_missing'})
        if cfg.get('runtime_scan'):
            runtime_scans[typ] = scan_text_patterns(repo, all_files, cfg['runtime_scan'], rules)

    # Always surface quality contracts if present
    for pat in ['quality/contracts/**','quality/policies/**','quality/profiles/**','tools/prisma-visual/**','tools/prisma-visual-system/**']:
        matches = match_glob(repo, all_files, pat)
        if matches:
            add_matches(readset, repo, matches, 'quality:always', 'quality_governance_scan')

    unmapped_info = find_unmapped_and_excluded(repo, all_files)

    # Contract/gate matrix
    contract_files = [r for r in readset if '/contracts/' in r['path'] or r['path'].startswith('quality/contracts/')]
    contract_matrix = {
        'task': task,
        'apps': apps,
        'change_types': types,
        'required_gates': gate_requirements + ['authority_readset_lock_required','app_impact_matrix_required','contract_gate_matrix_required','rollback_required','diagnostic_zip_on_failure','no_fake_green'],
        'forbidden_default_actions': forbidden,
        'contracts_found': contract_files,
        'critical_missing': [m for m in missing if m.get('critical')],
        'all_missing': missing,
    }

    visual_data = build_visual_capability_data(repo, all_files, apps, types, task, rules)
    if visual_data.get('visual_required'):
        for gate in [
            'visual_capability_matrix_required',
            'visual_stack_decision_required',
            'app_visual_exploitation_matrix_required',
            'visual_capability_rejection_reasons_required',
            'visual_exploitation_contract_required',
            'app_capability_requirements_required',
            'screen_visual_stack_plan_required',
            'premium_acceptance_bar_required',
            'used_rejected_capability_matrix_required',
            'layer_budget_decision_required',
            'visual_evidence_or_pending_verification_required'
        ]:
            if gate not in contract_matrix['required_gates']:
                contract_matrix['required_gates'].append(gate)

    status = 'PASS'
    if contract_matrix['critical_missing']:
        status = 'BLOCKED_CRITICAL_AUTHORITY_MISSING'
    elif missing:
        status = 'WARN_AUTHORITY_PATTERNS_MISSING'

    lock = {
        'schema_version':'1.0.0',
        'tool':'PRISMA Authority Mesh',
        'generated_at': now,
        'repo': str(repo),
        'task': task,
        'full_mode': full,
        'status': status,
        'apps_detected': apps,
        'change_types_detected': types,
        'authority_file_count': len(readset),
        'readset': sorted(readset, key=lambda x: x['path']),
        'missing': missing,
        'runtime_scans': runtime_scans,
        'unmapped_and_excluded_review': unmapped_info,
        'visual_capability_resolver': {
            'schema_version': visual_data.get('schema_version'),
            'visual_required': visual_data.get('visual_required'),
            'capability_count': len(visual_data.get('capabilities', [])),
            'available_capability_count': len([c for c in visual_data.get('capabilities', []) if c.get('available')]),
            'apps': visual_data.get('apps', []),
            'candidate_target_files': visual_data.get('candidate_target_files', [])[:40],
            'govmesh3_outputs': [
                'VISUAL_EXPLOITATION_CONTRACT.md',
                'VISUAL_EXPLOITATION_CONTRACT.json',
                'APP_CAPABILITY_REQUIREMENTS.json',
                'APP_CAPABILITY_REQUIREMENTS.md',
                'SCREEN_VISUAL_STACK_PLAN.md',
                'PREMIUM_ACCEPTANCE_BAR.md',
                'USED_REJECTED_REQUIREMENT.md'
            ],
        },
    }

    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir/'AUTHORITY_READSET.lock.json', lock)
    write_json(outdir/'CONTRACT_AND_GATE_MATRIX.json', contract_matrix)
    write_visual_capability_outputs(outdir, visual_data, task, status, now)

    # App matrix markdown
    md = ['# PRISMA App Impact Matrix', '', f'- Task: `{task}`', f'- Status: `{status}`', f'- Generated: `{now}`', '', '| App / surface | Applies | Authority files found | Mutation allowed | Exclusion / notes |', '|---|---:|---:|---:|---|']
    for row in app_matrix:
        md.append(f"| {row['app']} | {'yes' if row['applies'] else 'no'} | {row['authority_files_found']} | {'yes' if row['mutation_allowed'] else 'no'} | {row['exclusion_reason'] or 'Selected by task.'} |")
    (outdir/'APP_IMPACT_MATRIX.md').write_text('\n'.join(md)+'\n', encoding='utf-8')

    # Risks
    risks = ['# Missing / Unmapped / Excluded Risk Review', '', f'- Status: `{status}`', '']
    if missing:
        risks += ['## Missing authority patterns', '']
        for m in missing[:300]:
            risks.append(f"- `{m['glob']}` — {m['reason']} — critical={m.get('critical', False)}")
    else:
        risks += ['No missing authority patterns detected.', '']
    risks += ['', '## Unmapped/excluded candidates', '']
    if unmapped_info.get('candidate_files'):
        for c in unmapped_info['candidate_files'][:20]:
            risks.append(f"- `{c['path']}` — items≈{c['item_count_estimate']}")
            for item in c.get('sample_items', [])[:10]:
                risks.append(f"  - {item[2:]}")
    else:
        risks.append('No explicit unmapped/excluded state files found in the live repo scan. If using GOBIERNO extract ZIPs, review their META package separately.')
    if runtime_scans:
        risks += ['', '## Runtime scan highlights', '']
        for typ, pats in runtime_scans.items():
            risks.append(f'### {typ}')
            for pat, data in pats.items():
                risks.append(f"- `{pat}` matches={len(data['matches'])} truncated={data['truncated']}")
                for mm in data['matches'][:12]:
                    risks.append(f"  - `{mm['path']}`")
    (outdir/'MISSING_OR_UNMAPPED_RISK.md').write_text('\n'.join(risks)+'\n', encoding='utf-8')

    # Agent prompt envelope
    env = ['# PRISMA AUTHORITY MESH ENVELOPE', '', f'Task: {task}', '', f'Status: `{status}`', '', '## Apps / surfaces detected', '']
    for app in apps:
        env.append(f'- {app}')
    env += ['', '## Change types detected', '']
    for typ in types or ['general']:
        env.append(f'- {typ}')
    env += ['', '## Mandatory readset lock', '', 'Use `.governance/current/AUTHORITY_READSET.lock.json` as the authority readset for this task. Do not create patches without it.', '', '## Required gates', '']
    for gate in contract_matrix['required_gates']:
        env.append(f'- {gate}')
    env += ['', '## Forbidden default actions', '']
    for act in forbidden:
        env.append(f'- {act}')
    env += ['', '## Missing authority check', '']
    if contract_matrix['critical_missing']:
        env.append('Critical authority is missing. Do not patch. Resolve/report missing sources first.')
    elif missing:
        env.append('Non-critical authority patterns are missing. Review `MISSING_OR_UNMAPPED_RISK.md` before patching.')
    else:
        env.append('No missing authority patterns detected.')
    env += ['', '## Required output evidence', '', '- Include `.governance/current` in result or diagnostic ZIP.', '- Do not claim PASS without contract/gate evidence.', '- For visual work, include visual evidence beyond functional smoke tests.', '- For hot work, do not kill processes or regenerate Prisma.']
    (outdir/'AGENT_PROMPT_ENVELOPE.md').write_text('\n'.join(env)+'\n', encoding='utf-8')

    # Summary report
    report = ['# PRISMA Authority Mesh Report', '', f'- Status: `{status}`', f'- Task: `{task}`', f'- Repo: `{repo}`', f'- Authority files found: `{len(readset)}`', f'- Missing patterns: `{len(missing)}`', f'- Critical missing: `{len(contract_matrix["critical_missing"])}`', f'- Apps: `{", ".join(apps)}`', f'- Change types: `{", ".join(types) if types else "general"}`', '', '## Generated files', '', '- AUTHORITY_READSET.lock.json', '- APP_IMPACT_MATRIX.md', '- CONTRACT_AND_GATE_MATRIX.json', '- MISSING_OR_UNMAPPED_RISK.md', '- AGENT_PROMPT_ENVELOPE.md', '- VISUAL_CAPABILITY_MATRIX.json', '- VISUAL_CAPABILITY_MATRIX.md', '- VISUAL_STACK_DECISION.md', '- APP_VISUAL_EXPLOITATION_MATRIX.md', '- VISUAL_EXPLOITATION_CONTRACT.md', '- VISUAL_EXPLOITATION_CONTRACT.json', '- APP_CAPABILITY_REQUIREMENTS.json', '- APP_CAPABILITY_REQUIREMENTS.md', '- SCREEN_VISUAL_STACK_PLAN.md', '- PREMIUM_ACCEPTANCE_BAR.md', '- USED_REJECTED_REQUIREMENT.md']
    (outdir/'AUTHORITY_MESH_REPORT.md').write_text('\n'.join(report)+'\n', encoding='utf-8')

    return {'status': status, 'outdir': str(outdir), 'readset_count': len(readset), 'missing_count': len(missing), 'critical_missing_count': len(contract_matrix['critical_missing'])}


def selftest() -> int:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        repo=Path(td)/'repo'
        (repo/'docs/ops').mkdir(parents=True)
        (repo/'docs/atlas').mkdir(parents=True)
        (repo/'quality/contracts').mkdir(parents=True)
        (repo/'products/tablet/app/docs/atlas').mkdir(parents=True)
        (repo/'config/prisma-visual').mkdir(parents=True)
        for p in ['docs/PRISMA_CURRENT_STATE.json','docs/PRISMA_CURRENT_STATE.md','docs/PRISMA_DOCUMENT_PRECEDENCE_RULES.md','docs/PRISMA_MASTER_DOC_INDEX.md','docs/PRISMA_OPERATIONAL_SAFETY_RULES.md','docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md','docs/atlas/atlas.registry.json','docs/atlas/governor.atlas-map.json','docs/atlas/GOVERNOR_ATLAS_LOCATION.md','quality/prisma-quality.manifest.json','quality/contracts/no-fake-green.contract.json','quality/contracts/traceable-operation.contract.json','quality/contracts/release-evidence-required.contract.json','products/tablet/app/docs/atlas/ATLAS_TABLET_VISUAL.md','config/prisma-visual/tablet-usage-map.json']:
            f=repo/p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text('{}' if f.suffix=='.json' else '# x', encoding='utf-8')
        rules_path=Path(__file__).with_name('authority_mesh_rules.json')
        res=build_outputs(repo,'mejorar visual tablet liquid glass',repo/'.governance/current',False,rules_path)
        assert (repo/'.governance/current/AUTHORITY_READSET.lock.json').exists()
        assert (repo/'.governance/current/VISUAL_CAPABILITY_MATRIX.json').exists()
        assert (repo/'.governance/current/VISUAL_STACK_DECISION.md').exists()
        assert (repo/'.governance/current/APP_VISUAL_EXPLOITATION_MATRIX.md').exists()
        assert (repo/'.governance/current/VISUAL_EXPLOITATION_CONTRACT.md').exists()
        assert (repo/'.governance/current/VISUAL_EXPLOITATION_CONTRACT.json').exists()
        assert (repo/'.governance/current/APP_CAPABILITY_REQUIREMENTS.json').exists()
        assert (repo/'.governance/current/APP_CAPABILITY_REQUIREMENTS.md').exists()
        assert (repo/'.governance/current/SCREEN_VISUAL_STACK_PLAN.md').exists()
        assert (repo/'.governance/current/PREMIUM_ACCEPTANCE_BAR.md').exists()
        assert (repo/'.governance/current/USED_REJECTED_REQUIREMENT.md').exists()
        gates=json.loads((repo/'.governance/current/CONTRACT_AND_GATE_MATRIX.json').read_text(encoding='utf-8')).get('required_gates', [])
        assert 'visual_exploitation_contract_required' in gates
        assert 'used_rejected_capability_matrix_required' in gates
        assert res['readset_count'] >= 10
    print('AUTHORITY_MESH_SELFTEST_OK')
    return 0


def main(argv: List[str] | None = None) -> int:
    ap=argparse.ArgumentParser(description='PRISMA Authority Mesh preflight')
    ap.add_argument('--task', default='GLOBAL ALL APPS ALL SURFACES AUTHORITY PREFLIGHT')
    ap.add_argument('--repo', default='')
    ap.add_argument('--output', default='.governance/current')
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--rules', default='')
    ap.add_argument('--selftest', action='store_true')
    ns=ap.parse_args(argv)
    if ns.selftest:
        return selftest()
    start=Path(ns.repo) if ns.repo else Path.cwd()
    repo=discover_repo(start)
    rules_path=Path(ns.rules) if ns.rules else Path(__file__).with_name('authority_mesh_rules.json')
    outdir=Path(ns.output)
    if not outdir.is_absolute():
        outdir=repo/outdir
    res=build_outputs(repo, ns.task, outdir, ns.full, rules_path)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if res['status'] in ['PASS','WARN_AUTHORITY_PATTERNS_MISSING','BLOCKED_CRITICAL_AUTHORITY_MISSING'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
