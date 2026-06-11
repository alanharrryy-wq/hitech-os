#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRISMA Authority Mesh
Read-mostly preflight that resolves live governance authority for all PRISMA apps/surfaces.
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
    }

    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir/'AUTHORITY_READSET.lock.json', lock)
    write_json(outdir/'CONTRACT_AND_GATE_MATRIX.json', contract_matrix)

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
    report = ['# PRISMA Authority Mesh Report', '', f'- Status: `{status}`', f'- Task: `{task}`', f'- Repo: `{repo}`', f'- Authority files found: `{len(readset)}`', f'- Missing patterns: `{len(missing)}`', f'- Critical missing: `{len(contract_matrix["critical_missing"])}`', f'- Apps: `{", ".join(apps)}`', f'- Change types: `{", ".join(types) if types else "general"}`', '', '## Generated files', '', '- AUTHORITY_READSET.lock.json', '- APP_IMPACT_MATRIX.md', '- CONTRACT_AND_GATE_MATRIX.json', '- MISSING_OR_UNMAPPED_RISK.md', '- AGENT_PROMPT_ENVELOPE.md']
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
