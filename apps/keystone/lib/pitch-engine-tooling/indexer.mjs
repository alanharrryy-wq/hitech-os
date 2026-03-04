import path from "node:path"
import {
  INDEX_METADATA_VERSION,
  PITCH_INDEX_HTML,
  PITCH_INDEX_JSON,
  PITCH_INDEX_MD,
  SCENE_INDEX_HTML,
  SCENE_INDEX_JSON,
  SCENE_INDEX_MD
} from "./constants.mjs"
import {
  listDirectories,
  listFilesRecursive,
  pathExists,
  readDirectoryDetailed,
  readJsonIfExists,
  writeJsonFile,
  writeTextFile
} from "./fs-utils.mjs"
import {
  resolvePitchArtifactsRoot,
  resolvePitchIndexPath,
  resolveProgramDir,
  resolveProgramRunDir,
  resolveSceneArtifactsRoot,
  resolveSceneIndexPath,
  resolveSceneRetentionDir,
  resolveSceneTriageDir,
  resolveSharedRetentionPath,
  toRelativeFromArtifacts
} from "./paths.mjs"

function toHumanDate(value) {
  return new Date(value).toISOString()
}

async function buildProgramRunIndex(programId, runId) {
  const runPath = resolveProgramRunDir(programId, runId)
  const runFiles = await listFilesRecursive(runPath)

  return {
    runId,
    runPath: toRelativeFromArtifacts(runPath),
    fileCount: runFiles.length,
    files: runFiles.slice(0, 200).map((entry) => toRelativeFromArtifacts(entry))
  }
}

async function buildProgramEntry(programId) {
  const programDir = resolveProgramDir(programId)
  const runIds = await listDirectories(programDir)
  const runs = []

  for (const runId of runIds) {
    if (runId === "baselines") {
      continue
    }
    const runPath = resolveProgramRunDir(programId, runId)
    if (!(await pathExists(runPath))) {
      continue
    }
    runs.push(await buildProgramRunIndex(programId, runId))
  }

  const retentionPath = path.join(programDir, "retention.json")
  const retention = await readJsonIfExists(retentionPath, null)

  return {
    programId,
    runCount: runs.length,
    runs,
    retention
  }
}

export async function buildPitchIndexData() {
  const programsRoot = path.join(resolvePitchArtifactsRoot(), "programs")
  const programIds = await listDirectories(programsRoot)
  const programEntries = []

  for (const programId of programIds) {
    programEntries.push(await buildProgramEntry(programId))
  }

  const retentionMeta = await readJsonIfExists(path.join(resolveSharedRetentionPath(), "summary.json"), {
    version: 1,
    updatedAtUtc: null,
    programs: []
  })

  return {
    metadataVersion: INDEX_METADATA_VERSION,
    generatedAtUtc: new Date().toISOString(),
    root: toRelativeFromArtifacts(resolvePitchArtifactsRoot()),
    programCount: programEntries.length,
    programs: programEntries,
    retention: retentionMeta
  }
}

export async function writePitchIndexFiles() {
  const indexData = await buildPitchIndexData()

  await writeJsonFile(resolvePitchIndexPath(PITCH_INDEX_JSON), indexData)

  const markdownLines = [
    "# Keystone Pitch Engine Artifacts",
    "",
    `Generated: ${toHumanDate(indexData.generatedAtUtc)}`,
    `Programs: ${indexData.programCount}`,
    ""
  ]

  for (const program of indexData.programs) {
    markdownLines.push(`## Program ${program.programId}`)
    markdownLines.push(`Runs: ${program.runCount}`)
    markdownLines.push("")

    for (const run of program.runs) {
      markdownLines.push(`- ${run.runId} (${run.fileCount} files)`) // concise index list
    }

    markdownLines.push("")
  }

  await writeTextFile(resolvePitchIndexPath(PITCH_INDEX_MD), markdownLines.join("\n") + "\n")

  const htmlLines = [
    "<!doctype html>",
    '<html lang="en">',
    "<head>",
    '  <meta charset="utf-8">',
    '  <meta name="viewport" content="width=device-width, initial-scale=1">',
    "  <title>Keystone Pitch Engine Artifacts</title>",
    "  <style>",
    "    body{font-family:Segoe UI,Arial,sans-serif;margin:24px;background:#f4f6f9;color:#102a43}",
    "    .program{background:#fff;border:1px solid #d9e2ec;border-radius:8px;padding:16px;margin:12px 0}",
    "    code{background:#eef2f7;padding:2px 6px;border-radius:4px}",
    "  </style>",
    "</head>",
    "<body>",
    "  <h1>Keystone Pitch Engine Artifacts</h1>",
    `  <p>Generated at <code>${toHumanDate(indexData.generatedAtUtc)}</code></p>`,
    `  <p>Total programs: <strong>${indexData.programCount}</strong></p>`
  ]

  for (const program of indexData.programs) {
    htmlLines.push(`  <section class="program"><h2>${program.programId}</h2>`)
    htmlLines.push(`    <p>Runs: ${program.runCount}</p>`)
    htmlLines.push("    <ul>")
    for (const run of program.runs) {
      htmlLines.push(`      <li><code>${run.runId}</code> (${run.fileCount} files)</li>`)
    }
    htmlLines.push("    </ul>")
    htmlLines.push("  </section>")
  }

  htmlLines.push("</body>")
  htmlLines.push("</html>")

  await writeTextFile(resolvePitchIndexPath(PITCH_INDEX_HTML), htmlLines.join("\n") + "\n")

  return indexData
}

export async function buildSceneIndexData() {
  const root = resolveSceneArtifactsRoot()
  const triageDir = resolveSceneTriageDir()
  const retentionDir = resolveSceneRetentionDir()
  const triageEntries = await readDirectoryDetailed(triageDir)
  const retentionEntries = await readDirectoryDetailed(retentionDir)

  return {
    metadataVersion: INDEX_METADATA_VERSION,
    generatedAtUtc: new Date().toISOString(),
    root: toRelativeFromArtifacts(root),
    triageFiles: triageEntries.map((entry) => ({
      name: entry.name,
      size: entry.size,
      updatedAtUtc: toHumanDate(entry.mtimeMs)
    })),
    retentionFiles: retentionEntries.map((entry) => ({
      name: entry.name,
      size: entry.size,
      updatedAtUtc: toHumanDate(entry.mtimeMs)
    }))
  }
}

export async function writeSceneIndexFiles() {
  const indexData = await buildSceneIndexData()

  await writeJsonFile(resolveSceneIndexPath(SCENE_INDEX_JSON), indexData)

  const markdownLines = [
    "# Keystone Scene Studio Operations",
    "",
    `Generated: ${toHumanDate(indexData.generatedAtUtc)}`,
    "",
    "## Triage Files",
    ...indexData.triageFiles.map((entry) => `- ${entry.name} (${entry.size} bytes)`),
    "",
    "## Retention Files",
    ...indexData.retentionFiles.map((entry) => `- ${entry.name} (${entry.size} bytes)`),
    ""
  ]

  await writeTextFile(resolveSceneIndexPath(SCENE_INDEX_MD), markdownLines.join("\n") + "\n")

  const htmlLines = [
    "<!doctype html>",
    '<html lang="en">',
    "<head>",
    '  <meta charset="utf-8">',
    '  <meta name="viewport" content="width=device-width, initial-scale=1">',
    "  <title>Keystone Scene Studio Operations</title>",
    "  <style>",
    "    body{font-family:Segoe UI,Arial,sans-serif;margin:24px;background:#fbfcfe;color:#102a43}",
    "    section{margin-bottom:20px;padding:12px;border:1px solid #d9e2ec;border-radius:6px;background:#fff}",
    "    li{margin:4px 0}",
    "  </style>",
    "</head>",
    "<body>",
    "  <h1>Keystone Scene Studio Operations</h1>",
    `  <p>Generated at <strong>${toHumanDate(indexData.generatedAtUtc)}</strong></p>`,
    "  <section>",
    "    <h2>Triage Files</h2>",
    "    <ul>"
  ]

  for (const entry of indexData.triageFiles) {
    htmlLines.push(`      <li>${entry.name} (${entry.size} bytes)</li>`)
  }

  htmlLines.push("    </ul>")
  htmlLines.push("  </section>")
  htmlLines.push("  <section>")
  htmlLines.push("    <h2>Retention Files</h2>")
  htmlLines.push("    <ul>")

  for (const entry of indexData.retentionFiles) {
    htmlLines.push(`      <li>${entry.name} (${entry.size} bytes)</li>`)
  }

  htmlLines.push("    </ul>")
  htmlLines.push("  </section>")
  htmlLines.push("</body>")
  htmlLines.push("</html>")

  await writeTextFile(resolveSceneIndexPath(SCENE_INDEX_HTML), htmlLines.join("\n") + "\n")

  return indexData
}
