#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

PACKAGE = "PRISMA_BLACK_VISUAL_REFINEMENT_01G"
REQUIRED_FILES = [
    'docs/design/PRISMA_BLACK_VISUAL_REFINEMENT_01G.md',
    'docs/qa/PRISMA_BLACK_VISUAL_REFINEMENT_01G_QA.md',
    'shared/contracts/ui/prisma-black-visual-refinement-01g.contract.json',
    'manifests/PRISMA_BLACK_VISUAL_REFINEMENT_01G.manifest.json',
    'tools/prisma/prisma_black_visual_guardian_01g.py',
    'products/shared-ui/prisma/tokens/prisma-theme.css',
    'products/shared-ui/prisma/components/prisma-components.css',
    'products/tablet/app/components/pos/pos.module.css',
    'products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css',
    'products/tablet/app/app/globals.css',
    'products/pc/app/app/globals.css',
    'products/pc/app/app/pulso/prisma-pulso.module.css',
]
SURFACE_PATH_HINTS = {
    'tablet': ['products/tablet/'],
    'pc': ['products/pc/app/app/globals.css'],
    'mobile': ['products/pc/app/app/pulso/'],
}
MARKER = PACKAGE
ALLOWED_STATUS = {'TOUCHED', 'VALIDATED', 'EXCLUDED'}
FORBIDDEN_STATUS = {'OMITTED'}


def parse_args():
    parser = argparse.ArgumentParser(description='Guardian checker for PRISMA Black Visual Refinement 01G')
    parser.add_argument('--root', default='.', help='Root path of terminal-de-venta-system')
    parser.add_argument('--manifest', default='manifests/PRISMA_BLACK_VISUAL_REFINEMENT_01G.manifest.json', help='Manifest path relative to root or absolute')
    parser.add_argument('--text', action='store_true', help='Human output instead of JSON')
    return parser.parse_args()


def resolve(root: Path, maybe_path: str) -> Path:
    p = Path(maybe_path)
    return p if p.is_absolute() else root / p


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    manifest_path = resolve(root, args.manifest)
    result = {
        'guardian': PACKAGE,
        'root': str(root),
        'ok': True,
        'requiredFiles': [],
        'surfaceCoverage': {},
        'warnings': [],
        'errors': [],
        'summary': '',
    }

    if not root.exists() or not root.is_dir():
        result['ok'] = False
        result['errors'].append(f'Root no existe o no es directorio: {root}')
    if not manifest_path.exists():
        result['ok'] = False
        result['errors'].append(f'Manifest no existe: {manifest_path}')

    for rel in REQUIRED_FILES:
        present = (root / rel).exists()
        result['requiredFiles'].append({'file': rel, 'present': present})
        if not present:
            result['ok'] = False

    manifest = {}
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        coverage = manifest.get('coverage', {})
        invariants = manifest.get('autonomyInvariants', {})
        changed = manifest.get('changedFiles', [])
        marker = manifest.get('marker')

        if marker != MARKER:
            result['ok'] = False
            result['errors'].append(f'Marker de manifest inválido: {marker}')

        for surface in ('tablet', 'pc', 'mobile'):
            info = coverage.get(surface)
            if not isinstance(info, dict):
                result['ok'] = False
                result['errors'].append(f'Falta cobertura para superficie: {surface}')
                continue
            status = info.get('status')
            paths = info.get('paths', [])
            reasons = info.get('reason', '')
            surface_result = {'status': status, 'paths': paths}
            result['surfaceCoverage'][surface] = surface_result
            if status in FORBIDDEN_STATUS or status not in ALLOWED_STATUS:
                result['ok'] = False
                result['errors'].append(f'Estado inválido para {surface}: {status}')
            if status == 'EXCLUDED' and len(str(reasons).strip()) < 12:
                result['ok'] = False
                result['errors'].append(f'Exclusión débil para {surface}: requiere razón explícita')

        if invariants.get('tabletStandalone') is not True:
            result['ok'] = False
            result['errors'].append('Invariant rota: tabletStandalone debe ser true')
        if invariants.get('pcRequiredForTabletSale') is not False:
            result['ok'] = False
            result['errors'].append('Invariant rota: pcRequiredForTabletSale debe ser false')
        if invariants.get('mobileRequiredForTabletSale') is not False:
            result['ok'] = False
            result['errors'].append('Invariant rota: mobileRequiredForTabletSale debe ser false')

        for surface, hints in SURFACE_PATH_HINTS.items():
            touched = any(any(h in rel for h in hints) for rel in changed)
            status = coverage.get(surface, {}).get('status')
            if touched and status != 'TOUCHED':
                result['ok'] = False
                result['errors'].append(f'Superficie {surface} tiene archivos tocados pero status={status}')

        shared_touched = any(rel.startswith('products/shared-ui/prisma/') for rel in changed)
        if shared_touched:
            for surface in ('tablet', 'pc', 'mobile'):
                if coverage.get(surface, {}).get('status') == 'EXCLUDED':
                    result['ok'] = False
                    result['errors'].append(f'Hay shared-ui tocado y {surface} no puede quedar EXCLUDED')

        for rel in changed:
            path = root / rel
            if not path.exists():
                result['ok'] = False
                result['errors'].append(f'Archivo declarado en changedFiles no existe: {rel}')
            elif rel.endswith('.css'):
                text = path.read_text(encoding='utf-8')
                if MARKER not in text:
                    result['ok'] = False
                    result['errors'].append(f'Falta marker {MARKER} en CSS: {rel}')

    result['summary'] = 'Guardian OK: cobertura tri-superficie y autonomía Tablet preservadas.' if result['ok'] else 'Guardian FAIL: revisar contrato, cobertura o markers.'

    if args.text:
        print(result['summary'])
        print(f"Root: {result['root']}")
        print(f"Required files: {sum(1 for item in result['requiredFiles'] if item['present'])}/{len(result['requiredFiles'])}")
        print(f"Surface coverage keys: {', '.join(sorted(result['surfaceCoverage'].keys()))}")
        print(f"Warnings: {len(result['warnings'])}")
        print(f"Errors: {len(result['errors'])}")
        for item in result['errors']:
            print(f"- {item}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
