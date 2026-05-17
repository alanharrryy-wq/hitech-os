import fs from 'node:fs';
import path from 'node:path';

export function loadAutomationCatalog(qualityRoot) {
  const filePath = path.join(qualityRoot, 'automation', 'automation-improvements.json');
  if (!fs.existsSync(filePath)) {
    return { ok: false, filePath, improvements: [], error: 'automation catalog not found' };
  }
  try {
    const catalog = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const improvements = Array.isArray(catalog.improvements) ? catalog.improvements : [];
    const ids = new Set(improvements.map((item) => item.id));
    const implemented = improvements.filter((item) => item.status === 'implemented');
    const active = improvements.filter((item) => item.enabled !== false);
    const categories = {};
    for (const item of improvements) categories[item.category || 'uncategorized'] = (categories[item.category || 'uncategorized'] || 0) + 1;
    return {
      ok: improvements.length >= 100 && ids.size === improvements.length,
      filePath,
      schemaVersion: catalog.schemaVersion || '1.0',
      generatedAt: catalog.generatedAt || null,
      total: improvements.length,
      implemented: implemented.length,
      active: active.length,
      categories,
      improvements,
      error: null
    };
  } catch (error) {
    return { ok: false, filePath, improvements: [], error: error?.message || String(error) };
  }
}
