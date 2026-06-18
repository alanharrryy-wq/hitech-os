import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { BINARY_EXTENSIONS, DEFAULT_IGNORED_DIRS, MAX_DEFAULT_FILE_BYTES } from './constants.mjs';

export function normalizePath(value){ return String(value || '').replace(/\\/g, '/'); }
export function toPosixRelative(filePath, root){
  const rel = path.relative(root, filePath);
  return normalizePath(rel || '.');
}
export function splitPathParts(value){ return normalizePath(value).split('/').filter(Boolean); }
export function hasIgnoredDir(filePath, root, ignored = DEFAULT_IGNORED_DIRS){
  const parts = splitPathParts(toPosixRelative(filePath, root));
  return parts.some((part) => ignored.has(part));
}
export async function pathExists(target){
  try { await fsp.access(target); return true; } catch { return false; }
}
export function pathExistsSync(target){
  try { fs.accessSync(target); return true; } catch { return false; }
}
export function ensureDirSync(dir){ fs.mkdirSync(dir, { recursive: true }); }
export async function ensureDir(dir){ await fsp.mkdir(dir, { recursive: true }); }
export function readTextSync(filePath){ return fs.readFileSync(filePath, 'utf8'); }
export async function readText(filePath){ return await fsp.readFile(filePath, 'utf8'); }
export function writeTextSync(filePath, text){ ensureDirSync(path.dirname(filePath)); fs.writeFileSync(filePath, text, 'utf8'); }
export async function writeText(filePath, text){ await ensureDir(path.dirname(filePath)); await fsp.writeFile(filePath, text, 'utf8'); }
export function readJsonSync(filePath, fallback = null){
  try { return JSON.parse(readTextSync(filePath)); } catch { return fallback; }
}
export function writeJsonSync(filePath, value){ writeTextSync(filePath, `${JSON.stringify(value, null, 2)}\n`); }
export function fileExtension(filePath){
  const base = path.basename(filePath).toLowerCase();
  if(base.endsWith('.module.css')) return '.module.css';
  if(base.endsWith('.module.scss')) return '.module.scss';
  return path.extname(base).toLowerCase();
}
export function isBinaryByExtension(filePath){ return BINARY_EXTENSIONS.has(path.extname(filePath).toLowerCase()); }
export function isProbablyBinaryBuffer(buffer){
  const len = Math.min(buffer.length, 4096);
  for(let i=0;i<len;i++){ if(buffer[i] === 0) return true; }
  return false;
}
export function isTextCandidate(filePath, stat, maxBytes = MAX_DEFAULT_FILE_BYTES){
  if(!stat || !stat.isFile()) return false;
  if(stat.size > maxBytes) return false;
  if(isBinaryByExtension(filePath)) return false;
  return true;
}
export function sha256FileSync(filePath){
  const hash = crypto.createHash('sha256');
  const buffer = fs.readFileSync(filePath);
  hash.update(buffer);
  return hash.digest('hex');
}
export function countLines(text){ if(!text) return 0; return text.split(/\r?\n/).length; }
export function getLineAt(text, lineNumber){ const lines = String(text || '').split(/\r?\n/); return lines[Math.max(0, lineNumber - 1)] || ''; }
export function clamp(value, min, max){ return Math.min(max, Math.max(min, value)); }
export function preview(text, limit = 180){ return String(text || '').replace(/\s+/g, ' ').trim().slice(0, limit); }
export function uniqueBy(items, keyFn){
  const seen = new Set();
  const out = [];
  for(const item of items){
    const key = keyFn(item);
    if(seen.has(key)) continue;
    seen.add(key);
    out.push(item);
  }
  return out;
}
export function sortByPathLine(items){
  return [...items].sort((a,b) => String(a.file || '').localeCompare(String(b.file || '')) || Number(a.line || a.startLine || 0) - Number(b.line || b.startLine || 0));
}
export function safeStatSync(filePath){ try { return fs.statSync(filePath); } catch { return null; } }
export function walkFilesSync(root, options = {}){
  const ignored = options.ignoredDirs || DEFAULT_IGNORED_DIRS;
  const maxBytes = options.maxBytes || MAX_DEFAULT_FILE_BYTES;
  const include = options.include || (() => true);
  const result = [];
  const stack = [root];
  while(stack.length){
    const current = stack.pop();
    let entries = [];
    try { entries = fs.readdirSync(current, { withFileTypes: true }); } catch { continue; }
    for(const entry of entries){
      const full = path.join(current, entry.name);
      if(entry.isDirectory()){
        if(ignored.has(entry.name)) continue;
        stack.push(full);
      } else if(entry.isFile()){
        const stat = safeStatSync(full);
        if(!isTextCandidate(full, stat, maxBytes)) continue;
        if(include(full, stat)) result.push(full);
      }
    }
  }
  return result.sort((a,b) => normalizePath(a).localeCompare(normalizePath(b)));
}
export function extractLineWindow(text, centerLine, radius = 4){
  const lines = String(text || '').split(/\r?\n/);
  const start = clamp(centerLine - radius, 1, lines.length);
  const end = clamp(centerLine + radius, 1, lines.length);
  const out = [];
  for(let i=start;i<=end;i++) out.push({ line: i, text: lines[i-1] || '' });
  return out;
}
