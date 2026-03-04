import {
  TIMELINE_PRESET_SCRIPTS,
  ensurePreset,
  findPresetById
} from "../../components/pitch-engine/timeline/preset-scripts";

describe("timeline preset scripts", () => {
  it("contains deterministic presets with markers and tracks", () => {
    expect(TIMELINE_PRESET_SCRIPTS.length).toBeGreaterThan(5);

    for (const preset of TIMELINE_PRESET_SCRIPTS) {
      expect(preset.durationMs).toBeGreaterThan(1000);
      expect(preset.markers.length).toBe(3);
      expect(preset.tracks.length).toBe(8);
      expect(preset.markers.map((marker) => marker.type)).toEqual(["Reveal", "Settle", "CTA"]);
    }
  });

  it("returns a preset by id and falls back safely", () => {
    const preset = findPresetById("preset-01-01");
    expect(preset).not.toBeNull();
    expect(preset?.id).toBe("preset-01-01");

    const fallback = ensurePreset("missing-preset");
    expect(fallback.id).toBe(TIMELINE_PRESET_SCRIPTS[0].id);
  });
});
