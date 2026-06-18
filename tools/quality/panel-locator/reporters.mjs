import path from 'node:path';
import { OUTPUT_FILES, PANEL_LOCATOR_VERSION } from './constants.mjs';
import { ensureDirSync, writeTextSync, writeJsonSync, preview } from './fs-utils.mjs';
import { summarizeRisks, topRiskRules } from './visual-risk-detector.mjs';
import { buildOwnerMap } from './selector-ownership.mjs';
import { buildPseudoLayerMap, groupPseudoLayersByClass } from './pseudo-layer-map.mjs';

export function writeAllReports(outDir, model){
  ensureDirSync(outDir);
  writeTextSync(path.join(outDir, OUTPUT_FILES.report), renderMainReport(model));
  writeJsonSync(path.join(outDir, OUTPUT_FILES.selectorMap), renderSelectorMap(model));
  writeTextSync(path.join(outDir, OUTPUT_FILES.surfaceMap), renderSurfaceComponentMap(model));
  writeJsonSync(path.join(outDir, OUTPUT_FILES.ownerMap), renderOwnerMap(model));
  writeJsonSync(path.join(outDir, OUTPUT_FILES.pseudoMap), renderPseudoMap(model));
  writeTextSync(path.join(outDir, OUTPUT_FILES.riskReport), renderRiskReport(model));
  writeTextSync(path.join(outDir, OUTPUT_FILES.duplicateReport), renderDuplicateReport(model));
  writeTextSync(path.join(outDir, OUTPUT_FILES.guide), renderPanelChangeGuide(model));
  writeJsonSync(path.join(outDir, OUTPUT_FILES.summary), model.summary);
  writeTextSync(path.join(outDir, OUTPUT_FILES.continuation), renderContinuation(model));
}
export function renderMainReport(model){
  const lines = [];
  lines.push('# PANEL LOCATOR REPORT');
  lines.push('');
  lines.push(`- Version: ${PANEL_LOCATOR_VERSION}`);
  lines.push(`- Status: ${model.summary.status}`);
  lines.push(`- Repo: \`${model.summary.repoRoot}\``);
  lines.push(`- Mode: \`${model.summary.mode}\``);
  lines.push(`- Surface filter: \`${model.summary.surface}\``);
  lines.push(`- Files scanned: \`${model.summary.scan.total}\``);
  lines.push(`- CSS rules: \`${model.cssRules.length}\``);
  lines.push(`- Panels detected: \`${model.panels.length}\``);
  lines.push(`- Manual: ${model.manual.exists ? 'found' : 'not found'}`);
  lines.push('');
  lines.push('## Top panels');
  lines.push('| # | Panel | Canonical selector | Owner | Files | Usages | Risks | Pseudo |');
  lines.push('|---:|---|---|---|---:|---:|---:|---|');
  model.panels.slice(0, 40).forEach((panel, index) => {
    const c = panel.canonicalSelector;
    lines.push(`| ${index + 1} | ${panel.label} | ${c ? `\`${preview(c.selector, 70)}\`` : 'n/a'} | ${c?.owner || 'unknown'} | ${panel.files.length} | ${panel.usageCount} | ${panel.riskCount} | ${panel.pseudoLayers.join(', ') || 'none'} |`);
  });
  lines.push('');
  lines.push('## Safe edit route');
  lines.push('1. Pick panel by human label.');
  lines.push('2. Open canonical selector file and line.');
  lines.push('3. Inspect owner component and linked CSS module.');
  lines.push('4. Edit canonical selector or consolidate duplicate owners.');
  lines.push('5. Run `pnpm run verify:zero-important`.');
  lines.push('6. For real visual work, run fresh Authority Mesh for the exact task.');
  lines.push('');
  return lines.join('\n');
}
export function renderSelectorMap(model){
  return {
    summary: model.summary,
    selectors: model.cssRules.map((rule) => ({ file: rule.file, line: rule.startLine, endLine: rule.endLine, selector: rule.selector, surface: rule.surface, classes: rule.classes, humanName: rule.humanName, kind: rule.kind, owner: rule.primaryOwner, usageCount: rule.usageCount, riskScore: rule.riskScore, risks: rule.risks, duplicateCount: rule.duplicateCount, pseudoLayers: rule.pseudoLayers, tokens: rule.tokens })),
    panels: model.panels.map((panel) => ({ key: panel.key, label: panel.label, canonicalSelector: panel.canonicalSelector, files: panel.files, owners: panel.owners, classes: panel.classes, usageCount: panel.usageCount, riskScore: panel.riskScore, pseudoLayers: panel.pseudoLayers, tokens: panel.tokens }))
  };
}
export function renderSurfaceComponentMap(model){
  const lines = ['# SURFACE COMPONENT MAP', ''];
  const bySurface = new Map();
  for(const file of model.componentResolution.componentFiles){
    const id = file.surface?.id || 'unknown';
    if(!bySurface.has(id)) bySurface.set(id, []);
    bySurface.get(id).push(file);
  }
  for(const [surface, files] of [...bySurface.entries()].sort()){
    lines.push(`## ${surface}`);
    for(const file of files.slice(0, 300)) lines.push(`- \`${file.file}\`: ${file.components.map((c) => c.name).join(', ') || 'no components'} | style refs: ${file.styleUsageCount}`);
    lines.push('');
  }
  return lines.join('\n');
}
export function renderOwnerMap(model){ return { summary: model.summary, owners: buildOwnerMap(model.cssRules), componentFiles: model.componentResolution.componentFiles, styleUsages: model.componentResolution.styleUsages }; }
export function renderPseudoMap(model){ const layers = buildPseudoLayerMap(model.cssRules); return { summary: model.summary, layers, byClass: groupPseudoLayersByClass(layers) }; }
export function renderRiskReport(model){
  const lines = ['# VISUAL RISK REPORT', '', '## Summary', ''];
  const summary = summarizeRisks(model.cssRules);
  for(const [id,count] of Object.entries(summary.byId)) lines.push(`- ${id}: ${count}`);
  lines.push('', '## Top risk selectors', '');
  for(const rule of topRiskRules(model.cssRules, 120)){
    lines.push(`- \`${rule.file}:${rule.startLine}\` \`${preview(rule.selector, 140)}\``);
    lines.push(`  - owner: ${rule.primaryOwner}`);
    lines.push(`  - score: ${rule.riskScore}`);
    lines.push(`  - risks: ${(rule.risks || []).map((r) => r.id).join(', ') || 'none'}`);
  }
  return lines.join('\n');
}
export function renderDuplicateReport(model){
  const lines = ['# DUPLICATE SELECTOR REPORT', ''];
  for(const dup of model.duplicates.slice(0, 200)){
    lines.push(`- ${dup.count}x \`${preview(dup.selector, 160)}\``);
    for(const item of dup.items.slice(0, 12)) lines.push(`  - \`${item.file}:${item.line}\``);
  }
  return lines.join('\n');
}
export function renderPanelChangeGuide(model){
  const lines = ['# PANEL CHANGE GUIDE', '', 'No agent-specific prompts are generated by this tool. This is a neutral engineering guide.', ''];
  for(const panel of model.panels.slice(0, 30)){
    const c = panel.canonicalSelector;
    lines.push(`## ${panel.label}`);
    lines.push(`- Key: \`${panel.key}\``);
    lines.push(`- Files: ${panel.files.map((f) => `\`${f}\``).join(', ')}`);
    lines.push(`- Owners: ${panel.owners.join(', ') || 'unknown'}`);
    lines.push(`- Canonical selector: ${c ? `\`${c.file}:${c.line}\` \`${preview(c.selector, 140)}\`` : 'unknown'}`);
    lines.push(`- Pseudo layers: ${panel.pseudoLayers.join(', ') || 'none'}`);
    lines.push(`- Risks: ${panel.risks.slice(0, 12).map((r) => r.id).join(', ') || 'none'}`);
    lines.push('- Safe path: edit the canonical selector first, consolidate duplicates if present, then run the zero-priority gate.');
    lines.push('- Exclusions: do not touch unrelated surfaces unless a fresh Authority Mesh authorizes them.');
    lines.push('');
  }
  return lines.join('\n');
}
export function renderContinuation(model){
  return `# CONTINUATION\n\nPanel Locator completed.\n\nStatus: ${model.summary.status}\nRepo: ${model.summary.repoRoot}\nPanels: ${model.panels.length}\nCSS rules: ${model.cssRules.length}\n\nNext: choose a panel from PANEL_LOCATOR_REPORT.md and run fresh Authority Mesh before any visual patch.\n`;
}
