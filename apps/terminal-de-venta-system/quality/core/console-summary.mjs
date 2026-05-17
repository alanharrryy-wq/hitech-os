function trim(text, max = 180) {
  const value = String(text || '').replace(/\s+/g, ' ').trim();
  return value.length > max ? `${value.slice(0, max - 1)}…` : value;
}

function printFindingList(label, findings, maxItems = 5) {
  if (!findings?.length) return;
  console.log(`${label}:`);
  findings.slice(0, maxItems).forEach((finding, index) => {
    console.log(`  ${index + 1}. ${finding.id || finding.title || 'finding'} - ${trim(finding.detail || finding.recommendation || finding.title)}`);
  });
  if (findings.length > maxItems) console.log(`  ... ${findings.length - maxItems} more. See QUALITY_BLOCKERS.md / QUALITY_WARNINGS.md in the run dir.`);
}

export function printSummary(ctx, decision) {
  console.log('');
  console.log('=== PRISMA QUALITY OS ===');
  console.log(`Profile: ${ctx.profile}`);
  console.log(`Decision: ${decision.decision}`);
  console.log(`Blockers: ${decision.blockerCount}`);
  console.log(`Warnings: ${decision.warningCount}`);
  console.log(`Run dir: ${ctx.runDir}`);
  printFindingList('Top blockers', decision.blockers || []);
  printFindingList('Top warnings', decision.warnings || [], 3);
  console.log('');
}
