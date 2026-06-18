import path from 'node:path';
import { pathExistsSync, readTextSync, sha256FileSync, normalizePath, preview } from './fs-utils.mjs';

export function locateOperationalManual(repoRoot, config){
  const candidates = [];
  for(const rel of config.manualPaths || []) candidates.push(path.join(repoRoot, rel));
  const found = [];
  for(const file of candidates){
    if(pathExistsSync(file)){
      const text = readTextSync(file);
      found.push({
        path: normalizePath(path.relative(repoRoot, file)),
        absolutePath: normalizePath(file),
        size: text.length,
        sha256: sha256FileSync(file),
        firstLine: preview(text.split(/\r?\n/)[0] || ''),
        mentions: {
          zeroGate: /zero\s+(?:priority|important)/i.test(text),
          authorityMesh: /authority\s+mesh/i.test(text),
          tablet: /tablet/i.test(text),
          noPriorityOverride: /priority\s+override/i.test(text),
        }
      });
    }
  }
  return { exists: found.length > 0, count: found.length, found, candidates: candidates.map((p) => normalizePath(path.relative(repoRoot, p))) };
}
export function summarizeManual(manual){
  if(!manual.exists) return 'Manual operativo no encontrado en rutas conocidas.';
  return manual.found.map((item) => `${item.path} (${item.size} chars)`).join(', ');
}
