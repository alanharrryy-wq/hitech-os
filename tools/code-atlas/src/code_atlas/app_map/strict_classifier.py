# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ROUTE_BASENAMES = {"page", "route", "layout", "template", "default", "not-found", "error", "loading"}
ROUTE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}
STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less"}
COMPONENT_EXTENSIONS = {".tsx", ".jsx"}
SOURCE_EXTENSIONS = {".tsx", ".jsx", ".ts", ".js", ".mjs", ".mts", ".py", ".html"}
CONFIG_EXTENSIONS = {".json", ".jsonc", ".yaml", ".yml", ".toml", ".config", ".mjs", ".cjs"}
DOC_EXTENSIONS = {".md", ".mdx", ".txt", ".rst"}
SCAN_EXTENSIONS = SOURCE_EXTENSIONS | STYLE_EXTENSIONS | CONFIG_EXTENSIONS | DOC_EXTENSIONS

CONFIG_NAMES = {
    "package.json", "tsconfig.json", "tsconfig.base.json", "next.config.mjs", "next.config.js",
    "vite.config.ts", "tailwind.config.ts", "postcss.config.js", "wrangler.jsonc",
}

CSS_PROP_RE = re.compile(r"^[a-zA-Z-]+\s*:")
DECL_LEAK_RE = re.compile(r"(?:^|\n)\s*(?:--[\w-]+|[a-zA-Z-]+)\s*:")
CUSTOM_PROP_RE = re.compile(r"--[A-Za-z0-9_-]+")
TOKEN_DEF_RE = re.compile(r"(^|[;{\n\r])\s*(--[A-Za-z0-9_-]+)\s*:\s*([^;}{]+)", re.M)
TOKEN_REF_RE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)(?:\s*,\s*([^\)]+))?\)")


def classify_file(path: Path, app_root: Path | None = None) -> str:
    name = path.name
    suffix = path.suffix.lower()
    stem = path.stem
    rel = str(path).replace('\\', '/')
    if is_route_file(path, app_root):
        return "route"
    if suffix in STYLE_EXTENSIONS:
        return "style"
    if suffix in COMPONENT_EXTENSIONS:
        return "component"
    if suffix in DOC_EXTENSIONS:
        return "doc"
    if suffix in CONFIG_EXTENSIONS or name in CONFIG_NAMES:
        return "config"
    if suffix in SOURCE_EXTENSIONS:
        if stem[:1].isupper() or any(x in rel.lower() for x in ["/components/", "/widgets/", "/ui/"]):
            return "component_candidate"
        return "source"
    return "other"


def is_route_file(path: Path, app_root: Path | None = None) -> bool:
    suffix = path.suffix.lower()
    if suffix not in ROUTE_EXTENSIONS:
        return False
    stem = path.stem
    # route.ts, page.tsx, layout.tsx, etc. only. Never config, CSS, JSON or declarations.
    if stem not in ROUTE_BASENAMES:
        return False
    rel = str(path).replace('\\', '/')
    parts = rel.split('/')
    # Next.js app-router route files must live under an app directory.
    return "app" in parts


def derive_route(app_root: Path, path: Path) -> str:
    try:
        rel = path.resolve().relative_to(app_root.resolve()).as_posix()
    except Exception:
        rel = str(path).replace('\\', '/')
    parts = rel.split('/')
    if 'app' in parts:
        idx = len(parts) - 1 - parts[::-1].index('app')
        segs = parts[idx+1:-1]
    else:
        segs = parts[:-1]
    visible = []
    for seg in segs:
        if seg.startswith('(') and seg.endswith(')'):
            continue
        if seg.startswith('@'):
            continue
        visible.append(seg)
    route = '/' + '/'.join(visible)
    return route if route != '/' else '/'


def strip_css_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    quote = None
    esc = False
    for i in range(open_index, len(text)):
        ch = text[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
            continue
        if ch in ('"', "'"):
            quote = ch
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


def split_selector_list(prelude: str) -> list[str]:
    out, cur, depth, quote, esc = [], [], 0, None, False
    for ch in prelude:
        if quote:
            cur.append(ch)
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
            continue
        if ch in ('"', "'"):
            quote = ch
            cur.append(ch)
            continue
        if ch in '([':
            depth += 1
            cur.append(ch)
            continue
        if ch in ')]':
            depth = max(0, depth-1)
            cur.append(ch)
            continue
        if ch == ',' and depth == 0:
            item = ''.join(cur).strip()
            if item:
                out.append(item)
            cur = []
        else:
            cur.append(ch)
    item = ''.join(cur).strip()
    if item:
        out.append(item)
    return out


def is_valid_selector(selector: str) -> bool:
    s = ' '.join(selector.strip().split())
    if not s or len(s) > 240:
        return False
    if s.startswith('@'):
        return False
    if ';' in s or '{' in s or '}' in s:
        return False
    if DECL_LEAK_RE.search(selector):
        return False
    if selector.strip().startswith('--') or CUSTOM_PROP_RE.fullmatch(selector.strip()):
        return False
    if re.fullmatch(r"[0-9.\s%-]+", s):
        return False
    if CSS_PROP_RE.match(s):
        return False
    # A selector must contain selector grammar or a known element/tag, not arbitrary CSS values.
    known_tags = {"html", "body", "button", "a", "input", "select", "textarea", "svg", "path", "main", "section", "article", "header", "footer", "nav", "label", "form", "dialog", "canvas"}
    first = re.split(r"[\s>+~.#[:*]", s, 1)[0]
    if any(marker in s for marker in [".", "#", "[", ":", ">", "+", "~", "*"]):
        return True
    return first in known_tags


def extract_selectors(text: str) -> tuple[list[str], list[dict[str, Any]]]:
    css = strip_css_comments(text)
    selectors: list[str] = []
    quarantine: list[dict[str, Any]] = []

    def parse_region(region: str, context: str = "root"):
        pos = 0
        while True:
            open_idx = region.find('{', pos)
            if open_idx == -1:
                break
            prelude = region[pos:open_idx].strip()
            close_idx = find_matching_brace(region, open_idx)
            if close_idx == -1:
                if prelude:
                    quarantine.append({"candidate": prelude[:220], "reason": "unmatched_brace", "context": context})
                break
            body = region[open_idx+1:close_idx]
            # Clean prelude after previous block or semicolon noise.
            if '}' in prelude:
                prelude = prelude.rsplit('}', 1)[-1].strip()
            if prelude.startswith('@'):
                # Parse nested selectors inside @media/@supports/@container/@layer etc.
                parse_region(body, context=prelude.split(None, 1)[0])
            else:
                for item in split_selector_list(prelude):
                    if is_valid_selector(item):
                        selectors.append(' '.join(item.split()))
                    else:
                        quarantine.append({"candidate": item[:220], "reason": "not_selector_or_declaration_leak", "context": context})
            pos = close_idx + 1
    parse_region(css)
    # Deduplicate preserving order.
    seen, out = set(), []
    for s in selectors:
        if s not in seen:
            seen.add(s); out.append(s)
    return out, quarantine


def extract_tokens(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen = set()
    for m in TOKEN_DEF_RE.finditer(text):
        name = m.group(2)
        value = m.group(3).strip()
        key = ("definition", name, value)
        if key not in seen:
            seen.add(key)
            rows.append({"token": name, "kind": "definition", "defaultValue": value})
    for m in TOKEN_REF_RE.finditer(text):
        name = m.group(1)
        fallback = (m.group(2) or '').strip()
        key = ("reference", name, fallback)
        if key not in seen:
            seen.add(key)
            rows.append({"token": name, "kind": "reference", "defaultValue": fallback})
    return rows
