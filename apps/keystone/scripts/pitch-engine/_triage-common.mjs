import { listDirectories } from "../../lib/pitch-engine-tooling/fs-utils.mjs"
import { resolveProgramDir } from "../../lib/pitch-engine-tooling/paths.mjs"

export async function resolveLatestRunId(programId) {
  const runIds = await listDirectories(resolveProgramDir(programId))
  const candidates = runIds.filter((runId) => /^\d{8}_\d{6}_[A-Za-z0-9_-]+$/.test(runId))
  candidates.sort((a, b) => b.localeCompare(a))
  return candidates[0] ?? null
}
