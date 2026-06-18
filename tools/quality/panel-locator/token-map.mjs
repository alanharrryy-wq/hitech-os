const COLOR_LITERAL_RE = /(?:#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|hsla?\([^)]*\))/g;
const LENGTH_RE = /-?\d*\.?\d+(?:px|rem|em|vh|vw|dvh|dvw|%)/g;

export function buildTokenMap(rules){
  const tokens = new Map();
  const customProperties = new Map();
  const colorLiterals = [];
  const lengthLiterals = [];
  for(const rule of rules){
    for(const token of rule.tokens || []){
      if(!tokens.has(token)) tokens.set(token, []);
      tokens.get(token).push({ file: rule.file, line: rule.startLine, selector: rule.selector });
    }
    for(const prop of rule.customProperties || []){
      if(!customProperties.has(prop)) customProperties.set(prop, []);
      customProperties.get(prop).push({ file: rule.file, line: rule.startLine, selector: rule.selector });
    }
    for(const decl of rule.declarations || []){
      for(const match of String(decl.value || '').matchAll(COLOR_LITERAL_RE)) colorLiterals.push({ value: match[0], file: rule.file, line: decl.line, selector: rule.selector, property: decl.property });
      for(const match of String(decl.value || '').matchAll(LENGTH_RE)) lengthLiterals.push({ value: match[0], file: rule.file, line: decl.line, selector: rule.selector, property: decl.property });
    }
  }
  return {
    tokens: [...tokens.entries()].map(([token, usages]) => ({ token, count: usages.length, usages: usages.slice(0, 80) })).sort((a,b) => b.count - a.count || a.token.localeCompare(b.token)),
    customProperties: [...customProperties.entries()].map(([token, definitions]) => ({ token, count: definitions.length, definitions: definitions.slice(0, 80) })).sort((a,b) => b.count - a.count || a.token.localeCompare(b.token)),
    colorLiterals: colorLiterals.slice(0, 1000),
    lengthLiterals: lengthLiterals.slice(0, 1000),
  };
}
export function tokensForRule(rule){
  return { tokens: rule.tokens || [], customProperties: rule.customProperties || [], tokenCount: (rule.tokens || []).length + (rule.customProperties || []).length };
}
