import fs from 'node:fs';
import path from 'node:path';
const BACKSLASH = String.fromCharCode(92);
export function pathExists(p) { try { fs.accessSync(p); return true; } catch { return false; } }
export function isDir(p) { try { return fs.statSync(p).isDirectory(); } catch { return false; } }
export function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }
export function toPosix(p) { return String(p).split(BACKSLASH).join('/'); }
export function shouldIgnore(fullPath, ignoreParts = []) {
  const normalized = toPosix(fullPath).toLowerCase();
  return ignoreParts.some((part) => normalized.includes(String(part).split(BACKSLASH).join('/').toLowerCase()));
}
export function listFiles(root, options = {}) {
  const out = [];
  const maxBytes = options.maxBytes ?? 1048576;
  const exts = new Set(options.extensions ?? []);
  const ignore = options.ignore ?? [];
  function walk(dir) {
    if (!isDir(dir) || shouldIgnore(dir, ignore)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, entry.name);
      if (shouldIgnore(p, ignore)) continue;
      if (entry.isDirectory()) walk(p);
      if (entry.isFile()) {
        const stat = fs.statSync(p);
        const ext = path.extname(entry.name);
        if (stat.size <= maxBytes && (exts.size === 0 || exts.has(ext))) out.push(p);
      }
    }
  }
  walk(root);
  return out;
}
export function readTextSafe(p) { try { return fs.readFileSync(p, 'utf8'); } catch { return ''; } }
export function rel(ctx, p) { return toPosix(path.relative(ctx.repoRoot, p)); }
