import { describe, expect, it } from "vitest"
import { ensureSceneOperationsLayout, requestSceneRerun, appendSceneNote } from "../../lib/pitch-engine-tooling/scene-ops.mjs"
import { pathExists } from "../../lib/pitch-engine-tooling/fs-utils.mjs"
import { resolveSceneRerunFile, resolveSceneNotesFile } from "../../lib/pitch-engine-tooling/paths.mjs"

describe("scene operations", () => {
  it("initializes scene operations layout", async () => {
    const index = await ensureSceneOperationsLayout()
    expect(index.metadataVersion).toBe("1.0.0")
  })

  it("queues rerun request", async () => {
    const result = await requestSceneRerun({ sceneId: "scene-a", actor: "test" })
    expect(result.request.status).toBe("queued")
    const exists = await pathExists(resolveSceneRerunFile("scene-a"))
    expect(exists).toBe(true)
  })

  it("appends scene note", async () => {
    const sceneId = "scene-note-a"
    const runId = "20260304_061005_61C9"
    const result = await appendSceneNote({
      sceneId,
      runId,
      actor: "test",
      note: "This is a deterministic note."
    })
    expect(result.appended).toBe(true)
    expect(await pathExists(resolveSceneNotesFile(sceneId, runId))).toBe(true)
  })
})
