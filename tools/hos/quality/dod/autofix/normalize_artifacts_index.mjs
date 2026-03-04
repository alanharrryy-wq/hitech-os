import fs from "node:fs/promises"
import path from "node:path"
import { PITCH_ARTIFACT_ROOT, SCENE_ARTIFACT_ROOT } from "../../../../../apps/keystone/lib/pitch-engine-tooling/constants.mjs"
import { pathExists, readJsonIfExists, writeJsonFile } from "../../../../../apps/keystone/lib/pitch-engine-tooling/fs-utils.mjs"

async function normalizeIndexFile(indexPath) {
  if (!(await pathExists(indexPath))) {
    return {
      path: indexPath,
      changed: false,
      reason: "missing"
    }
  }

  const payload = await readJsonIfExists(indexPath, null)
  if (!payload || typeof payload !== "object") {
    await writeJsonFile(indexPath, {
      metadataVersion: "1.0.0",
      generatedAtUtc: new Date().toISOString(),
      entries: []
    })

    return {
      path: indexPath,
      changed: true,
      reason: "replaced-invalid-json"
    }
  }

  payload.generatedAtUtc = new Date().toISOString()
  await writeJsonFile(indexPath, payload)

  return {
    path: indexPath,
    changed: true,
    reason: "normalized-generatedAt"
  }
}

export async function runAutofixNormalizeArtifactsIndex() {
  const targets = [
    path.join(PITCH_ARTIFACT_ROOT, "index.json"),
    path.join(SCENE_ARTIFACT_ROOT, "index.json")
  ]

  const results = []
  for (const target of targets) {
    results.push(await normalizeIndexFile(target))
  }

  return {
    ok: true,
    id: "autofix-normalize-artifacts-index",
    detail: "Normalized artifact index JSON files.",
    results
  }
}
