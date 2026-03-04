import path from "node:path"
import { runCommand } from "../../../../../apps/keystone/lib/pitch-engine-tooling/exec.mjs"

export async function runAutofixRegenerateRouteDiscovery(repoRoot = process.cwd()) {
  const appDir = path.join(repoRoot, "apps/keystone")

  const result = await runCommand("pnpm", ["--filter", "@hitech/keystone", "build"], {
    cwd: repoRoot,
    captureOutput: true,
    timeoutMs: 20 * 60 * 1000
  })

  if (result.exitCode !== 0) {
    return {
      ok: false,
      id: "autofix-regenerate-route-discovery",
      detail: "Failed to regenerate route discovery outputs via build.",
      stderr: result.stderr,
      stdout: result.stdout,
      appDir
    }
  }

  return {
    ok: true,
    id: "autofix-regenerate-route-discovery",
    detail: "Regenerated route discovery outputs by running Keystone build.",
    appDir
  }
}
