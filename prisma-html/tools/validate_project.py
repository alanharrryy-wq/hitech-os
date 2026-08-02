from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import tinycss2


MANIFEST_IGNORED_DIRS = {
    '__pycache__',
    '.wrangler',
    'cloudflare-results',
    'dist',
    'node_modules',
}
MANIFEST_IGNORED_NAMES = {'.DS_Store', 'Thumbs.db'}
MANIFEST_IGNORED_SUFFIXES = ('.fail.zip', '.partial.zip', '.pyc', '.result.zip')


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.refs = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get('id'):
            self.ids.append(data['id'])
        for attr in ('href', 'src'):
            if data.get(attr):
                self.refs.append((tag, data[attr]))
        if tag == 'script' and data.get('src'):
            self.scripts.append(data)


def is_local(ref):
    return not (
        ref.startswith(('#', 'data:', 'mailto:', 'tel:', 'javascript:'))
        or urlparse(ref).scheme in {'http', 'https'}
    )


def is_primary_scope(path):
    return (
        'backup_original' not in path.parts
        and 'dist' not in path.parts
        and 'extras' not in path.parts
        and 'rollback' not in path.parts
    )


def validate_files_manifest(root):
    manifest_path = root / 'FILES_MANIFEST.json'
    issues = []
    if not manifest_path.is_file():
        return {'ok': False, 'entry_count': 0, 'issues': ['FILES_MANIFEST.json missing']}

    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    except (OSError, json.JSONDecodeError) as error:
        return {'ok': False, 'entry_count': 0, 'issues': [f'FILES_MANIFEST.json invalid: {error}']}

    entries = manifest.get('files', [])
    if manifest.get('file_count_excluding_manifest') != len(entries):
        issues.append('declared file count does not match manifest entries')

    paths = [entry.get('path') for entry in entries]
    valid_paths = [path for path in paths if isinstance(path, str)]
    if len(valid_paths) != len(entries):
        issues.append('manifest contains a non-string path')
    if len(valid_paths) != len(set(valid_paths)):
        issues.append('manifest contains duplicate paths')

    actual_paths = set()
    for path in root.rglob('*'):
        if not path.is_file() or path == manifest_path:
            continue
        relative = path.relative_to(root)
        if any(part in MANIFEST_IGNORED_DIRS for part in relative.parts):
            continue
        if path.name in MANIFEST_IGNORED_NAMES or path.name.endswith(MANIFEST_IGNORED_SUFFIXES):
            continue
        actual_paths.add(relative.as_posix())

    manifest_paths = set(valid_paths)
    uncovered = sorted(actual_paths - manifest_paths)
    extraneous = sorted(manifest_paths - actual_paths)
    if uncovered:
        issues.append(f'uncovered files: {uncovered[:20]}')
    if extraneous:
        issues.append(f'extraneous or missing files: {extraneous[:20]}')

    for entry in entries:
        relative = entry.get('path')
        if not isinstance(relative, str):
            continue
        if '#U' in relative or Path(relative).is_absolute() or '..' in Path(relative).parts:
            issues.append(f'unsafe or mechanically corrupted path: {relative}')
            continue
        path = root / relative
        if not path.is_file():
            continue
        if path.stat().st_size != entry.get('bytes'):
            issues.append(f'byte count mismatch: {relative}')
        digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        if digest != entry.get('sha256'):
            issues.append(f'SHA-256 mismatch: {relative}')

    return {'ok': not issues, 'entry_count': len(entries), 'issues': issues}


def split_selectors(text):
    selectors, buffer, depth, quote, escape = [], [], 0, None, False
    for char in text:
        if escape:
            buffer.append(char)
            escape = False
            continue
        if char == '\\\\':
            buffer.append(char)
            escape = True
            continue
        if quote:
            buffer.append(char)
            if char == quote:
                quote = None
            continue
        if char in ('"', "'"):
            quote = char
            buffer.append(char)
            continue
        if char in '([':
            depth += 1
        elif char in ')]':
            depth = max(0, depth - 1)
        if char == ',' and depth == 0:
            value = ''.join(buffer).strip()
            if value:
                selectors.append(value)
            buffer = []
        else:
            buffer.append(char)
    value = ''.join(buffer).strip()
    if value:
        selectors.append(value)
    return selectors


def combine_selectors(parents, nested):
    nested_selectors = split_selectors(nested)
    if not parents:
        return nested_selectors
    combined = []
    for parent in parents:
        for child in nested_selectors:
            combined.append(child.replace('&', parent) if '&' in child else f'{parent} {child}')
    return combined


def normalize_css_text(value):
    return re.sub(r'\s+', ' ', value).strip()


def collect_css_rules(root):
    records = []

    def walk(items, path, parents=None, context=()):
        for item in items:
            if item.type == 'qualified-rule':
                raw = normalize_css_text(tinycss2.serialize(item.prelude))
                selectors = [
                    normalize_css_text(selector)
                    for selector in combine_selectors(parents, raw)
                ]
                declarations = []
                for declaration in tinycss2.parse_declaration_list(
                    item.content,
                    skip_whitespace=True,
                    skip_comments=True,
                ):
                    if declaration.type != 'declaration':
                        continue
                    declarations.append({
                        'property': declaration.lower_name,
                        'value': normalize_css_text(tinycss2.serialize(declaration.value)),
                        'important': bool(declaration.important),
                    })

                records.append({
                    'selectors': selectors,
                    'selector_text': raw,
                    'file': path.relative_to(root).as_posix(),
                    'context': list(context),
                    'line': item.source_line,
                    'column': getattr(item, 'source_column', None),
                    'declarations': declarations,
                })

                inner = tinycss2.parse_blocks_contents(
                    item.content,
                    skip_whitespace=True,
                    skip_comments=True,
                )
                nested = [
                    child for child in inner
                    if child.type in {'qualified-rule', 'at-rule'}
                ]
                if nested:
                    walk(nested, path, selectors, context)
            elif item.type == 'at-rule' and item.content is not None:
                prelude = normalize_css_text(tinycss2.serialize(item.prelude))
                label = f'@{item.at_keyword} {prelude}'.strip()
                inner = tinycss2.parse_blocks_contents(
                    item.content,
                    skip_whitespace=True,
                    skip_comments=True,
                )
                walk(inner, path, parents, context + (label,))

    for path in root.rglob('*.css'):
        if not is_primary_scope(path):
            continue
        rules = tinycss2.parse_stylesheet(
            path.read_text(encoding='utf-8', errors='replace'),
            skip_whitespace=True,
            skip_comments=True,
        )
        parse_errors = [rule for rule in rules if rule.type == 'error']
        if parse_errors:
            records.append({
                'css_parse_errors': [error.message for error in parse_errors],
                'file': path.relative_to(root).as_posix(),
            })
        walk(rules, path)
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)

    checks, errors, warnings = [], [], []
    expected = [
        'index.html', 'index.css',
        'paginas/pagina-1-prisma/index.html', 'paginas/pagina-1-prisma/pagina.css', 'paginas/pagina-1-prisma/pagina.js',
        'paginas/pagina-2-inversionistas/index.html', 'paginas/pagina-2-inversionistas/pagina.css', 'paginas/pagina-2-inversionistas/pagina.js',
        'paginas/pagina-3-por-que-prisma/index.html', 'paginas/pagina-3-por-que-prisma/pagina.css', 'paginas/pagina-3-por-que-prisma/pagina.js',
        'paginas/pagina-4-ecosistema-producto/index.html', 'paginas/pagina-4-ecosistema-producto/pagina.css', 'paginas/pagina-4-ecosistema-producto/pagina.js',
        'sistema-ui/css/prisma-ui.css', 'sistema-ui/js/prisma-ui.js', 'sistema-ui/catalogo/index.html',
        'assets/images/prisma-logo.png', 'README.md', 'TREE.md', 'BASELINE-MANIFEST.json',
        'extras/atlasfin/index.html', 'extras/atlasfin/MANIFEST.json',
    ]

    for relative in expected:
        ok = (root / relative).is_file()
        checks.append({'check': 'exists', 'path': relative, 'ok': ok})
        if not ok:
            errors.append(f'Falta {relative}')

    manifest_check = validate_files_manifest(root)
    checks.append({
        'check': 'files_manifest_integrity',
        'ok': manifest_check['ok'],
        'entry_count': manifest_check['entry_count'],
        'details': manifest_check['issues'],
    })
    if not manifest_check['ok']:
        errors.append('FILES_MANIFEST.json no representa exactamente las fuentes actuales')

    for html_path in root.rglob('*.html'):
        if not is_primary_scope(html_path):
            continue
        text = html_path.read_text(encoding='utf-8', errors='replace')
        inspector = Inspector()
        inspector.feed(text)
        duplicates = sorted({item for item in inspector.ids if inspector.ids.count(item) > 1})
        ok = not duplicates
        checks.append({'check': 'duplicate_ids', 'path': html_path.relative_to(root).as_posix(), 'ok': ok, 'details': duplicates})
        if not ok:
            errors.append(f'IDs duplicados en {html_path.relative_to(root)}')

        stale_comment = bool(re.search(r'(?m)^- (?:styles\\.css|app\\.js)\\s*=', text))
        checks.append({'check': 'current_page_comments', 'path': html_path.relative_to(root).as_posix(), 'ok': not stale_comment})
        if stale_comment:
            errors.append(f'Comentarios desactualizados en {html_path.relative_to(root)}')

        for script in inspector.scripts:
            src = script.get('src', '')
            if src.endswith('prisma-ui.js') or src.endswith('pagina.js') or src.endswith('catalogo.js'):
                module_ok = script.get('type') == 'module'
                checks.append({'check': 'es_module_script', 'path': html_path.relative_to(root).as_posix(), 'src': src, 'ok': module_ok})
                if not module_ok:
                    errors.append(f'Script ES sin type=module: {src} en {html_path.relative_to(root)}')

        for tag, ref in inspector.refs:
            if not is_local(ref):
                continue
            clean = ref.split('#', 1)[0].split('?', 1)[0]
            if not clean:
                continue
            ok = (html_path.parent / clean).resolve().exists()
            checks.append({'check': 'reference', 'from': html_path.relative_to(root).as_posix(), 'ref': ref, 'ok': ok})
            if not ok:
                errors.append(f'Referencia rota {ref} desde {html_path.relative_to(root)}')

    active = [
        path for path in root.rglob('*')
        if path.is_file() and is_primary_scope(path) and path.suffix.lower() in {'.html', '.css', '.js'}
    ]
    for path in active:
        text = path.read_text(encoding='utf-8', errors='replace')
        relative = path.relative_to(root).as_posix()
        validations = {
            'no_important': '!important' not in text,
            'no_embedded_base64': not ('data:image' in text and ';base64,' in text),
            'no_document_write': 'document.write' not in text,
        }
        for name, ok in validations.items():
            checks.append({'check': name, 'path': relative, 'ok': ok})
            if not ok:
                errors.append(f'{name} incumplido en {relative}')

    css_records = [record for record in collect_css_rules(root) if 'selectors' in record]
    exact_blocks = {}
    selector_extensions = {}
    for record in css_records:
        declaration_signature = tuple(
            (
                declaration['property'],
                declaration['value'],
                declaration['important'],
            )
            for declaration in record['declarations']
        )
        block_key = (
            record['file'],
            tuple(record['context']),
            tuple(record['selectors']),
            declaration_signature,
        )
        exact_blocks.setdefault(block_key, []).append(record)

        for selector in set(record['selectors']):
            extension_key = (
                record['file'],
                tuple(record['context']),
                selector,
            )
            selector_extensions.setdefault(extension_key, []).append({
                'line': record['line'],
                'column': record['column'],
                'selector_text': record['selector_text'],
            })

    duplicate_groups = []
    for (file_name, context, selectors, declarations), locations in exact_blocks.items():
        unique_locations = {}
        for location in locations:
            point = (location['line'], location['column'])
            unique_locations[point] = {
                'file': file_name,
                'line': location['line'],
                'column': location['column'],
                'selector_text': location['selector_text'],
            }
        if len(unique_locations) < 2:
            continue
        duplicate_groups.append({
            'file': file_name,
            'selectors': list(selectors),
            'context': list(context),
            'declarations': [
                {
                    'property': prop,
                    'value': value,
                    'important': important,
                }
                for prop, value, important in declarations
            ],
            'locations': list(unique_locations.values()),
        })

    cascade_extension_groups = sum(
        1
        for locations in selector_extensions.values()
        if len({
            (location['line'], location['column'], location['selector_text'])
            for location in locations
        }) > 1
    )

    duplicate_ok = not duplicate_groups
    checks.append({
        'check': 'no_unnecessary_duplicate_selectors',
        'ok': duplicate_ok,
        'details': duplicate_groups,
        'policy': {
            'dist_is_generated_projection': True,
            'css_modules_are_file_scoped': True,
            'repeated_selectors_with_different_blocks_are_cascade_extensions': True,
            'cascade_extension_groups_allowed': cascade_extension_groups,
            'exact_duplicate_blocks_rejected': len(duplicate_groups),
        },
    })
    if not duplicate_ok:
        errors.append(
            f'Existen {len(duplicate_groups)} bloques CSS exactamente duplicados '
            'dentro del mismo archivo y contexto'
        )

    node = shutil.which('node')
    if node:
        for js_path in root.rglob('*.js'):
            if not is_primary_scope(js_path):
                continue
            process = subprocess.run([node, '--check', str(js_path)], capture_output=True, text=True)
            ok = process.returncode == 0
            checks.append({'check': 'node_syntax', 'path': js_path.relative_to(root).as_posix(), 'ok': ok, 'stderr': process.stderr[-500:]})
            if not ok:
                errors.append(f'JS inválido {js_path.relative_to(root)}')

    status = 'PASS' if not errors else 'FAIL'
    result = {'status': status, 'checks': checks, 'warnings': warnings, 'errors': errors}
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
