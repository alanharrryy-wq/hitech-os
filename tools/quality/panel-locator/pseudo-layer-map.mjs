export function buildPseudoLayerMap(rules){
  const layers = [];
  for(const rule of rules){
    if(!rule.pseudoLayers?.length) continue;
    layers.push({ file: rule.file, selector: rule.selector, line: rule.startLine, endLine: rule.endLine, pseudoLayers: rule.pseudoLayers, classes: rule.classes, risks: rule.risks || [], properties: rule.properties || [], humanName: rule.humanName, kind: rule.kind });
  }
  return layers.sort((a,b) => a.file.localeCompare(b.file) || a.line - b.line);
}
export function groupPseudoLayersByClass(layers){
  const out = new Map();
  for(const layer of layers){
    for(const cls of layer.classes || []){
      if(!out.has(cls)) out.set(cls, []);
      out.get(cls).push(layer);
    }
  }
  return [...out.entries()].map(([className, items]) => ({ className, count: items.length, items })).sort((a,b) => b.count - a.count || a.className.localeCompare(b.className));
}
