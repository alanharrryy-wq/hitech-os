import childProcess from 'node:child_process';
import path from 'node:path';
import { normalizePath } from './fs-utils.mjs';

export function runCommand(command, args = [], options = {}){
  const result = childProcess.spawnSync(command, args, {
    cwd: options.cwd,
    encoding: 'utf8',
    shell: false,
    windowsHide: true,
    maxBuffer: options.maxBuffer || 20 * 1024 * 1024,
  });
  return { code: result.status ?? 1, stdout: result.stdout || '', stderr: result.stderr || '', command: [command, ...args].join(' ') };
}
export function runGit(repoRoot, args, options = {}){ return runCommand('git', args, { ...options, cwd: repoRoot }); }
export function discoverGitRoot(startDir){
  const result = runCommand('git', ['rev-parse', '--show-toplevel'], { cwd: startDir });
  if(result.code === 0 && result.stdout.trim()) return path.resolve(result.stdout.trim());
  return path.resolve(startDir);
}
export function isGitRepo(repoRoot){ return runGit(repoRoot, ['rev-parse', '--is-inside-work-tree']).code === 0; }
export function getCurrentBranch(repoRoot){
  const result = runGit(repoRoot, ['branch', '--show-current']);
  return result.code === 0 ? result.stdout.trim() : '';
}
export function getGitStatus(repoRoot){
  const result = runGit(repoRoot, ['status', '--short']);
  return result.code === 0 ? result.stdout : '';
}
export function listTrackedFiles(repoRoot){
  const result = runGit(repoRoot, ['ls-files', '-z']);
  if(result.code !== 0) return [];
  return result.stdout.split('\0').filter(Boolean).map((p) => normalizePath(p));
}
export function listStagedFiles(repoRoot){
  const result = runGit(repoRoot, ['diff', '--cached', '--name-only', '-z']);
  if(result.code !== 0) return [];
  return result.stdout.split('\0').filter(Boolean).map((p) => normalizePath(p));
}
export function listModifiedFiles(repoRoot){
  const result = runGit(repoRoot, ['diff', '--name-only', '-z']);
  if(result.code !== 0) return [];
  return result.stdout.split('\0').filter(Boolean).map((p) => normalizePath(p));
}
export function buildGitSnapshot(repoRoot){
  return {
    repoRoot: normalizePath(repoRoot),
    isGitRepo: isGitRepo(repoRoot),
    branch: getCurrentBranch(repoRoot),
    status: getGitStatus(repoRoot),
    trackedCount: listTrackedFiles(repoRoot).length,
    stagedCount: listStagedFiles(repoRoot).length,
    modifiedCount: listModifiedFiles(repoRoot).length,
  };
}
