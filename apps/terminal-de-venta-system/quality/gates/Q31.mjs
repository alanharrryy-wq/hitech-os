import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { loadAutomationCatalog } from '../core/automation-catalog.mjs';

export async function run(ctx) {
  const catalog = loadAutomationCatalog(ctx.qualityRoot);
  const evidence = [createEvidence(ctx, 'Q31', 'automation_catalog', 'Automation improvement catalog validation', {
    ok: catalog.ok,
    total: catalog.total || 0,
    implemented: catalog.implemented || 0,
    active: catalog.active || 0,
    categories: catalog.categories || {},
    filePath: catalog.filePath,
    error: catalog.error
  })];
  const findings = [];
  if (!catalog.ok) {
    findings.push(finding({
      id: 'Q31_AUTOMATION_CATALOG_INVALID',
      severity: 'S1',
      layer: 'Quality',
      title: 'Automation catalog is not release-ready',
      detail: catalog.error || `Expected at least 100 unique improvements, found ${catalog.total || 0}.`,
      file: 'quality/automation/automation-improvements.json',
      recommendation: 'Restore the automation catalog with at least 100 unique implemented improvements.'
    }));
  }
  if ((catalog.implemented || 0) < 100) {
    findings.push(finding({
      id: 'Q31_AUTOMATION_IMPLEMENTED_UNDER_100',
      severity: 'S1',
      layer: 'Quality',
      title: 'Automation improvements under required threshold',
      detail: `Implemented improvements: ${catalog.implemented || 0}/100.`,
      file: 'quality/automation/automation-improvements.json',
      recommendation: 'Mark only real implemented improvements and keep the count at 100 or higher.'
    }));
  }
  return {
    gateId: 'Q31',
    title: 'Automation Improvement Catalog',
    status: findings.length ? 'BLOCKED' : 'READY',
    summary: `${catalog.implemented || 0}/${catalog.total || 0} automation improvements implemented across ${Object.keys(catalog.categories || {}).length} categories.`,
    findings,
    evidence
  };
}
