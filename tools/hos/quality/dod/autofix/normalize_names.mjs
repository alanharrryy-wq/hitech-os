import path from "node:path"
import fs from "node:fs/promises"
import { sanitizeId } from "../../../../../apps/keystone/lib/pitch-engine-tooling/windows-safe.mjs"
import { pathExists } from "../../../../../apps/keystone/lib/pitch-engine-tooling/fs-utils.mjs"
import { PITCH_ARTIFACT_ROOT } from "../../../../../apps/keystone/lib/pitch-engine-tooling/constants.mjs"

export async function runAutofixNormalizeNames() {
  const programsRoot = path.join(PITCH_ARTIFACT_ROOT, "programs")
  if (!(await pathExists(programsRoot))) {
    return {
      ok: true,
      id: "autofix-normalize-names",
      detail: "No programs directory present; nothing to normalize.",
      renamed: []
    }
  }

  const entries = await fs.readdir(programsRoot, { withFileTypes: true })
  const renamed = []

  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue
    }

    const safeName = sanitizeId(entry.name, "program")
    if (safeName === entry.name) {
      continue
    }

    const fromPath = path.join(programsRoot, entry.name)
    const toPath = path.join(programsRoot, safeName)

    await fs.rename(fromPath, toPath)
    renamed.push({ from: entry.name, to: safeName })
  }

  return {
    ok: true,
    id: "autofix-normalize-names",
    detail: "Normalized unsafe directory names under pitch artifacts.",
    renamed
  }
}
