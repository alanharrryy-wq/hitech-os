import { groupStyleUsagesByClass } from './component-resolver.mjs';

export function attachOwnership(rules, componentResolution){
  const usageByClass = groupStyleUsagesByClass(componentResolution.styleUsages || []);
  return rules.map((rule) => {
    const usages = [];
    for(const cls of rule.classes || []) usages.push(...(usageByClass.get(cls) || []));
    const componentCounts = new Map();
    for(const usage of usages) componentCounts.set(usage.component, (componentCounts.get(usage.component) || 0) + 1);
    const owners = [...componentCounts.entries()].map(([component, count]) => ({ component, count })).sort((a,b) => b.count - a.count || a.component.localeCompare(b.component));
    const primaryOwner = owners[0]?.component || 'UnknownComponent';
    const ownershipScore = usages.length * 3 + owners.length + (rule.humanName !== 'Unknown panel' ? 5 : 0) + (rule.kind !== 'unknown' ? 3 : 0);
    return { ...rule, usages: usages.slice(0, 60), usageCount: usages.length, owners, primaryOwner, ownershipScore };
  });
}
export function buildOwnerMap(rules){
  const map = new Map();
  for(const rule of rules){
    const key = `${rule.file}::${rule.primaryOwner}`;
    if(!map.has(key)) map.set(key, { file: rule.file, component: rule.primaryOwner, selectors: [], usageCount: 0, riskScore: 0 });
    const entry = map.get(key);
    entry.selectors.push({ selector: rule.selector, line: rule.startLine, kind: rule.kind, humanName: rule.humanName, classes: rule.classes, risks: rule.risks, usageCount: rule.usageCount });
    entry.usageCount += rule.usageCount || 0;
    entry.riskScore += rule.riskScore || 0;
  }
  return [...map.values()].sort((a,b) => b.usageCount - a.usageCount || b.riskScore - a.riskScore || a.file.localeCompare(b.file));
}
export function chooseCanonicalSelector(panel){
  const sorted = [...(panel.rules || [])].sort((a,b) => (b.usageCount || 0) - (a.usageCount || 0) || (b.ownershipScore || 0) - (a.ownershipScore || 0) || (a.startLine || 0) - (b.startLine || 0));
  return sorted[0] || null;
}
