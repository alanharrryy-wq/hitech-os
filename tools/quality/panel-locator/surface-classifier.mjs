import { DEFAULT_SURFACE_RULES } from './constants.mjs';
import { normalizePath } from './fs-utils.mjs';

export function classifySurface(filePath, rules = DEFAULT_SURFACE_RULES){
  const p = normalizePath(filePath).toLowerCase();
  const matches = [];
  for(const rule of rules){
    for(const pattern of rule.patterns || []){
      const q = normalizePath(pattern).toLowerCase();
      if(p.includes(q) || p.endsWith(q)) matches.push({ id: rule.id, label: rule.label, pattern });
    }
  }
  if(matches.length){
    matches.sort((a,b) => String(b.pattern).length - String(a.pattern).length);
    return matches[0];
  }
  return { id: 'unknown', label: 'Unknown', pattern: '' };
}
export function surfaceMatchesFilter(filePath, surfaceId, rules = DEFAULT_SURFACE_RULES){
  if(!surfaceId || surfaceId === 'all') return true;
  const surface = classifySurface(filePath, rules);
  return surface.id === surfaceId || surface.label.toLowerCase() === String(surfaceId).toLowerCase();
}
export function groupBySurface(files, rules = DEFAULT_SURFACE_RULES){
  const out = new Map();
  for(const file of files){
    const surface = classifySurface(file, rules);
    if(!out.has(surface.id)) out.set(surface.id, { surface, files: [] });
    out.get(surface.id).files.push(file);
  }
  return [...out.values()].sort((a,b) => a.surface.label.localeCompare(b.surface.label));
}
export function inferRouteFromPath(filePath){
  const p = normalizePath(filePath);
  const routeMatch = p.match(/app\/(?:\(([^)]+)\)\/)?([^/]+)(?:\/page|\/layout)?\.(?:tsx|jsx|ts|js)$/);
  if(routeMatch) return '/' + routeMatch[2];
  if(p.includes('/components/pos/')) return '/pos';
  if(p.includes('/checkout')) return '/checkout';
  if(p.includes('/payment')) return '/payment';
  return '';
}
export function createSurfaceSummary(files, rules = DEFAULT_SURFACE_RULES){
  const groups = groupBySurface(files, rules);
  return groups.map((group) => ({ id: group.surface.id, label: group.surface.label, files: group.files.length }));
}
