import fs from 'node:fs';
import path from 'node:path';

export function readPackageJson(packagePath) {
  try {
    return JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  } catch (error) {
    return { __error: error.message || String(error), scripts: {} };
  }
}

export function workspaceScriptMatrix(repoRoot, workspaces) {
  return workspaces.map((workspace) => {
    const packagePath = path.join(repoRoot, workspace, 'package.json');
    const pkg = readPackageJson(packagePath);
    const scripts = pkg.scripts || {};
    return {
      workspace,
      packagePath: path.relative(repoRoot, packagePath).replaceAll('\\', '/'),
      exists: fs.existsSync(packagePath),
      name: pkg.name || null,
      hasDev: Boolean(scripts.dev),
      hasBuild: Boolean(scripts.build),
      hasTypecheck: Boolean(scripts.typecheck),
      hasLint: Boolean(scripts.lint),
      scripts: Object.keys(scripts).sort(),
      error: pkg.__error || null
    };
  });
}
