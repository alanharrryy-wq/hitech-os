import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs';
import { parseCssRules } from './css-parser.mjs';
import { resolveComponents } from './component-resolver.mjs';
import { applyVisualRisks } from './visual-risk-detector.mjs';
import { detectDuplicateSelectors } from './duplicate-selector-detector.mjs';
import { attachOwnership } from './selector-ownership.mjs';
import { groupRulesIntoPanels } from './panel-grouper.mjs';
import { assertValidAnalysisModel } from './validation.mjs';

export function createFixtureRecords(){
  const css = `
.ticketPanel {
  display: grid;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0,0,0,.12);
  color: var(--prisma-ink);
}
.ticketPanel::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.paymentPanel { position: fixed; z-index: 900; }
.paymentPanel { backdrop-filter: blur(12px); }
`;
  const tsx = `
import styles from './pos.module.css';
export function TicketPanel(){ return <section className={styles.ticketPanel}>Ticket</section>; }
export const PaymentPanel = () => <aside className={styles['paymentPanel']}>Pay</aside>;
`;
  return [
    { kind: 'style', relativePath: 'products/tablet/app/components/pos/pos.module.css', file: 'products/tablet/app/components/pos/pos.module.css', text: css, surface: { id: 'tablet-pos', label: 'Tablet POS' } },
    { kind: 'code', relativePath: 'products/tablet/app/components/pos/panels.tsx', file: 'products/tablet/app/components/pos/panels.tsx', text: tsx, surface: { id: 'tablet-pos', label: 'Tablet POS' } },
  ];
}
export function runPanelLocatorSelfTest(){
  const records = createFixtureRecords();
  let rules = records.filter((r) => r.kind === 'style').flatMap((record) => parseCssRules(record));
  rules = applyVisualRisks(rules);
  const dup = detectDuplicateSelectors(rules);
  rules = dup.rules;
  const componentResolution = resolveComponents(records);
  rules = attachOwnership(rules, componentResolution);
  const panels = groupRulesIntoPanels(rules);
  const model = { records, cssRules: rules, duplicates: dup.duplicates, panels, componentResolution, manual: { exists: false }, summary: { status: 'PASS', repoRoot: 'fixture', mode: 'self-test', surface: 'tablet-pos', scan: { total: records.length } }, policy: { modifiedRepo: false, startedServers: false, killedProcesses: false, freedPorts: false, regeneratedPrisma: false, gitWrite: false } };
  assertValidAnalysisModel(model);
  if(rules.length < 3) throw new Error('expected fixture css rules');
  if(!panels.length) throw new Error('expected fixture panels');
  if(!rules.some((r) => r.primaryOwner === 'TicketPanel')) throw new Error('expected TicketPanel ownership');
  if(!dup.duplicates.length) throw new Error('expected duplicate payment selector');
  return { status: 'PASS', rules: rules.length, panels: panels.length, duplicates: dup.duplicates.length };
}
