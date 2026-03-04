import { describe, expect, it } from "vitest"
import { generateOfflinePlayer } from "../../lib/pitch-engine-tooling/player.mjs"
import { resolvePlayerDir } from "../../lib/pitch-engine-tooling/paths.mjs"
import { pathExists } from "../../lib/pitch-engine-tooling/fs-utils.mjs"

describe("player", () => {
  it("generates offline player bundle", async () => {
    const programId = "player-test"
    const runId = "20260304_030303_CCCC"

    const timeline = {
      hash: "abc",
      sequences: [
        {
          sequenceId: "01-double-engine",
          timestampsMs: [0, 400],
          markers: []
        }
      ]
    }

    const result = await generateOfflinePlayer(programId, runId, timeline as any)
    expect(result.files.length).toBe(3)

    const playerDir = resolvePlayerDir(programId, runId)
    expect(await pathExists(`${playerDir}/index.html`)).toBe(true)
    expect(await pathExists(`${playerDir}/player.js`)).toBe(true)
    expect(await pathExists(`${playerDir}/styles.css`)).toBe(true)
  })
})
