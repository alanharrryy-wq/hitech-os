from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import tinycss2


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


def collect_selectors(root):
    records = []

    def walk(items, path, parents=None, context=()):
        for item in items:
            if item.type == 'qualified-rule':
                raw = tinycss2.serialize(item.prelude).strip()
                selectors = combine_selectors(parents, raw)
                for selector in selectors:
                    records.append({
                        'selector': re.sub(r'\\s+', ' ', selector).strip(),
                        'file': path.relative_to(root).as_posix(),
                        'context': list(context),
                        'line': item.source_line,
                    })
                inner = tinycss2.parse_blocks_contents(item.content, skip_whitespace=True, skip_comments=True)
                walk(inner, path, selectors, context)
            elif item.type == 'at-rule' and item.content is not None:
                prelude = tinycss2.serialize(item.prelude).strip()
                label = f'@{item.at_keyword} {prelude}'.strip()
                inner = tinycss2.parse_blocks_contents(item.content, skip_whitespace=True, skip_comments=True)
                walk(inner, path, parents, context + (label,))

    for path in root.rglob('*.css'):
        if 'backup_original' in path.parts:
            continue
        rules = tinycss2.parse_stylesheet(path.read_text(encoding='utf-8'), skip_whitespace=True, skip_comments=True)
        parse_errors = [rule for rule in rules if rule.type == 'error']
        if parse_errors:
            records.append({'css_parse_errors': [error.message for error in parse_errors], 'file': path.relative_to(root).as_posix()})
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
        'sistema-ui/css/prisma-ui.css', 'sistema-ui/js/prisma-ui.js', 'sistema-ui/catalogo/index.html',
        'assets/images/prisma-logo.svg', 'README.md', 'TREE.md', 'BASELINE-MANIFEST.json',
    ]

    for relative in expected:
        ok = (root / relative).is_file()
        checks.append({'check': 'exists', 'path': relative, 'ok': ok})
        if not ok:
            errors.append(f'Falta {relative}')

    for html_path in root.rglob('*.html'):
        if 'backup_original' in html_path.parts:
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
        if path.is_file() and 'backup_original' not in path.parts and path.suffix.lower() in {'.html', '.css', '.js'}
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

    selector_records = [record for record in collect_selectors(root) if 'selector' in record]
    exact = {}
    for record in selector_records:
        key = (record['selector'], tuple(record['context']))
        exact.setdefault(key, []).append(record)

    # :root is intentionally partitioned across token-domain files.
    allowed_token_roots = {
        record['file'] for record in exact.get((':root', ()), [])
        if record['file'].startswith('sistema-ui/css/tokens/')
    }
    duplicate_groups = []
    for (selector, context), locations in exact.items():
        if len(locations) < 2:
            continue
        if selector == ':root' and len(allowed_token_roots) == len(locations):
            continue
        duplicate_groups.append({'selector': selector, 'context': list(context), 'locations': locations})

    duplicate_ok = not duplicate_groups
    checks.append({'check': 'no_unnecessary_duplicate_selectors', 'ok': duplicate_ok, 'details': duplicate_groups})
    if not duplicate_ok:
        errors.append(f'Existen {len(duplicate_groups)} grupos de selectores duplicados no justificados')

    node = shutil.which('node')
    if node:
        for js_path in root.rglob('*.js'):
            if 'backup_original' in js_path.parts:
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
