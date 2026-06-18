import { createRiskRegexes } from './constants.mjs';
import { preview } from './fs-utils.mjs';

export function detectRisksForRule(rule){
  const riskRules = createRiskRegexes();
  const risks = [];
  for(const decl of rule.declarations || []){
    const text = `${decl.property}: ${decl.value}`;
    for(const risk of riskRules){
      if(risk.regex.test(text)){
        risks.push({ id: risk.id, severity: risk.severity, category: risk.category, message: risk.message, line: decl.line, property: decl.property, sample: preview(text) });
      }
    }
  }
  if(rule.pseudoLayers?.length) risks.push({ id: 'pseudo-layer', severity: 3, category: 'layering', message: 'decorative or state layer needs owner verification', line: rule.startLine, sample: rule.selector });
  if(rule.selectorSpecificityHint?.score >= 80) risks.push({ id: 'specificity-high', severity: 5, category: 'cascade', message: 'high selector specificity can complicate safe edits', line: rule.startLine, sample: rule.selector });
  return risks;
}
export function applyVisualRisks(rules){
  return rules.map((rule) => {
    const risks = detectRisksForRule(rule);
    const riskScore = risks.reduce((sum, item) => sum + Number(item.severity || 0), 0);
    return { ...rule, risks, riskScore };
  });
}
export function summarizeRisks(rules){
  const byId = new Map();
  const byFile = new Map();
  for(const rule of rules){
    for(const risk of rule.risks || []){
      byId.set(risk.id, (byId.get(risk.id) || 0) + 1);
      byFile.set(rule.file, (byFile.get(rule.file) || 0) + 1);
    }
  }
  return { byId: Object.fromEntries([...byId.entries()].sort()), byFile: Object.fromEntries([...byFile.entries()].sort()) };
}
export function topRiskRules(rules, limit = 80){
  return [...rules].filter((r) => r.risks?.length).sort((a,b) => (b.riskScore || 0) - (a.riskScore || 0) || a.file.localeCompare(b.file) || a.startLine - b.startLine).slice(0, limit);
}
