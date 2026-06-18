import { normalizeSelector } from './css-parser.mjs';

export function detectDuplicateSelectors(rules){
  const groups = new Map();
  for(const rule of rules){
    const key = normalizeSelector(rule.selector);
    if(!groups.has(key)) groups.set(key, []);
    groups.get(key).push({ file: rule.file, line: rule.startLine, endLine: rule.endLine, selector: rule.selector, properties: rule.properties });
  }
  const duplicates = [];
  for(const [selector, items] of groups){
    if(items.length > 1) duplicates.push({ selector, count: items.length, items });
  }
  duplicates.sort((a,b) => b.count - a.count || a.selector.localeCompare(b.selector));
  const duplicateMap = new Map();
  for(const dup of duplicates) duplicateMap.set(dup.selector, dup.count);
  const annotated = rules.map((rule) => ({ ...rule, duplicateCount: duplicateMap.get(normalizeSelector(rule.selector)) || 1 }));
  return { rules: annotated, duplicates };
}
export function detectClassConflicts(rules){
  const map = new Map();
  for(const rule of rules){
    for(const cls of rule.classes || []){
      if(!map.has(cls)) map.set(cls, []);
      map.get(cls).push(rule);
    }
  }
  const conflicts = [];
  for(const [className, hits] of map){
    const files = new Set(hits.map((h) => h.file));
    if(hits.length > 1 || files.size > 1){
      conflicts.push({ className, count: hits.length, files: [...files].sort(), selectors: hits.map((h) => ({ selector: h.selector, file: h.file, line: h.startLine })) });
    }
  }
  return conflicts.sort((a,b) => b.count - a.count || a.className.localeCompare(b.className));
}
