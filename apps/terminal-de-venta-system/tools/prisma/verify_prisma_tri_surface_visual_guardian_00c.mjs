import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";

const root = process.argv[2] || process.cwd();
const manifest = join(root, "manifests/PRISMA_APP_MOBILE_03_PRODUCT_ROOT_REBASE.manifest.json");
const script = join(root, "tools/prisma/prisma_tri_surface_visual_guardian_00c.py");

if (!existsSync(manifest)) {
  console.error(`Missing manifest: ${manifest}`);
  process.exit(1);
}
if (!existsSync(script)) {
  console.error(`Missing guardian script: ${script}`);
  process.exit(1);
}

const candidates = [];
if (process.env.PYTHON) candidates.push([process.env.PYTHON, []]);
candidates.push(["py", ["-3", "-S"]]);
candidates.push(["python", ["-S"]]);
candidates.push(["python3", ["-S"]]);

let last = null;
for (const [cmd, prefix] of candidates) {
  const result = spawnSync(cmd, [...prefix, script, "--manifest", manifest, "--root", root, "--scan-root", "products/mobile/app", "--scan-root", "docs/mobile/PRISMA_APP_MOBILE_03_PRODUCT_ROOT_REBASE.md"], {
    cwd: root,
    encoding: "utf8",
    shell: false
  });
  if (result.error) {
    last = result.error.message;
    continue;
  }
  process.stdout.write(result.stdout || "");
  process.stderr.write(result.stderr || "");
  process.exit(result.status ?? 1);
}
console.error(`Unable to run Python guardian. Last error: ${last}`);
process.exit(1);
