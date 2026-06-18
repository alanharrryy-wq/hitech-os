import { PANEL_KEYWORDS, HUMAN_PANEL_ALIASES } from './constants.mjs';
import { preview, extractLineWindow } from './fs-utils.mjs';

const CLASS_RE = /\.([A-Za-z_][A-Za-z0-9_-]*)/g;
const ID_RE = /#([A-Za-z_][A-Za-z0-9_-]*)/g;
const DATA_RE = /\[\s*(data-[A-Za-z0-9_-]+)(?:=[^\]]+)?\s*\]/g;
const TOKEN_RE = /var\(\s*(--[A-Za-z0-9_-]+)/g;
const CUSTOM_PROP_RE = /(--[A-Za-z0-9_-]+)\s*:/g;
const DECL_RE = /^\s*([*_-]?[A-Za-z-]+)\s*:\s*(.*?)\s*;?\s*$/;

export function stripCssComments(text){ return String(text || '').replace(/\/\*[\s\S]*?\*\//g, (m) => '\n'.repeat((m.match(/\n/g) || []).length)); }
export function collectMatches(regex, text){
  const out = [];
  let m;
  regex.lastIndex = 0;
  while((m = regex.exec(text))) out.push(m[1]);
  return [...new Set(out)].sort();
}
export function normalizeSelector(selector){ return String(selector || '').replace(/\s+/g, ' ').trim(); }
export function splitSelectorList(selector){
  const result = [];
  let buf = '';
  let depth = 0;
  for(const ch of selector){
    if(ch === '(' || ch === '[') depth++;
    if(ch === ')' || ch === ']') depth = Math.max(0, depth - 1);
    if(ch === ',' && depth === 0){ if(buf.trim()) result.push(buf.trim()); buf = ''; }
    else buf += ch;
  }
  if(buf.trim()) result.push(buf.trim());
  return result;
}
export function inferHumanPanelName(selector, classes = []){
  const lower = `${selector} ${classes.join(' ')}`.toLowerCase();
  for(const [needle, label] of HUMAN_PANEL_ALIASES){ if(lower.includes(needle)) return label; }
  return 'Unknown panel';
}
export function inferPanelKind(selector, classes = []){
  const lower = `${selector} ${classes.join(' ')}`.toLowerCase();
  for(const keyword of PANEL_KEYWORDS){ if(lower.includes(keyword)) return keyword; }
  return 'unknown';
}
export function parseDeclaration(line){
  const m = String(line || '').match(DECL_RE);
  if(!m) return null;
  return { property: m[1].trim(), value: m[2].trim() };
}
export function parseCssRules(record){
  const original = record.text || '';
  const text = stripCssComments(original);
  const lines = text.split(/\r?\n/);
  const rules = [];
  let pending = [];
  let current = null;
  let depth = 0;
  let atStack = [];
  for(let index = 0; index < lines.length; index++){
    const lineNumber = index + 1;
    const raw = lines[index];
    const trimmed = raw.trim();
    if(!trimmed) continue;
    if(!current){
      if(trimmed.startsWith('@') && trimmed.includes('{') && !trimmed.includes(';')){
        atStack.push({ name: normalizeSelector(trimmed.split('{')[0]), line: lineNumber });
      }
      pending.push(trimmed);
      if(trimmed.includes('{')){
        const joined = normalizeSelector(pending.join(' '));
        const selector = normalizeSelector(joined.split('{')[0]);
        pending = [];
        depth = (raw.match(/{/g) || []).length - (raw.match(/}/g) || []).length;
        if(selector && !selector.startsWith('@')){
          const classes = collectMatches(CLASS_RE, selector);
          current = {
            file: record.relativePath,
            surface: record.surface,
            selector,
            selectorParts: splitSelectorList(selector),
            startLine: lineNumber,
            endLine: lineNumber,
            classes,
            ids: collectMatches(ID_RE, selector),
            dataAttributes: collectMatches(DATA_RE, selector),
            tokens: collectMatches(TOKEN_RE, raw),
            customProperties: collectMatches(CUSTOM_PROP_RE, raw),
            declarations: [],
            declarationMap: {},
            pseudoLayers: [],
            atRules: [...atStack],
            lineWindow: extractLineWindow(original, lineNumber, 3),
            humanName: inferHumanPanelName(selector, classes),
            kind: inferPanelKind(selector, classes),
            rawPreview: preview(raw),
          };
          if(/::before\b/.test(selector)) current.pseudoLayers.push('before');
          if(/::after\b/.test(selector)) current.pseudoLayers.push('after');
          if(/:hover\b/.test(selector)) current.pseudoLayers.push('hover-state');
          if(/:focus(?:-visible)?\b/.test(selector)) current.pseudoLayers.push('focus-state');
          const afterOpen = raw.slice(raw.indexOf('{') + 1);
          const decl = parseDeclaration(afterOpen);
          if(decl){ current.declarations.push({ ...decl, line: lineNumber, text: preview(afterOpen) }); current.declarationMap[decl.property] = decl.value; }
          if(depth <= 0){ rules.push(finalizeRule(current)); current = null; depth = 0; }
        } else if(depth <= 0) {
          atStack = atStack.filter((r) => r.line !== lineNumber);
        }
      } else if(trimmed.endsWith(';') || trimmed.endsWith('}')) pending = [];
    } else {
      current.endLine = lineNumber;
      current.tokens = [...new Set([...current.tokens, ...collectMatches(TOKEN_RE, raw)])].sort();
      current.customProperties = [...new Set([...current.customProperties, ...collectMatches(CUSTOM_PROP_RE, raw)])].sort();
      const decl = parseDeclaration(trimmed);
      if(decl){ current.declarations.push({ ...decl, line: lineNumber, text: preview(trimmed) }); current.declarationMap[decl.property] = decl.value; }
      depth += (raw.match(/{/g) || []).length - (raw.match(/}/g) || []).length;
      if(depth <= 0){ rules.push(finalizeRule(current)); current = null; depth = 0; }
    }
    if(trimmed === '}' && atStack.length) atStack.pop();
  }
  return rules;
}
export function finalizeRule(rule){
  const properties = rule.declarations.map((d) => d.property);
  return {
    ...rule,
    lineSpan: Math.max(1, rule.endLine - rule.startLine + 1),
    properties,
    propertyCount: properties.length,
    tokenCount: rule.tokens.length,
    classCount: rule.classes.length,
    selectorSpecificityHint: computeSpecificityHint(rule.selector),
  };
}
export function computeSpecificityHint(selector){
  const ids = (selector.match(/#[A-Za-z_][A-Za-z0-9_-]*/g) || []).length;
  const classes = (selector.match(/\.[A-Za-z_][A-Za-z0-9_-]*/g) || []).length + (selector.match(/\[[^\]]+\]/g) || []).length + (selector.match(/:[A-Za-z_-]+/g) || []).length;
  const elements = selector.replace(/[#.:[\](),>+~*='"-]/g, ' ').split(/\s+/).filter(Boolean).length;
  return { ids, classes, elements, score: ids * 100 + classes * 10 + elements };
}
export function parseAllCss(records){
  const out = [];
  for(const record of records.filter((r) => r.kind === 'style')) out.push(...parseCssRules(record));
  return out;
}
