import path from 'node:path';
import { DEFAULT_IGNORED_DIRS, DEFAULT_SURFACE_RULES, DEFAULT_WORKERS, MAX_DEFAULT_FILE_BYTES, ROOT_CONFIG_FILE } from './constants.mjs';
import { pathExistsSync, readJsonSync, normalizePath } from './fs-utils.mjs';
import { discoverGitRoot } from './git-utils.mjs';

export function defaultConfig(){
  return {
    version: 1,
    workers: DEFAULT_WORKERS,
    maxFileBytes: MAX_DEFAULT_FILE_BYTES,
    ignoredDirs: [...DEFAULT_IGNORED_DIRS],
    surfaceRules: DEFAULT_SURFACE_RULES,
    manualPaths: [
      'docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md',
      'apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md',
      'apps/terminal-de-venta-system/docs/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md',
      'docs/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md'
    ],
    output: { includeJson: true, includeMarkdown: true, includeContinuation: true },
    safety: { readOnly: true, noProcessTouch: true, noPrismaGenerate: true, noGitWrite: true },
  };
}
export function deepMerge(base, extra){
  if(!extra || typeof extra !== 'object') return base;
  const out = Array.isArray(base) ? [...base] : { ...base };
  for(const [key,value] of Object.entries(extra)){
    if(value && typeof value === 'object' && !Array.isArray(value) && base && typeof base[key] === 'object' && !Array.isArray(base[key])) out[key] = deepMerge(base[key], value);
    else out[key] = value;
  }
  return out;
}
export function resolveRepoRoot(argvRepo){
  if(argvRepo) return path.resolve(argvRepo);
  return discoverGitRoot(process.cwd());
}
export function loadPanelLocatorConfig(repoRoot, explicitConfig){
  const base = defaultConfig();
  const configPath = explicitConfig ? path.resolve(explicitConfig) : path.join(repoRoot, ROOT_CONFIG_FILE);
  const disk = pathExistsSync(configPath) ? readJsonSync(configPath, {}) : {};
  const merged = deepMerge(base, disk || {});
  merged.repoRoot = normalizePath(repoRoot);
  merged.configPath = normalizePath(configPath);
  merged.ignoredDirsSet = new Set(merged.ignoredDirs || []);
  return merged;
}
export function parseCliArgs(argv){
  const args = { _: [] };
  for(let i=0;i<argv.length;i++){
    const item = argv[i];
    if(!item.startsWith('--')){ args._.push(item); continue; }
    const eq = item.indexOf('=');
    if(eq > 0){ args[item.slice(2,eq)] = item.slice(eq+1); continue; }
    const key = item.slice(2);
    const next = argv[i+1];
    if(next && !next.startsWith('--')){ args[key] = next; i++; }
    else args[key] = true;
  }
  return args;
}
export function normalizeMode(value){
  const mode = String(value || 'repo-tree').toLowerCase();
  if(['repo-tree','tracked','staged','surface'].includes(mode)) return mode;
  return 'repo-tree';
}
