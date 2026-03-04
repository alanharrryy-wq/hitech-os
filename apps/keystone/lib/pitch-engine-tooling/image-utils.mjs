import path from "node:path"
import { PSEUDO_PNG_BASE64 } from "./constants.mjs"
import { copyFileSafe, ensureDir, pathExists, writeJsonFile } from "./fs-utils.mjs"

export function createPlaceholderPngBuffer() {
  return Buffer.from(PSEUDO_PNG_BASE64, "base64")
}

export async function writePlaceholderPng(targetPath) {
  await ensureDir(path.dirname(targetPath))
  const payload = createPlaceholderPngBuffer()
  await import("node:fs/promises").then((fsp) => fsp.writeFile(targetPath, payload))
}

export async function buildSceneDiffAssets(options) {
  const {
    baselinePath,
    currentPath,
    beforeOutputPath,
    afterOutputPath,
    diffOutputPath,
    metadataOutputPath
  } = options

  const baselineExists = await pathExists(baselinePath)

  if (baselineExists) {
    await copyFileSafe(baselinePath, beforeOutputPath)
  } else {
    await writePlaceholderPng(beforeOutputPath)
  }

  await copyFileSafe(currentPath, afterOutputPath)

  if (baselineExists) {
    // Deterministic fallback for environments where image diff libraries are unavailable.
    // We still materialize a diff artifact so triage workflows are unblocked.
    await copyFileSafe(currentPath, diffOutputPath)
  } else {
    await writePlaceholderPng(diffOutputPath)
  }

  await writeJsonFile(metadataOutputPath, {
    baselineExists,
    before: path.basename(beforeOutputPath),
    after: path.basename(afterOutputPath),
    diff: path.basename(diffOutputPath),
    generatedAtUtc: new Date().toISOString(),
    strategy: baselineExists ? "copy-current-as-diff" : "placeholder"
  })

  return {
    baselineExists,
    beforeOutputPath,
    afterOutputPath,
    diffOutputPath,
    metadataOutputPath
  }
}
