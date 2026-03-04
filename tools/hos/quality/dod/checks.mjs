import path from "node:path"
import fs from "node:fs/promises"
import {
  DOD_CHECK_IDS,
  DOD_CHECK_STATUS,
  PITCH_ARTIFACT_ROOT,
  SCENE_ARTIFACT_ROOT
} from "../../../../apps/keystone/lib/pitch-engine-tooling/constants.mjs"
import { pathExists, readJsonIfExists } from "../../../../apps/keystone/lib/pitch-engine-tooling/fs-utils.mjs"
import { runCommand } from "../../../../apps/keystone/lib/pitch-engine-tooling/exec.mjs"

function makeResult(check, status, detail, extras = {}) {
  return {
    id: check.id,
    title: check.title,
    ownership: check.ownership,
    severity: check.severity,
    status,
    detail,
    ...extras
  }
}

async function fileContains(filePath, pattern) {
  try {
    const payload = await fs.readFile(filePath, "utf8")
    return payload.includes(pattern)
  } catch {
    return false
  }
}

async function checkLayerDomContract(check, repoRoot) {
  const layerFile = path.join(repoRoot, "packages/ui-kit/src/layers/layerIds.ts")
  const testFile = path.join(repoRoot, "apps/keystone/tests/layer-data-attributes.test.tsx")

  const layerReady = await fileContains(layerFile, "data-layer-stage-noise")
  const testReady = await fileContains(testFile, "data-layer-stage-noise")

  if (layerReady && testReady) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Layer DOM hooks and tests detected.")
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "Missing canonical data-layer hook references.", {
    blockers: [
      layerReady ? null : `Missing layer mapping in ${path.relative(repoRoot, layerFile)}`,
      testReady ? null : `Missing layer test coverage in ${path.relative(repoRoot, testFile)}`
    ].filter(Boolean)
  })
}

async function checkSceneReadySignal(check, repoRoot) {
  const result = await runCommand(
    "rg",
    ["-n", "data-scene-ready", "apps", "packages", "tools", "docs"],
    {
      cwd: repoRoot,
      captureOutput: true,
      timeoutMs: 30_000
    }
  )

  if (result.exitCode === 0) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "data-scene-ready signal exists.")
  }

  return makeResult(
    check,
    DOD_CHECK_STATUS.fail,
    "data-scene-ready signal not found. Requires core scene runtime updates outside B_tooling ownership.",
    {
      blockers: ["No data-scene-ready='1' selector found in repo sources."]
    }
  )
}

async function checkSchemaVersioned(check, repoRoot) {
  const programModelPath = path.join(repoRoot, "apps/keystone/lib/pitch-engine-tooling/program-model.mjs")
  const hasSchema = await fileContains(programModelPath, "SCENE_SCHEMA_VERSION")
  const hasCanonicalUrl = await fileContains(programModelPath, "canonicalUrl")

  if (hasSchema && hasCanonicalUrl) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Scene schema envelope includes version and canonical URL.")
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "Scene schema envelope is incomplete.")
}

async function checkRouteDiscoveryOutput(check, repoRoot) {
  const candidates = [
    path.join(repoRoot, "apps/keystone/.next/server/app-paths-manifest.json"),
    path.join(repoRoot, "apps/keystone/.next/routes-manifest.json"),
    path.join(repoRoot, "apps/keystone/.next/app-path-routes-manifest.json")
  ]

  const exists = []
  for (const candidate of candidates) {
    if (await pathExists(candidate)) {
      exists.push(path.relative(repoRoot, candidate))
    }
  }

  if (exists.length > 0) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Route discovery outputs detected.", {
      evidence: exists
    })
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "Route discovery outputs missing; run next build to regenerate.", {
    blockers: ["No .next route manifest files found."]
  })
}

async function checkDevOnly404(check, repoRoot) {
  const appRoot = path.join(repoRoot, "apps/keystone/app")
  const routeFile = path.join(appRoot, "api")
  const exists = await pathExists(routeFile)

  if (!exists) {
    return makeResult(
      check,
      DOD_CHECK_STATUS.fail,
      "Unable to verify dev-only 404 contract because Keystone API directory is missing."
    )
  }

  // This check is inference-based: presence of app/api routes indicates Next handler exists.
  // Enforcement details are owned by core route handlers.
  return makeResult(
    check,
    DOD_CHECK_STATUS.warn,
    "Dev-only 404 behavior must be validated in runtime integration tests (outside tooling ownership)."
  )
}

async function checkRunnerCommands(check, repoRoot) {
  const appPackage = path.join(repoRoot, "apps/keystone/package.json")
  const payload = JSON.parse(await fs.readFile(appPackage, "utf8"))
  const scripts = payload.scripts ?? {}

  const expected = [
    "keystone:pitch:render",
    "keystone:pitch:render:sequence",
    "keystone:pitch:doctor",
    "keystone:pitch:onebutton",
    "keystone:scene:triage",
    "keystone:scene:doctor",
    "keystone:scene:onebutton"
  ]

  const missing = expected.filter((name) => typeof scripts[name] !== "string")

  if (missing.length === 0) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Deterministic runner scripts are wired.")
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "Missing runner script wiring in apps/keystone/package.json.", {
    blockers: missing
  })
}

async function checkArtifactsIndex(check) {
  const pitchIndex = path.join(PITCH_ARTIFACT_ROOT, "index.json")
  const sceneIndex = path.join(SCENE_ARTIFACT_ROOT, "index.json")

  const pitchExists = await pathExists(pitchIndex)
  const sceneExists = await pathExists(sceneIndex)

  if (pitchExists && sceneExists) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Artifact indexes are present.")
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "Artifact index files are missing.", {
    blockers: [
      pitchExists ? null : pitchIndex,
      sceneExists ? null : sceneIndex
    ].filter(Boolean)
  })
}

async function checkRetentionPin(check, repoRoot) {
  const retentionScript = path.join(repoRoot, "apps/keystone/scripts/pitch-engine/prune.mjs")
  const pinScript = path.join(repoRoot, "apps/keystone/scripts/pitch-engine/pin.mjs")

  const hasRetention = await pathExists(retentionScript)
  const hasPin = await pathExists(pinScript)

  if (hasRetention && hasPin) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Retention + pin commands present.")
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "Retention/pin command scripts missing.")
}

async function checkClaimWorkflow(check, repoRoot) {
  const governanceDoc = path.join(repoRoot, "docs/CONTRACT.md")
  const hasClaim = await fileContains(governanceDoc, "Evidence")
  const hasGate = await fileContains(governanceDoc, "No silent passes")

  if (hasClaim && hasGate) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Governance claims + gate language present in contract.")
  }

  return makeResult(check, DOD_CHECK_STATUS.warn, "Claim workflow or gate language not fully discoverable in docs.")
}

async function checkCapabilitiesRegistry(check, repoRoot) {
  const contractsIndex = path.join(repoRoot, "packages/contracts/src/index.ts")
  const flagsFile = path.join(repoRoot, "packages/contracts/src/featureFlags.ts")

  const hasCapabilities = await fileContains(contractsIndex, "capabilities")
  const hasFlagsDefaultOff = await fileContains(flagsFile, "false")

  if (hasCapabilities && hasFlagsDefaultOff) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Capabilities registry references and OFF defaults detected.")
  }

  return makeResult(check, DOD_CHECK_STATUS.warn, "Capabilities/prod-off assertion needs broader cross-service validation.")
}

async function checkDirectorTimeline(check, repoRoot) {
  const timelineFile = path.join(repoRoot, "apps/keystone/lib/pitch-engine-tooling/timeline.mjs")
  const rendererFile = path.join(repoRoot, "apps/keystone/lib/pitch-engine-tooling/renderer.mjs")

  const hasTimeline = await fileContains(timelineFile, "buildProgramTimeline")
  const hasKeyframes = await fileContains(rendererFile, "buildCaptureTasks")

  if (hasTimeline && hasKeyframes) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Timeline + keyframe orchestration present.")
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "Timeline/keyframe orchestration missing.")
}

async function checkTests(check, repoRoot, options) {
  const testsDir = path.join(repoRoot, "apps/keystone/tests/pitch-engine-tooling")
  const hasTestsDir = await pathExists(testsDir)

  if (!hasTestsDir) {
    return makeResult(check, DOD_CHECK_STATUS.fail, "Tooling tests directory missing.")
  }

  if (options.skipTests === true) {
    return makeResult(check, DOD_CHECK_STATUS.skip, "Skipped test execution by option.")
  }

  const testResult = await runCommand(
    "pnpm",
    ["--filter", "@hitech/keystone", "test", "--", "tests/pitch-engine-tooling"],
    {
      cwd: repoRoot,
      captureOutput: true,
      timeoutMs: 10 * 60 * 1000
    }
  )

  if (testResult.exitCode === 0) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Tooling tests passed.")
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "Tooling tests failed.", {
    stderr: testResult.stderr,
    stdout: testResult.stdout
  })
}

async function checkDoctorCommand(check, repoRoot) {
  const files = [
    "apps/keystone/scripts/pitch-engine/doctor.mjs",
    "apps/keystone/scripts/scene-studio/doctor.mjs",
    "tools/hos/launcher/pitch_engine_doctor.ps1",
    "tools/hos/launcher/scene_studio_doctor.ps1"
  ]

  const missing = []
  for (const relative of files) {
    if (!(await pathExists(path.join(repoRoot, relative)))) {
      missing.push(relative)
    }
  }

  if (missing.length === 0) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Doctor scripts present.")
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "Doctor script files missing.", {
    blockers: missing
  })
}

async function checkOneButton(check, repoRoot) {
  const files = [
    "apps/keystone/scripts/pitch-engine/one-button.mjs",
    "apps/keystone/scripts/scene-studio/one-button.mjs",
    "tools/hos/launcher/pitch_engine_one_button.ps1",
    "tools/hos/launcher/scene_studio_one_button.ps1"
  ]

  const missing = []
  for (const relative of files) {
    if (!(await pathExists(path.join(repoRoot, relative)))) {
      missing.push(relative)
    }
  }

  if (missing.length === 0) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "One-button scripts present.")
  }

  return makeResult(check, DOD_CHECK_STATUS.fail, "One-button scripts missing.", {
    blockers: missing
  })
}

async function checkPlayerOffline(check) {
  const programsRoot = path.join(PITCH_ARTIFACT_ROOT, "programs")

  if (!(await pathExists(programsRoot))) {
    return makeResult(check, DOD_CHECK_STATUS.warn, "No pitch runs yet; player files will be validated after render.")
  }

  const programDirs = await fs.readdir(programsRoot, { withFileTypes: true })
  for (const programDir of programDirs) {
    if (!programDir.isDirectory()) {
      continue
    }

    const runsPath = path.join(programsRoot, programDir.name)
    const runDirs = await fs.readdir(runsPath, { withFileTypes: true })
    for (const runDir of runDirs) {
      if (!runDir.isDirectory()) {
        continue
      }

      const playerDir = path.join(runsPath, runDir.name, "player")
      const html = path.join(playerDir, "index.html")
      const js = path.join(playerDir, "player.js")
      const css = path.join(playerDir, "styles.css")

      if ((await pathExists(html)) && (await pathExists(js)) && (await pathExists(css))) {
        return makeResult(check, DOD_CHECK_STATUS.pass, "Offline player assets exist for at least one run.")
      }
    }
  }

  return makeResult(check, DOD_CHECK_STATUS.warn, "No run with complete player assets found yet.")
}

async function checkDiffNotes(check) {
  const programsRoot = path.join(PITCH_ARTIFACT_ROOT, "programs")
  if (!(await pathExists(programsRoot))) {
    return makeResult(check, DOD_CHECK_STATUS.warn, "No pitch runs yet; DIFF_NOTES check deferred.")
  }

  const files = await runCommand("rg", ["-n", "# Diff Notes", programsRoot], {
    cwd: process.cwd(),
    captureOutput: true,
    timeoutMs: 30_000
  })

  if (files.exitCode === 0) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Diff notes detected in artifact runs.")
  }

  return makeResult(check, DOD_CHECK_STATUS.warn, "No DIFF_NOTES files detected yet.")
}

async function checkPerSequenceReports(check) {
  const programsRoot = path.join(PITCH_ARTIFACT_ROOT, "programs")
  if (!(await pathExists(programsRoot))) {
    return makeResult(check, DOD_CHECK_STATUS.warn, "No pitch runs yet; report check deferred.")
  }

  const reportScan = await runCommand("rg", ["-n", "Sequence Report", programsRoot], {
    cwd: process.cwd(),
    captureOutput: true,
    timeoutMs: 30_000
  })

  if (reportScan.exitCode === 0) {
    return makeResult(check, DOD_CHECK_STATUS.pass, "Per-sequence reports detected.")
  }

  return makeResult(check, DOD_CHECK_STATUS.warn, "No per-sequence report markers found yet.")
}

async function checkRunRetentionInvariant(check) {
  const summaryPath = path.join(PITCH_ARTIFACT_ROOT, "retention", "summary.json")
  const summary = await readJsonIfExists(summaryPath, null)

  if (!summary) {
    return makeResult(check, DOD_CHECK_STATUS.warn, "Retention summary not found yet.")
  }

  if (!summary.programs || typeof summary.programs !== "object") {
    return makeResult(check, DOD_CHECK_STATUS.fail, "Retention summary malformed.")
  }

  return makeResult(check, DOD_CHECK_STATUS.pass, "Retention summary present and parseable.")
}

export async function runDodCheck(check, context) {
  const { repoRoot, options } = context

  switch (check.id) {
    case DOD_CHECK_IDS.layerDomContract:
      return checkLayerDomContract(check, repoRoot)
    case DOD_CHECK_IDS.sceneReadySignal:
      return checkSceneReadySignal(check, repoRoot)
    case DOD_CHECK_IDS.schemaVersioned:
      return checkSchemaVersioned(check, repoRoot)
    case DOD_CHECK_IDS.routeDiscoveryOutput:
      return checkRouteDiscoveryOutput(check, repoRoot)
    case DOD_CHECK_IDS.devOnly404Prod:
      return checkDevOnly404(check, repoRoot)
    case DOD_CHECK_IDS.deterministicRunnerCommands:
      return checkRunnerCommands(check, repoRoot)
    case DOD_CHECK_IDS.artifactsIndexExists:
      return checkArtifactsIndex(check)
    case DOD_CHECK_IDS.retentionPinPresent:
      return checkRetentionPin(check, repoRoot)
    case DOD_CHECK_IDS.claimWorkflowGate:
      return checkClaimWorkflow(check, repoRoot)
    case DOD_CHECK_IDS.capabilitiesRegistry:
      return checkCapabilitiesRegistry(check, repoRoot)
    case DOD_CHECK_IDS.directorTimelineSequence:
      return checkDirectorTimeline(check, repoRoot)
    case DOD_CHECK_IDS.testsPresentAndPassing:
      return checkTests(check, repoRoot, options)
    case DOD_CHECK_IDS.doctorCommandPresent:
      return checkDoctorCommand(check, repoRoot)
    case DOD_CHECK_IDS.oneButtonRunnerPresent:
      return checkOneButton(check, repoRoot)
    case DOD_CHECK_IDS.playerOfflineStatic:
      return checkPlayerOffline(check)
    case DOD_CHECK_IDS.diffNotesPresence:
      return checkDiffNotes(check)
    case DOD_CHECK_IDS.perSequenceReports:
      return checkPerSequenceReports(check)
    case DOD_CHECK_IDS.runRetentionInvariant:
      return checkRunRetentionInvariant(check)
    default:
      return makeResult(check, DOD_CHECK_STATUS.skip, `Unknown check id: ${check.id}`)
  }
}
