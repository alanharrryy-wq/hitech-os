import path from 'node:path';
import { PANEL_LOCATOR_VERSION } from './constants.mjs';
import { parseCliArgs, resolveRepoRoot, loadPanelLocatorConfig, normalizeMode } from './config.mjs';
import { enumerateRepoFiles, readFileRecords, createScanSummary } from './scanner.mjs';
import { parseAllCss } from './css-parser.mjs';
import { resolveComponents } from './component-resolver.mjs';
import { applyVisualRisks } from './visual-risk-detector.mjs';
import { detectDuplicateSelectors, detectClassConflicts } from './duplicate-selector-detector.mjs';
import { attachOwnership } from './selector-ownership.mjs';
import { buildTokenMap } from './token-map.mjs';
import { groupRulesIntoPanels, topPanels } from './panel-grouper.mjs';
import { writeAllReports } from './reporters.mjs';
import { locateOperationalManual } from './manual-locator.mjs';
import { buildGitSnapshot } from './git-utils.mjs';
import { assertValidAnalysisModel } from './validation.mjs';
import { runPanelLocatorSelfTest } from './self-test.mjs';

export async function runPanelLocatorCli(argv){
  const args = parseCliArgs(argv);
  if(args.help || args.h){ printHelp(); return; }
  if(args.version){ console.log(PANEL_LOCATOR_VERSION); return; }
  if(args['self-test']){
    const result = runPanelLocatorSelfTest();
    console.log(`PANEL LOCATOR SELF TEST: ${result.status}`);
    console.log(`Rules: ${result.rules}`);
    console.log(`Panels: ${result.panels}`);
    console.log(`Duplicates: ${result.duplicates}`);
    return;
  }
  const repoRoot = resolveRepoRoot(args.repo);
  const config = loadPanelLocatorConfig(repoRoot, args.config);
  const mode = normalizeMode(args.mode || (args.tracked ? 'tracked' : args.staged ? 'staged' : 'repo-tree'));
  const surface = args.surface || 'all';
  const defaultOutBase = process.env.PANEL_LOCATOR_OUTPUT_DIR || process.env.PRISMA_OUTPUT_DIR || 'F:/descargasf';
  const safeStamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outDir = path.resolve(args['out-dir'] || path.join(defaultOutBase, `panel-locator-result-${safeStamp}`));
  const start = Date.now();

  const fileCandidates = enumerateRepoFiles(repoRoot, config, { mode, surface });
  const records = readFileRecords(fileCandidates);
  const scan = createScanSummary(records);
  let cssRules = parseAllCss(records);
  cssRules = applyVisualRisks(cssRules);
  const duplicateResult = detectDuplicateSelectors(cssRules);
  cssRules = duplicateResult.rules;
  const classConflicts = detectClassConflicts(cssRules);
  const componentResolution = resolveComponents(records);
  cssRules = attachOwnership(cssRules, componentResolution);
  const tokenMap = buildTokenMap(cssRules);
  const panels = topPanels(groupRulesIntoPanels(cssRules), Number(args['max-panels'] || 120));
  const manual = locateOperationalManual(repoRoot, config);
  const git = buildGitSnapshot(repoRoot);
  const summary = {
    status: 'PASS',
    version: PANEL_LOCATOR_VERSION,
    createdAt: new Date().toISOString(),
    durationMs: Date.now() - start,
    repoRoot,
    mode,
    surface,
    scan,
    cssRules: cssRules.length,
    panels: panels.length,
    duplicates: duplicateResult.duplicates.length,
    classConflicts: classConflicts.length,
    tokenCount: tokenMap.tokens.length,
    customPropertyCount: tokenMap.customProperties.length,
    manualExists: manual.exists,
    git,
  };
  const model = { records: records.map(({ text, ...rest }) => rest), cssRules, duplicates: duplicateResult.duplicates, classConflicts, componentResolution, tokenMap, panels, manual, summary, policy: { modifiedRepo: false, startedServers: false, killedProcesses: false, freedPorts: false, regeneratedPrisma: false, gitWrite: false } };
  assertValidAnalysisModel(model);
  writeAllReports(outDir, model);
  console.log('PANEL LOCATOR: PASS');
  console.log(`Reports: ${outDir}`);
  console.log(`Files scanned: ${scan.total}`);
  console.log(`Panels: ${panels.length}`);
  console.log(`CSS rules: ${cssRules.length}`);
}
export function printHelp(){
  console.log(`Panel Locator ${PANEL_LOCATOR_VERSION}\n\nUsage:\n  node tools/quality/panel-locator.mjs --surface tablet-pos --out-dir F:/descargasf/panel-locator-result\n\nOptions:\n  --repo <path>          Repo root. Defaults to git root.\n  --surface <id>         Surface filter: all, tablet-pos, tablet, pc, mobile, chart-lab, shared-ui.\n  --mode <mode>          repo-tree, tracked, staged.\n  --out-dir <path>       Report output directory.\n  --self-test            Run fixture self-test.\n  --help                 Show help.\n`);
}
