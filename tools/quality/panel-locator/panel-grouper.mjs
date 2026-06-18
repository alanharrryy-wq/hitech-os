import { PANEL_KEYWORDS } from './constants.mjs';
import { chooseCanonicalSelector } from './selector-ownership.mjs';

export function classStem(className){
  const raw = String(className || '').replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
  const parts = raw.split(/[-_]+/).filter(Boolean);
  const meaningful = parts.filter((part) => !['pos','prisma','tablet','premium','visual','ui','root','base','item'].includes(part));
  return meaningful.slice(0, 3).join('-') || parts.slice(0, 2).join('-') || raw;
}
export function inferPanelKey(rule){
  if(rule.humanName && rule.humanName !== 'Unknown panel') return rule.humanName.toLowerCase().replace(/\s+/g, '-');
  for(const cls of rule.classes || []){
    const stem = classStem(cls);
    for(const keyword of PANEL_KEYWORDS){ if(stem.includes(keyword)) return keyword; }
    if(stem) return stem;
  }
  return `${rule.file}:${rule.startLine}`;
}
export function groupRulesIntoPanels(rules){
  const map = new Map();
  for(const rule of rules){
    const key = inferPanelKey(rule);
    if(!map.has(key)) map.set(key, { key, label: rule.humanName !== 'Unknown panel' ? rule.humanName : key, surface: rule.surface, rules: [], files: new Set(), classes: new Set(), owners: new Set(), risks: [], tokens: new Set(), pseudoLayers: new Set() });
    const panel = map.get(key);
    panel.rules.push(rule);
    panel.files.add(rule.file);
    for(const cls of rule.classes || []) panel.classes.add(cls);
    for(const owner of rule.owners || []) panel.owners.add(owner.component);
    for(const risk of rule.risks || []) panel.risks.push({ ...risk, file: rule.file, selector: rule.selector });
    for(const token of rule.tokens || []) panel.tokens.add(token);
    for(const layer of rule.pseudoLayers || []) panel.pseudoLayers.add(layer);
  }
  const panels = [...map.values()].map((panel) => {
    const canonical = chooseCanonicalSelector(panel);
    const riskScore = panel.risks.reduce((sum, risk) => sum + Number(risk.severity || 0), 0);
    return {
      key: panel.key,
      label: panel.label,
      surface: panel.surface,
      files: [...panel.files].sort(),
      classes: [...panel.classes].sort(),
      owners: [...panel.owners].sort(),
      rules: panel.rules,
      selectorCount: panel.rules.length,
      usageCount: panel.rules.reduce((sum, rule) => sum + Number(rule.usageCount || 0), 0),
      riskCount: panel.risks.length,
      riskScore,
      risks: panel.risks.slice(0, 120),
      tokens: [...panel.tokens].sort(),
      pseudoLayers: [...panel.pseudoLayers].sort(),
      canonicalSelector: canonical ? { file: canonical.file, selector: canonical.selector, line: canonical.startLine, endLine: canonical.endLine, owner: canonical.primaryOwner, classes: canonical.classes } : null,
    };
  });
  return panels.sort((a,b) => b.usageCount - a.usageCount || b.riskScore - a.riskScore || b.selectorCount - a.selectorCount || a.label.localeCompare(b.label));
}
export function topPanels(panels, limit = 80){ return panels.slice(0, limit); }
