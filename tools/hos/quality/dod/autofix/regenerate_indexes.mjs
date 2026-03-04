import { writePitchIndexFiles, writeSceneIndexFiles } from "../../../../../apps/keystone/lib/pitch-engine-tooling/indexer.mjs"

export async function runAutofixRegenerateIndexes() {
  const pitch = await writePitchIndexFiles()
  const scene = await writeSceneIndexFiles()

  return {
    ok: true,
    id: "autofix-regenerate-indexes",
    detail: "Regenerated pitch and scene index artifacts.",
    pitchProgramCount: pitch.programCount,
    sceneTriageCount: scene.triageFiles.length
  }
}
