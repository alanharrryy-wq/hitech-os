import { DEFAULT_PROGRAM_LIBRARY } from "../../components/pitch-engine/program-library/default-programs";

describe("default program library", () => {
  it("provides a large deterministic dataset", () => {
    expect(DEFAULT_PROGRAM_LIBRARY.length).toBe(8);

    const ids = new Set<string>();
    let totalScenes = 0;
    let totalSequences = 0;
    let totalMarkers = 0;
    let totalKeyframes = 0;

    for (const program of DEFAULT_PROGRAM_LIBRARY) {
      expect(ids.has(program.id)).toBe(false);
      ids.add(program.id);

      totalScenes += program.scenes.length;
      totalSequences += program.sequences.length;

      for (const sequence of program.sequences) {
        totalMarkers += sequence.timeline.markers.length;
        for (const track of sequence.timeline.tracks) {
          totalKeyframes += track.keyframes.length;
        }
      }
    }

    expect(totalScenes).toBe(32);
    expect(totalSequences).toBe(96);
    expect(totalMarkers).toBe(288);
    expect(totalKeyframes).toBe(1920);
  });

  it("maps each sequence to an existing scene", () => {
    for (const program of DEFAULT_PROGRAM_LIBRARY) {
      const sceneIds = new Set(program.scenes.map((scene) => scene.id));
      for (const sequence of program.sequences) {
        expect(sceneIds.has(sequence.sceneId)).toBe(true);
      }
    }
  });
});
