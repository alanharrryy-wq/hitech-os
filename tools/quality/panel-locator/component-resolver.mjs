import { preview, extractLineWindow } from './fs-utils.mjs';

const STYLE_IMPORT_RE = /import\s+([A-Za-z_$][\w$]*)\s+from\s+['"]([^'"]+\.module\.(?:css|scss))['"]/g;
const STYLE_DOT_RE = /([A-Za-z_$][\w$]*)\.([A-Za-z_][A-Za-z0-9_]*)/g;
const STYLE_BRACKET_RE = /([A-Za-z_$][\w$]*)\[['"]([^'"]+)['"]\]/g;
const FUNCTION_RE = /\bexport\s+default\s+function\s+([A-Z][A-Za-z0-9_]*)\b|\bexport\s+function\s+([A-Z][A-Za-z0-9_]*)\b|\bfunction\s+([A-Z][A-Za-z0-9_]*)\b|\bconst\s+([A-Z][A-Za-z0-9_]*)\s*=\s*(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>|\bconst\s+([A-Z][A-Za-z0-9_]*)\s*=\s*(?:memo|forwardRef)\b/g;
const JSX_TAG_RE = /<([A-Z][A-Za-z0-9_]*)(?:\s|>|\/)/g;

export function findStyleImports(text){
  const imports = [];
  let m;
  STYLE_IMPORT_RE.lastIndex = 0;
  while((m = STYLE_IMPORT_RE.exec(text))) imports.push({ local: m[1], source: m[2], index: m.index });
  return imports;
}
export function findComponentDeclarations(text){
  const components = [];
  let m;
  FUNCTION_RE.lastIndex = 0;
  const lineStarts = buildLineStarts(text);
  while((m = FUNCTION_RE.exec(text))){
    const name = m[1] || m[2] || m[3] || m[4] || m[5];
    const line = offsetToLine(lineStarts, m.index);
    components.push({ name, line, offset: m.index });
  }
  return components.sort((a,b) => a.offset - b.offset);
}
export function buildLineStarts(text){
  const starts = [0];
  for(let i=0;i<text.length;i++) if(text[i] === '\n') starts.push(i+1);
  return starts;
}
export function offsetToLine(starts, offset){
  let lo = 0, hi = starts.length - 1;
  while(lo <= hi){
    const mid = (lo + hi) >> 1;
    if(starts[mid] <= offset) lo = mid + 1; else hi = mid - 1;
  }
  return Math.max(1, hi + 1);
}
export function nearestComponent(components, line){
  let found = null;
  for(const comp of components){ if(comp.line <= line) found = comp; else break; }
  return found ? found.name : 'UnknownComponent';
}
export function resolveComponents(records){
  const styleUsages = [];
  const componentFiles = [];
  for(const record of records.filter((r) => r.kind === 'code')){
    const text = record.text || '';
    const imports = findStyleImports(text);
    const locals = new Set(imports.map((item) => item.local));
    const components = findComponentDeclarations(text);
    const lineStarts = buildLineStarts(text);
    const lines = text.split(/\r?\n/);
    const jsxTags = [];
    let tag;
    JSX_TAG_RE.lastIndex = 0;
    while((tag = JSX_TAG_RE.exec(text))) jsxTags.push({ name: tag[1], line: offsetToLine(lineStarts, tag.index) });
    let m;
    STYLE_DOT_RE.lastIndex = 0;
    while((m = STYLE_DOT_RE.exec(text))){
      if(!locals.has(m[1])) continue;
      const line = offsetToLine(lineStarts, m.index);
      styleUsages.push({ file: record.relativePath, line, styleLocal: m[1], className: m[2], component: nearestComponent(components, line), sample: preview(lines[line-1] || ''), window: extractLineWindow(text, line, 2) });
    }
    STYLE_BRACKET_RE.lastIndex = 0;
    while((m = STYLE_BRACKET_RE.exec(text))){
      if(!locals.has(m[1])) continue;
      const line = offsetToLine(lineStarts, m.index);
      styleUsages.push({ file: record.relativePath, line, styleLocal: m[1], className: m[2], component: nearestComponent(components, line), sample: preview(lines[line-1] || ''), window: extractLineWindow(text, line, 2) });
    }
    componentFiles.push({ file: record.relativePath, surface: record.surface, imports, components, jsxTags: jsxTags.slice(0, 200), styleUsageCount: styleUsages.filter((u) => u.file === record.relativePath).length });
  }
  return { styleUsages, componentFiles };
}
export function groupStyleUsagesByClass(styleUsages){
  const map = new Map();
  for(const usage of styleUsages){
    const key = usage.className;
    if(!map.has(key)) map.set(key, []);
    map.get(key).push(usage);
  }
  return map;
}
export function createComponentSummary(componentFiles){
  return componentFiles.map((file) => ({ file: file.file, surface: file.surface, components: file.components.map((c) => c.name), styleUsageCount: file.styleUsageCount }));
}
