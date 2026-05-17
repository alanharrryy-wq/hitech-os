import os from 'node:os';
import process from 'node:process';
import childProcess from 'node:child_process';
function tryRun(cmd, args) { try { const r = childProcess.spawnSync(cmd, args, { encoding: 'utf8', shell: false }); return { command: [cmd, ...args].join(' '), exitCode: r.status, stdout: (r.stdout || '').trim().slice(0, 4000), stderr: (r.stderr || '').trim().slice(0, 4000) }; } catch (error) { return { command: [cmd, ...args].join(' '), error: String(error.message || error) }; } }
export function environmentSnapshot(repoRoot) { return { schemaVersion: '1.0', platform: process.platform, node: process.version, cwd: process.cwd(), repoRoot, os: { type: os.type(), release: os.release(), arch: os.arch(), cpus: os.cpus()?.length ?? null }, tools: [tryRun('pnpm', ['--version']), tryRun('git', ['rev-parse', '--short', 'HEAD'])] }; }
