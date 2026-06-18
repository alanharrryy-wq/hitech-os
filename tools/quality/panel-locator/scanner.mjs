import fs from 'node:fs';
import path from 'node:path';
import { SUPPORTED_CODE_EXTENSIONS, SUPPORTED_STYLE_EXTENSIONS, SUPPORTED_DOC_EXTENSIONS } from './constants.mjs';
import { fileExtension, toPosixRelative, walkFilesSync, readTextSync, countLines, safeStatSync, isTextCandidate } from './fs-utils.mjs';
import { listTrackedFiles, listStagedFiles } from './git-utils.mjs';
import { surfaceMatchesFilter, classifySurface } from './surface-classifier.mjs';

export function isCodeFile(filePath){ return SUPPORTED_CODE_EXTENSIONS.has(fileExtension(filePath)); }
export function isStyleFile(filePath){ return SUPPORTED_STYLE_EXTENSIONS.has(fileExtension(filePath)) || /\.module\.(css|scss)$/i.test(filePath); }
export function isDocFile(filePath){ return SUPPORTED_DOC_EXTENSIONS.has(fileExtension(filePath)); }
export function isRelevantFile(filePath){ return isCodeFile(filePath) || isStyleFile(filePath) || isDocFile(filePath); }
export function enumerateRepoFiles(repoRoot, config, options = {}){
  const mode = options.mode || 'repo-tree';
  const surface = options.surface || 'all';
  const maxBytes = config.maxFileBytes;
  let files = [];
  if(mode === 'tracked'){
    files = listTrackedFiles(repoRoot).map((rel) => path.join(repoRoot, rel));
  } else if(mode === 'staged'){
    files = listStagedFiles(repoRoot).map((rel) => path.join(repoRoot, rel));
  } else {
    files = walkFilesSync(repoRoot, { ignoredDirs: config.ignoredDirsSet, maxBytes, include: (file, stat) => isRelevantFile(file) && isTextCandidate(file, stat, maxBytes) });
  }
  const seen = new Set();
  const out = [];
  for(const file of files){
    const stat = safeStatSync(file);
    if(!stat || !stat.isFile()) continue;
    if(!isRelevantFile(file)) continue;
    const rel = toPosixRelative(file, repoRoot);
    if(!surfaceMatchesFilter(rel, surface, config.surfaceRules)) continue;
    if(seen.has(rel)) continue;
    seen.add(rel);
    out.push({ absolutePath: file, relativePath: rel, extension: fileExtension(file), kind: isStyleFile(file) ? 'style' : isCodeFile(file) ? 'code' : 'doc', size: stat.size, surface: classifySurface(rel, config.surfaceRules) });
  }
  return out.sort((a,b) => a.relativePath.localeCompare(b.relativePath));
}
export function readFileRecords(records){
  return records.map((record) => {
    let text = '';
    let error = null;
    try { text = readTextSync(record.absolutePath); } catch (err) { error = String(err && err.message ? err.message : err); }
    return { ...record, text, error, lines: text ? countLines(text) : 0 };
  });
}
export function createScanSummary(records){
  const summary = { total: records.length, code: 0, style: 0, doc: 0, bytes: 0, lines: 0, surfaces: {} };
  for(const record of records){
    summary[record.kind] = (summary[record.kind] || 0) + 1;
    summary.bytes += record.size || 0;
    summary.lines += record.lines || 0;
    const key = record.surface?.id || 'unknown';
    if(!summary.surfaces[key]) summary.surfaces[key] = { label: record.surface?.label || key, files: 0, lines: 0 };
    summary.surfaces[key].files++;
    summary.surfaces[key].lines += record.lines || 0;
  }
  return summary;
}
