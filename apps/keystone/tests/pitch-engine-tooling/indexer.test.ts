import { describe, expect, it } from "vitest"
import { writePitchIndexFiles, writeSceneIndexFiles } from "../../lib/pitch-engine-tooling/indexer.mjs"
import { pathExists } from "../../lib/pitch-engine-tooling/fs-utils.mjs"
import { resolvePitchIndexPath, resolveSceneIndexPath } from "../../lib/pitch-engine-tooling/paths.mjs"

describe("indexers", () => {
  it("writes pitch index files", async () => {
    const data = await writePitchIndexFiles()
    expect(data.metadataVersion).toBe("1.0.0")
    expect(await pathExists(resolvePitchIndexPath("index.json"))).toBe(true)
    expect(await pathExists(resolvePitchIndexPath("index.md"))).toBe(true)
    expect(await pathExists(resolvePitchIndexPath("index.html"))).toBe(true)
  })

  it("writes scene index files", async () => {
    const data = await writeSceneIndexFiles()
    expect(data.metadataVersion).toBe("1.0.0")
    expect(await pathExists(resolveSceneIndexPath("index.json"))).toBe(true)
    expect(await pathExists(resolveSceneIndexPath("index.md"))).toBe(true)
    expect(await pathExists(resolveSceneIndexPath("index.html"))).toBe(true)
  })
})
