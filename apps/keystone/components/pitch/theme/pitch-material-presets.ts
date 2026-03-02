export interface PitchMaterialPreset {
  readonly id: string;
  readonly tone: "gold" | "teal" | "cyan" | "brown";
  readonly gradient: string;
  readonly border: string;
  readonly glow: string;
  readonly blur: number;
  readonly noise: number;
}

export const PITCH_MATERIAL_PRESETS: readonly PitchMaterialPreset[] = [
  {
    id: "material-001",
    tone: "teal",
    gradient: "linear-gradient(11deg, rgba(171,123,38,0.12), rgba(2,167,202,0.08), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 9,
    noise: 0.045
  },
  {
    id: "material-002",
    tone: "cyan",
    gradient: "linear-gradient(22deg, rgba(171,123,38,0.13), rgba(2,167,202,0.09), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 10,
    noise: 0.05
  },
  {
    id: "material-003",
    tone: "brown",
    gradient: "linear-gradient(33deg, rgba(171,123,38,0.14), rgba(2,167,202,0.1), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 11,
    noise: 0.055
  },
  {
    id: "material-004",
    tone: "gold",
    gradient: "linear-gradient(44deg, rgba(171,123,38,0.15), rgba(2,167,202,0.11), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 12,
    noise: 0.06
  },
  {
    id: "material-005",
    tone: "teal",
    gradient: "linear-gradient(55deg, rgba(171,123,38,0.16), rgba(2,167,202,0.12), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 13,
    noise: 0.065
  },
  {
    id: "material-006",
    tone: "cyan",
    gradient: "linear-gradient(66deg, rgba(171,123,38,0.17), rgba(2,167,202,0.13), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 14,
    noise: 0.07
  },
  {
    id: "material-007",
    tone: "brown",
    gradient: "linear-gradient(77deg, rgba(171,123,38,0.18), rgba(2,167,202,0.07), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 15,
    noise: 0.075
  },
  {
    id: "material-008",
    tone: "gold",
    gradient: "linear-gradient(88deg, rgba(171,123,38,0.19), rgba(2,167,202,0.08), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 16,
    noise: 0.08
  },
  {
    id: "material-009",
    tone: "teal",
    gradient: "linear-gradient(99deg, rgba(171,123,38,0.11), rgba(2,167,202,0.09), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 17,
    noise: 0.085
  },
  {
    id: "material-010",
    tone: "cyan",
    gradient: "linear-gradient(110deg, rgba(171,123,38,0.12), rgba(2,167,202,0.1), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 18,
    noise: 0.04
  },
  {
    id: "material-011",
    tone: "brown",
    gradient: "linear-gradient(121deg, rgba(171,123,38,0.13), rgba(2,167,202,0.11), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 19,
    noise: 0.045
  },
  {
    id: "material-012",
    tone: "gold",
    gradient: "linear-gradient(132deg, rgba(171,123,38,0.14), rgba(2,167,202,0.12), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 20,
    noise: 0.05
  },
  {
    id: "material-013",
    tone: "teal",
    gradient: "linear-gradient(143deg, rgba(171,123,38,0.15), rgba(2,167,202,0.13), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 21,
    noise: 0.055
  },
  {
    id: "material-014",
    tone: "cyan",
    gradient: "linear-gradient(154deg, rgba(171,123,38,0.16), rgba(2,167,202,0.07), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 22,
    noise: 0.06
  },
  {
    id: "material-015",
    tone: "brown",
    gradient: "linear-gradient(165deg, rgba(171,123,38,0.17), rgba(2,167,202,0.08), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 23,
    noise: 0.065
  },
  {
    id: "material-016",
    tone: "gold",
    gradient: "linear-gradient(176deg, rgba(171,123,38,0.18), rgba(2,167,202,0.09), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 24,
    noise: 0.07
  },
  {
    id: "material-017",
    tone: "teal",
    gradient: "linear-gradient(187deg, rgba(171,123,38,0.19), rgba(2,167,202,0.1), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 25,
    noise: 0.075
  },
  {
    id: "material-018",
    tone: "cyan",
    gradient: "linear-gradient(198deg, rgba(171,123,38,0.11), rgba(2,167,202,0.11), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 8,
    noise: 0.08
  },
  {
    id: "material-019",
    tone: "brown",
    gradient: "linear-gradient(209deg, rgba(171,123,38,0.12), rgba(2,167,202,0.12), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 9,
    noise: 0.085
  },
  {
    id: "material-020",
    tone: "gold",
    gradient: "linear-gradient(220deg, rgba(171,123,38,0.13), rgba(2,167,202,0.13), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 10,
    noise: 0.04
  },
  {
    id: "material-021",
    tone: "teal",
    gradient: "linear-gradient(231deg, rgba(171,123,38,0.14), rgba(2,167,202,0.07), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 11,
    noise: 0.045
  },
  {
    id: "material-022",
    tone: "cyan",
    gradient: "linear-gradient(242deg, rgba(171,123,38,0.15), rgba(2,167,202,0.08), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 12,
    noise: 0.05
  },
  {
    id: "material-023",
    tone: "brown",
    gradient: "linear-gradient(253deg, rgba(171,123,38,0.16), rgba(2,167,202,0.09), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 13,
    noise: 0.055
  },
  {
    id: "material-024",
    tone: "gold",
    gradient: "linear-gradient(264deg, rgba(171,123,38,0.17), rgba(2,167,202,0.1), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 14,
    noise: 0.06
  },
  {
    id: "material-025",
    tone: "teal",
    gradient: "linear-gradient(275deg, rgba(171,123,38,0.18), rgba(2,167,202,0.11), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 15,
    noise: 0.065
  },
  {
    id: "material-026",
    tone: "cyan",
    gradient: "linear-gradient(286deg, rgba(171,123,38,0.19), rgba(2,167,202,0.12), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 16,
    noise: 0.07
  },
  {
    id: "material-027",
    tone: "brown",
    gradient: "linear-gradient(297deg, rgba(171,123,38,0.11), rgba(2,167,202,0.13), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 17,
    noise: 0.075
  },
  {
    id: "material-028",
    tone: "gold",
    gradient: "linear-gradient(308deg, rgba(171,123,38,0.12), rgba(2,167,202,0.07), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 18,
    noise: 0.08
  },
  {
    id: "material-029",
    tone: "teal",
    gradient: "linear-gradient(319deg, rgba(171,123,38,0.13), rgba(2,167,202,0.08), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 19,
    noise: 0.085
  },
  {
    id: "material-030",
    tone: "cyan",
    gradient: "linear-gradient(330deg, rgba(171,123,38,0.14), rgba(2,167,202,0.09), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 20,
    noise: 0.04
  },
  {
    id: "material-031",
    tone: "brown",
    gradient: "linear-gradient(341deg, rgba(171,123,38,0.15), rgba(2,167,202,0.1), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 21,
    noise: 0.045
  },
  {
    id: "material-032",
    tone: "gold",
    gradient: "linear-gradient(352deg, rgba(171,123,38,0.16), rgba(2,167,202,0.11), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 22,
    noise: 0.05
  },
  {
    id: "material-033",
    tone: "teal",
    gradient: "linear-gradient(3deg, rgba(171,123,38,0.17), rgba(2,167,202,0.12), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 23,
    noise: 0.055
  },
  {
    id: "material-034",
    tone: "cyan",
    gradient: "linear-gradient(14deg, rgba(171,123,38,0.18), rgba(2,167,202,0.13), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 24,
    noise: 0.06
  },
  {
    id: "material-035",
    tone: "brown",
    gradient: "linear-gradient(25deg, rgba(171,123,38,0.19), rgba(2,167,202,0.07), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 25,
    noise: 0.065
  },
  {
    id: "material-036",
    tone: "gold",
    gradient: "linear-gradient(36deg, rgba(171,123,38,0.11), rgba(2,167,202,0.08), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 8,
    noise: 0.07
  },
  {
    id: "material-037",
    tone: "teal",
    gradient: "linear-gradient(47deg, rgba(171,123,38,0.12), rgba(2,167,202,0.09), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 9,
    noise: 0.075
  },
  {
    id: "material-038",
    tone: "cyan",
    gradient: "linear-gradient(58deg, rgba(171,123,38,0.13), rgba(2,167,202,0.1), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 10,
    noise: 0.08
  },
  {
    id: "material-039",
    tone: "brown",
    gradient: "linear-gradient(69deg, rgba(171,123,38,0.14), rgba(2,167,202,0.11), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 11,
    noise: 0.085
  },
  {
    id: "material-040",
    tone: "gold",
    gradient: "linear-gradient(80deg, rgba(171,123,38,0.15), rgba(2,167,202,0.12), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 12,
    noise: 0.04
  },
  {
    id: "material-041",
    tone: "teal",
    gradient: "linear-gradient(91deg, rgba(171,123,38,0.16), rgba(2,167,202,0.13), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 13,
    noise: 0.045
  },
  {
    id: "material-042",
    tone: "cyan",
    gradient: "linear-gradient(102deg, rgba(171,123,38,0.17), rgba(2,167,202,0.07), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 14,
    noise: 0.05
  },
  {
    id: "material-043",
    tone: "brown",
    gradient: "linear-gradient(113deg, rgba(171,123,38,0.18), rgba(2,167,202,0.08), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 15,
    noise: 0.055
  },
  {
    id: "material-044",
    tone: "gold",
    gradient: "linear-gradient(124deg, rgba(171,123,38,0.19), rgba(2,167,202,0.09), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 16,
    noise: 0.06
  },
  {
    id: "material-045",
    tone: "teal",
    gradient: "linear-gradient(135deg, rgba(171,123,38,0.11), rgba(2,167,202,0.1), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 17,
    noise: 0.065
  },
  {
    id: "material-046",
    tone: "cyan",
    gradient: "linear-gradient(146deg, rgba(171,123,38,0.12), rgba(2,167,202,0.11), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 18,
    noise: 0.07
  },
  {
    id: "material-047",
    tone: "brown",
    gradient: "linear-gradient(157deg, rgba(171,123,38,0.13), rgba(2,167,202,0.12), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 19,
    noise: 0.075
  },
  {
    id: "material-048",
    tone: "gold",
    gradient: "linear-gradient(168deg, rgba(171,123,38,0.14), rgba(2,167,202,0.13), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 20,
    noise: 0.08
  },
  {
    id: "material-049",
    tone: "teal",
    gradient: "linear-gradient(179deg, rgba(171,123,38,0.15), rgba(2,167,202,0.07), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 21,
    noise: 0.085
  },
  {
    id: "material-050",
    tone: "cyan",
    gradient: "linear-gradient(190deg, rgba(171,123,38,0.16), rgba(2,167,202,0.08), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 22,
    noise: 0.04
  },
  {
    id: "material-051",
    tone: "brown",
    gradient: "linear-gradient(201deg, rgba(171,123,38,0.17), rgba(2,167,202,0.09), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 23,
    noise: 0.045
  },
  {
    id: "material-052",
    tone: "gold",
    gradient: "linear-gradient(212deg, rgba(171,123,38,0.18), rgba(2,167,202,0.1), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 24,
    noise: 0.05
  },
  {
    id: "material-053",
    tone: "teal",
    gradient: "linear-gradient(223deg, rgba(171,123,38,0.19), rgba(2,167,202,0.11), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 25,
    noise: 0.055
  },
  {
    id: "material-054",
    tone: "cyan",
    gradient: "linear-gradient(234deg, rgba(171,123,38,0.11), rgba(2,167,202,0.12), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 8,
    noise: 0.06
  },
  {
    id: "material-055",
    tone: "brown",
    gradient: "linear-gradient(245deg, rgba(171,123,38,0.12), rgba(2,167,202,0.13), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 9,
    noise: 0.065
  },
  {
    id: "material-056",
    tone: "gold",
    gradient: "linear-gradient(256deg, rgba(171,123,38,0.13), rgba(2,167,202,0.07), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 10,
    noise: 0.07
  },
  {
    id: "material-057",
    tone: "teal",
    gradient: "linear-gradient(267deg, rgba(171,123,38,0.14), rgba(2,167,202,0.08), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 11,
    noise: 0.075
  },
  {
    id: "material-058",
    tone: "cyan",
    gradient: "linear-gradient(278deg, rgba(171,123,38,0.15), rgba(2,167,202,0.09), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 12,
    noise: 0.08
  },
  {
    id: "material-059",
    tone: "brown",
    gradient: "linear-gradient(289deg, rgba(171,123,38,0.16), rgba(2,167,202,0.1), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 13,
    noise: 0.085
  },
  {
    id: "material-060",
    tone: "gold",
    gradient: "linear-gradient(300deg, rgba(171,123,38,0.17), rgba(2,167,202,0.11), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 14,
    noise: 0.04
  },
  {
    id: "material-061",
    tone: "teal",
    gradient: "linear-gradient(311deg, rgba(171,123,38,0.18), rgba(2,167,202,0.12), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 15,
    noise: 0.045
  },
  {
    id: "material-062",
    tone: "cyan",
    gradient: "linear-gradient(322deg, rgba(171,123,38,0.19), rgba(2,167,202,0.13), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 16,
    noise: 0.05
  },
  {
    id: "material-063",
    tone: "brown",
    gradient: "linear-gradient(333deg, rgba(171,123,38,0.11), rgba(2,167,202,0.07), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 17,
    noise: 0.055
  },
  {
    id: "material-064",
    tone: "gold",
    gradient: "linear-gradient(344deg, rgba(171,123,38,0.12), rgba(2,167,202,0.08), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 18,
    noise: 0.06
  },
  {
    id: "material-065",
    tone: "teal",
    gradient: "linear-gradient(355deg, rgba(171,123,38,0.13), rgba(2,167,202,0.09), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 19,
    noise: 0.065
  },
  {
    id: "material-066",
    tone: "cyan",
    gradient: "linear-gradient(6deg, rgba(171,123,38,0.14), rgba(2,167,202,0.1), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 20,
    noise: 0.07
  },
  {
    id: "material-067",
    tone: "brown",
    gradient: "linear-gradient(17deg, rgba(171,123,38,0.15), rgba(2,167,202,0.11), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 21,
    noise: 0.075
  },
  {
    id: "material-068",
    tone: "gold",
    gradient: "linear-gradient(28deg, rgba(171,123,38,0.16), rgba(2,167,202,0.12), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 22,
    noise: 0.08
  },
  {
    id: "material-069",
    tone: "teal",
    gradient: "linear-gradient(39deg, rgba(171,123,38,0.17), rgba(2,167,202,0.13), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 23,
    noise: 0.085
  },
  {
    id: "material-070",
    tone: "cyan",
    gradient: "linear-gradient(50deg, rgba(171,123,38,0.18), rgba(2,167,202,0.07), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 24,
    noise: 0.04
  },
  {
    id: "material-071",
    tone: "brown",
    gradient: "linear-gradient(61deg, rgba(171,123,38,0.19), rgba(2,167,202,0.08), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 25,
    noise: 0.045
  },
  {
    id: "material-072",
    tone: "gold",
    gradient: "linear-gradient(72deg, rgba(171,123,38,0.11), rgba(2,167,202,0.09), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 8,
    noise: 0.05
  },
  {
    id: "material-073",
    tone: "teal",
    gradient: "linear-gradient(83deg, rgba(171,123,38,0.12), rgba(2,167,202,0.1), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 9,
    noise: 0.055
  },
  {
    id: "material-074",
    tone: "cyan",
    gradient: "linear-gradient(94deg, rgba(171,123,38,0.13), rgba(2,167,202,0.11), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 10,
    noise: 0.06
  },
  {
    id: "material-075",
    tone: "brown",
    gradient: "linear-gradient(105deg, rgba(171,123,38,0.14), rgba(2,167,202,0.12), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 11,
    noise: 0.065
  },
  {
    id: "material-076",
    tone: "gold",
    gradient: "linear-gradient(116deg, rgba(171,123,38,0.15), rgba(2,167,202,0.13), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 12,
    noise: 0.07
  },
  {
    id: "material-077",
    tone: "teal",
    gradient: "linear-gradient(127deg, rgba(171,123,38,0.16), rgba(2,167,202,0.07), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 13,
    noise: 0.075
  },
  {
    id: "material-078",
    tone: "cyan",
    gradient: "linear-gradient(138deg, rgba(171,123,38,0.17), rgba(2,167,202,0.08), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 14,
    noise: 0.08
  },
  {
    id: "material-079",
    tone: "brown",
    gradient: "linear-gradient(149deg, rgba(171,123,38,0.18), rgba(2,167,202,0.09), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 15,
    noise: 0.085
  },
  {
    id: "material-080",
    tone: "gold",
    gradient: "linear-gradient(160deg, rgba(171,123,38,0.19), rgba(2,167,202,0.1), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 16,
    noise: 0.04
  },
  {
    id: "material-081",
    tone: "teal",
    gradient: "linear-gradient(171deg, rgba(171,123,38,0.11), rgba(2,167,202,0.11), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 17,
    noise: 0.045
  },
  {
    id: "material-082",
    tone: "cyan",
    gradient: "linear-gradient(182deg, rgba(171,123,38,0.12), rgba(2,167,202,0.12), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 18,
    noise: 0.05
  },
  {
    id: "material-083",
    tone: "brown",
    gradient: "linear-gradient(193deg, rgba(171,123,38,0.13), rgba(2,167,202,0.13), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 19,
    noise: 0.055
  },
  {
    id: "material-084",
    tone: "gold",
    gradient: "linear-gradient(204deg, rgba(171,123,38,0.14), rgba(2,167,202,0.07), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 20,
    noise: 0.06
  },
  {
    id: "material-085",
    tone: "teal",
    gradient: "linear-gradient(215deg, rgba(171,123,38,0.15), rgba(2,167,202,0.08), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 21,
    noise: 0.065
  },
  {
    id: "material-086",
    tone: "cyan",
    gradient: "linear-gradient(226deg, rgba(171,123,38,0.16), rgba(2,167,202,0.09), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 22,
    noise: 0.07
  },
  {
    id: "material-087",
    tone: "brown",
    gradient: "linear-gradient(237deg, rgba(171,123,38,0.17), rgba(2,167,202,0.1), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 23,
    noise: 0.075
  },
  {
    id: "material-088",
    tone: "gold",
    gradient: "linear-gradient(248deg, rgba(171,123,38,0.18), rgba(2,167,202,0.11), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 24,
    noise: 0.08
  },
  {
    id: "material-089",
    tone: "teal",
    gradient: "linear-gradient(259deg, rgba(171,123,38,0.19), rgba(2,167,202,0.12), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 25,
    noise: 0.085
  },
  {
    id: "material-090",
    tone: "cyan",
    gradient: "linear-gradient(270deg, rgba(171,123,38,0.11), rgba(2,167,202,0.13), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 8,
    noise: 0.04
  },
  {
    id: "material-091",
    tone: "brown",
    gradient: "linear-gradient(281deg, rgba(171,123,38,0.12), rgba(2,167,202,0.07), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 9,
    noise: 0.045
  },
  {
    id: "material-092",
    tone: "gold",
    gradient: "linear-gradient(292deg, rgba(171,123,38,0.13), rgba(2,167,202,0.08), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 10,
    noise: 0.05
  },
  {
    id: "material-093",
    tone: "teal",
    gradient: "linear-gradient(303deg, rgba(171,123,38,0.14), rgba(2,167,202,0.09), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 11,
    noise: 0.055
  },
  {
    id: "material-094",
    tone: "cyan",
    gradient: "linear-gradient(314deg, rgba(171,123,38,0.15), rgba(2,167,202,0.1), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 12,
    noise: 0.06
  },
  {
    id: "material-095",
    tone: "brown",
    gradient: "linear-gradient(325deg, rgba(171,123,38,0.16), rgba(2,167,202,0.11), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 13,
    noise: 0.065
  },
  {
    id: "material-096",
    tone: "gold",
    gradient: "linear-gradient(336deg, rgba(171,123,38,0.17), rgba(2,167,202,0.12), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 14,
    noise: 0.07
  },
  {
    id: "material-097",
    tone: "teal",
    gradient: "linear-gradient(347deg, rgba(171,123,38,0.18), rgba(2,167,202,0.13), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 15,
    noise: 0.075
  },
  {
    id: "material-098",
    tone: "cyan",
    gradient: "linear-gradient(358deg, rgba(171,123,38,0.19), rgba(2,167,202,0.07), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 16,
    noise: 0.08
  },
  {
    id: "material-099",
    tone: "brown",
    gradient: "linear-gradient(9deg, rgba(171,123,38,0.11), rgba(2,167,202,0.08), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 17,
    noise: 0.085
  },
  {
    id: "material-100",
    tone: "gold",
    gradient: "linear-gradient(20deg, rgba(171,123,38,0.12), rgba(2,167,202,0.09), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 18,
    noise: 0.04
  },
  {
    id: "material-101",
    tone: "teal",
    gradient: "linear-gradient(31deg, rgba(171,123,38,0.13), rgba(2,167,202,0.1), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 19,
    noise: 0.045
  },
  {
    id: "material-102",
    tone: "cyan",
    gradient: "linear-gradient(42deg, rgba(171,123,38,0.14), rgba(2,167,202,0.11), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 20,
    noise: 0.05
  },
  {
    id: "material-103",
    tone: "brown",
    gradient: "linear-gradient(53deg, rgba(171,123,38,0.15), rgba(2,167,202,0.12), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 21,
    noise: 0.055
  },
  {
    id: "material-104",
    tone: "gold",
    gradient: "linear-gradient(64deg, rgba(171,123,38,0.16), rgba(2,167,202,0.13), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 22,
    noise: 0.06
  },
  {
    id: "material-105",
    tone: "teal",
    gradient: "linear-gradient(75deg, rgba(171,123,38,0.17), rgba(2,167,202,0.07), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 23,
    noise: 0.065
  },
  {
    id: "material-106",
    tone: "cyan",
    gradient: "linear-gradient(86deg, rgba(171,123,38,0.18), rgba(2,167,202,0.08), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 24,
    noise: 0.07
  },
  {
    id: "material-107",
    tone: "brown",
    gradient: "linear-gradient(97deg, rgba(171,123,38,0.19), rgba(2,167,202,0.09), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 25,
    noise: 0.075
  },
  {
    id: "material-108",
    tone: "gold",
    gradient: "linear-gradient(108deg, rgba(171,123,38,0.11), rgba(2,167,202,0.1), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 8,
    noise: 0.08
  },
  {
    id: "material-109",
    tone: "teal",
    gradient: "linear-gradient(119deg, rgba(171,123,38,0.12), rgba(2,167,202,0.11), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 9,
    noise: 0.085
  },
  {
    id: "material-110",
    tone: "cyan",
    gradient: "linear-gradient(130deg, rgba(171,123,38,0.13), rgba(2,167,202,0.12), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 10,
    noise: 0.04
  },
  {
    id: "material-111",
    tone: "brown",
    gradient: "linear-gradient(141deg, rgba(171,123,38,0.14), rgba(2,167,202,0.13), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 11,
    noise: 0.045
  },
  {
    id: "material-112",
    tone: "gold",
    gradient: "linear-gradient(152deg, rgba(171,123,38,0.15), rgba(2,167,202,0.07), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 12,
    noise: 0.05
  },
  {
    id: "material-113",
    tone: "teal",
    gradient: "linear-gradient(163deg, rgba(171,123,38,0.16), rgba(2,167,202,0.08), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 13,
    noise: 0.055
  },
  {
    id: "material-114",
    tone: "cyan",
    gradient: "linear-gradient(174deg, rgba(171,123,38,0.17), rgba(2,167,202,0.09), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 14,
    noise: 0.06
  },
  {
    id: "material-115",
    tone: "brown",
    gradient: "linear-gradient(185deg, rgba(171,123,38,0.18), rgba(2,167,202,0.1), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 15,
    noise: 0.065
  },
  {
    id: "material-116",
    tone: "gold",
    gradient: "linear-gradient(196deg, rgba(171,123,38,0.19), rgba(2,167,202,0.11), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 16,
    noise: 0.07
  },
  {
    id: "material-117",
    tone: "teal",
    gradient: "linear-gradient(207deg, rgba(171,123,38,0.11), rgba(2,167,202,0.12), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 17,
    noise: 0.075
  },
  {
    id: "material-118",
    tone: "cyan",
    gradient: "linear-gradient(218deg, rgba(171,123,38,0.12), rgba(2,167,202,0.13), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 18,
    noise: 0.08
  },
  {
    id: "material-119",
    tone: "brown",
    gradient: "linear-gradient(229deg, rgba(171,123,38,0.13), rgba(2,167,202,0.07), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 19,
    noise: 0.085
  },
  {
    id: "material-120",
    tone: "gold",
    gradient: "linear-gradient(240deg, rgba(171,123,38,0.14), rgba(2,167,202,0.08), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 20,
    noise: 0.04
  },
  {
    id: "material-121",
    tone: "teal",
    gradient: "linear-gradient(251deg, rgba(171,123,38,0.15), rgba(2,167,202,0.09), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 21,
    noise: 0.045
  },
  {
    id: "material-122",
    tone: "cyan",
    gradient: "linear-gradient(262deg, rgba(171,123,38,0.16), rgba(2,167,202,0.1), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 22,
    noise: 0.05
  },
  {
    id: "material-123",
    tone: "brown",
    gradient: "linear-gradient(273deg, rgba(171,123,38,0.17), rgba(2,167,202,0.11), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 23,
    noise: 0.055
  },
  {
    id: "material-124",
    tone: "gold",
    gradient: "linear-gradient(284deg, rgba(171,123,38,0.18), rgba(2,167,202,0.12), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 24,
    noise: 0.06
  },
  {
    id: "material-125",
    tone: "teal",
    gradient: "linear-gradient(295deg, rgba(171,123,38,0.19), rgba(2,167,202,0.13), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 25,
    noise: 0.065
  },
  {
    id: "material-126",
    tone: "cyan",
    gradient: "linear-gradient(306deg, rgba(171,123,38,0.11), rgba(2,167,202,0.07), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 8,
    noise: 0.07
  },
  {
    id: "material-127",
    tone: "brown",
    gradient: "linear-gradient(317deg, rgba(171,123,38,0.12), rgba(2,167,202,0.08), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 9,
    noise: 0.075
  },
  {
    id: "material-128",
    tone: "gold",
    gradient: "linear-gradient(328deg, rgba(171,123,38,0.13), rgba(2,167,202,0.09), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 10,
    noise: 0.08
  },
  {
    id: "material-129",
    tone: "teal",
    gradient: "linear-gradient(339deg, rgba(171,123,38,0.14), rgba(2,167,202,0.1), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 11,
    noise: 0.085
  },
  {
    id: "material-130",
    tone: "cyan",
    gradient: "linear-gradient(350deg, rgba(171,123,38,0.15), rgba(2,167,202,0.11), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 12,
    noise: 0.04
  },
  {
    id: "material-131",
    tone: "brown",
    gradient: "linear-gradient(1deg, rgba(171,123,38,0.16), rgba(2,167,202,0.12), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 13,
    noise: 0.045
  },
  {
    id: "material-132",
    tone: "gold",
    gradient: "linear-gradient(12deg, rgba(171,123,38,0.17), rgba(2,167,202,0.13), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 14,
    noise: 0.05
  },
  {
    id: "material-133",
    tone: "teal",
    gradient: "linear-gradient(23deg, rgba(171,123,38,0.18), rgba(2,167,202,0.07), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 15,
    noise: 0.055
  },
  {
    id: "material-134",
    tone: "cyan",
    gradient: "linear-gradient(34deg, rgba(171,123,38,0.19), rgba(2,167,202,0.08), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 16,
    noise: 0.06
  },
  {
    id: "material-135",
    tone: "brown",
    gradient: "linear-gradient(45deg, rgba(171,123,38,0.11), rgba(2,167,202,0.09), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 17,
    noise: 0.065
  },
  {
    id: "material-136",
    tone: "gold",
    gradient: "linear-gradient(56deg, rgba(171,123,38,0.12), rgba(2,167,202,0.1), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 18,
    noise: 0.07
  },
  {
    id: "material-137",
    tone: "teal",
    gradient: "linear-gradient(67deg, rgba(171,123,38,0.13), rgba(2,167,202,0.11), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 19,
    noise: 0.075
  },
  {
    id: "material-138",
    tone: "cyan",
    gradient: "linear-gradient(78deg, rgba(171,123,38,0.14), rgba(2,167,202,0.12), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 20,
    noise: 0.08
  },
  {
    id: "material-139",
    tone: "brown",
    gradient: "linear-gradient(89deg, rgba(171,123,38,0.15), rgba(2,167,202,0.13), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 21,
    noise: 0.085
  },
  {
    id: "material-140",
    tone: "gold",
    gradient: "linear-gradient(100deg, rgba(171,123,38,0.16), rgba(2,167,202,0.07), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 22,
    noise: 0.04
  },
  {
    id: "material-141",
    tone: "teal",
    gradient: "linear-gradient(111deg, rgba(171,123,38,0.17), rgba(2,167,202,0.08), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 23,
    noise: 0.045
  },
  {
    id: "material-142",
    tone: "cyan",
    gradient: "linear-gradient(122deg, rgba(171,123,38,0.18), rgba(2,167,202,0.09), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 24,
    noise: 0.05
  },
  {
    id: "material-143",
    tone: "brown",
    gradient: "linear-gradient(133deg, rgba(171,123,38,0.19), rgba(2,167,202,0.1), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 25,
    noise: 0.055
  },
  {
    id: "material-144",
    tone: "gold",
    gradient: "linear-gradient(144deg, rgba(171,123,38,0.11), rgba(2,167,202,0.11), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 8,
    noise: 0.06
  },
  {
    id: "material-145",
    tone: "teal",
    gradient: "linear-gradient(155deg, rgba(171,123,38,0.12), rgba(2,167,202,0.12), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 9,
    noise: 0.065
  },
  {
    id: "material-146",
    tone: "cyan",
    gradient: "linear-gradient(166deg, rgba(171,123,38,0.13), rgba(2,167,202,0.13), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 10,
    noise: 0.07
  },
  {
    id: "material-147",
    tone: "brown",
    gradient: "linear-gradient(177deg, rgba(171,123,38,0.14), rgba(2,167,202,0.07), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 11,
    noise: 0.075
  },
  {
    id: "material-148",
    tone: "gold",
    gradient: "linear-gradient(188deg, rgba(171,123,38,0.15), rgba(2,167,202,0.08), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 12,
    noise: 0.08
  },
  {
    id: "material-149",
    tone: "teal",
    gradient: "linear-gradient(199deg, rgba(171,123,38,0.16), rgba(2,167,202,0.09), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 13,
    noise: 0.085
  },
  {
    id: "material-150",
    tone: "cyan",
    gradient: "linear-gradient(210deg, rgba(171,123,38,0.17), rgba(2,167,202,0.1), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 14,
    noise: 0.04
  },
  {
    id: "material-151",
    tone: "brown",
    gradient: "linear-gradient(221deg, rgba(171,123,38,0.18), rgba(2,167,202,0.11), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 15,
    noise: 0.045
  },
  {
    id: "material-152",
    tone: "gold",
    gradient: "linear-gradient(232deg, rgba(171,123,38,0.19), rgba(2,167,202,0.12), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 16,
    noise: 0.05
  },
  {
    id: "material-153",
    tone: "teal",
    gradient: "linear-gradient(243deg, rgba(171,123,38,0.11), rgba(2,167,202,0.13), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 17,
    noise: 0.055
  },
  {
    id: "material-154",
    tone: "cyan",
    gradient: "linear-gradient(254deg, rgba(171,123,38,0.12), rgba(2,167,202,0.07), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 18,
    noise: 0.06
  },
  {
    id: "material-155",
    tone: "brown",
    gradient: "linear-gradient(265deg, rgba(171,123,38,0.13), rgba(2,167,202,0.08), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 19,
    noise: 0.065
  },
  {
    id: "material-156",
    tone: "gold",
    gradient: "linear-gradient(276deg, rgba(171,123,38,0.14), rgba(2,167,202,0.09), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 20,
    noise: 0.07
  },
  {
    id: "material-157",
    tone: "teal",
    gradient: "linear-gradient(287deg, rgba(171,123,38,0.15), rgba(2,167,202,0.1), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 21,
    noise: 0.075
  },
  {
    id: "material-158",
    tone: "cyan",
    gradient: "linear-gradient(298deg, rgba(171,123,38,0.16), rgba(2,167,202,0.11), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 22,
    noise: 0.08
  },
  {
    id: "material-159",
    tone: "brown",
    gradient: "linear-gradient(309deg, rgba(171,123,38,0.17), rgba(2,167,202,0.12), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 23,
    noise: 0.085
  },
  {
    id: "material-160",
    tone: "gold",
    gradient: "linear-gradient(320deg, rgba(171,123,38,0.18), rgba(2,167,202,0.13), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 24,
    noise: 0.04
  },
  {
    id: "material-161",
    tone: "teal",
    gradient: "linear-gradient(331deg, rgba(171,123,38,0.19), rgba(2,167,202,0.07), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 25,
    noise: 0.045
  },
  {
    id: "material-162",
    tone: "cyan",
    gradient: "linear-gradient(342deg, rgba(171,123,38,0.11), rgba(2,167,202,0.08), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 8,
    noise: 0.05
  },
  {
    id: "material-163",
    tone: "brown",
    gradient: "linear-gradient(353deg, rgba(171,123,38,0.12), rgba(2,167,202,0.09), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 9,
    noise: 0.055
  },
  {
    id: "material-164",
    tone: "gold",
    gradient: "linear-gradient(4deg, rgba(171,123,38,0.13), rgba(2,167,202,0.1), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 10,
    noise: 0.06
  },
  {
    id: "material-165",
    tone: "teal",
    gradient: "linear-gradient(15deg, rgba(171,123,38,0.14), rgba(2,167,202,0.11), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 11,
    noise: 0.065
  },
  {
    id: "material-166",
    tone: "cyan",
    gradient: "linear-gradient(26deg, rgba(171,123,38,0.15), rgba(2,167,202,0.12), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 12,
    noise: 0.07
  },
  {
    id: "material-167",
    tone: "brown",
    gradient: "linear-gradient(37deg, rgba(171,123,38,0.16), rgba(2,167,202,0.13), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 13,
    noise: 0.075
  },
  {
    id: "material-168",
    tone: "gold",
    gradient: "linear-gradient(48deg, rgba(171,123,38,0.17), rgba(2,167,202,0.07), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 14,
    noise: 0.08
  },
  {
    id: "material-169",
    tone: "teal",
    gradient: "linear-gradient(59deg, rgba(171,123,38,0.18), rgba(2,167,202,0.08), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 15,
    noise: 0.085
  },
  {
    id: "material-170",
    tone: "cyan",
    gradient: "linear-gradient(70deg, rgba(171,123,38,0.19), rgba(2,167,202,0.09), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 16,
    noise: 0.04
  },
  {
    id: "material-171",
    tone: "brown",
    gradient: "linear-gradient(81deg, rgba(171,123,38,0.11), rgba(2,167,202,0.1), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 17,
    noise: 0.045
  },
  {
    id: "material-172",
    tone: "gold",
    gradient: "linear-gradient(92deg, rgba(171,123,38,0.12), rgba(2,167,202,0.11), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 18,
    noise: 0.05
  },
  {
    id: "material-173",
    tone: "teal",
    gradient: "linear-gradient(103deg, rgba(171,123,38,0.13), rgba(2,167,202,0.12), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 19,
    noise: 0.055
  },
  {
    id: "material-174",
    tone: "cyan",
    gradient: "linear-gradient(114deg, rgba(171,123,38,0.14), rgba(2,167,202,0.13), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 20,
    noise: 0.06
  },
  {
    id: "material-175",
    tone: "brown",
    gradient: "linear-gradient(125deg, rgba(171,123,38,0.15), rgba(2,167,202,0.07), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 21,
    noise: 0.065
  },
  {
    id: "material-176",
    tone: "gold",
    gradient: "linear-gradient(136deg, rgba(171,123,38,0.16), rgba(2,167,202,0.08), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 22,
    noise: 0.07
  },
  {
    id: "material-177",
    tone: "teal",
    gradient: "linear-gradient(147deg, rgba(171,123,38,0.17), rgba(2,167,202,0.09), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 23,
    noise: 0.075
  },
  {
    id: "material-178",
    tone: "cyan",
    gradient: "linear-gradient(158deg, rgba(171,123,38,0.18), rgba(2,167,202,0.1), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 24,
    noise: 0.08
  },
  {
    id: "material-179",
    tone: "brown",
    gradient: "linear-gradient(169deg, rgba(171,123,38,0.19), rgba(2,167,202,0.11), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 25,
    noise: 0.085
  },
  {
    id: "material-180",
    tone: "gold",
    gradient: "linear-gradient(180deg, rgba(171,123,38,0.11), rgba(2,167,202,0.12), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 8,
    noise: 0.04
  },
  {
    id: "material-181",
    tone: "teal",
    gradient: "linear-gradient(191deg, rgba(171,123,38,0.12), rgba(2,167,202,0.13), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 9,
    noise: 0.045
  },
  {
    id: "material-182",
    tone: "cyan",
    gradient: "linear-gradient(202deg, rgba(171,123,38,0.13), rgba(2,167,202,0.07), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 10,
    noise: 0.05
  },
  {
    id: "material-183",
    tone: "brown",
    gradient: "linear-gradient(213deg, rgba(171,123,38,0.14), rgba(2,167,202,0.08), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 11,
    noise: 0.055
  },
  {
    id: "material-184",
    tone: "gold",
    gradient: "linear-gradient(224deg, rgba(171,123,38,0.15), rgba(2,167,202,0.09), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 12,
    noise: 0.06
  },
  {
    id: "material-185",
    tone: "teal",
    gradient: "linear-gradient(235deg, rgba(171,123,38,0.16), rgba(2,167,202,0.1), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 13,
    noise: 0.065
  },
  {
    id: "material-186",
    tone: "cyan",
    gradient: "linear-gradient(246deg, rgba(171,123,38,0.17), rgba(2,167,202,0.11), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 14,
    noise: 0.07
  },
  {
    id: "material-187",
    tone: "brown",
    gradient: "linear-gradient(257deg, rgba(171,123,38,0.18), rgba(2,167,202,0.12), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 15,
    noise: 0.075
  },
  {
    id: "material-188",
    tone: "gold",
    gradient: "linear-gradient(268deg, rgba(171,123,38,0.19), rgba(2,167,202,0.13), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 16,
    noise: 0.08
  },
  {
    id: "material-189",
    tone: "teal",
    gradient: "linear-gradient(279deg, rgba(171,123,38,0.11), rgba(2,167,202,0.07), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 17,
    noise: 0.085
  },
  {
    id: "material-190",
    tone: "cyan",
    gradient: "linear-gradient(290deg, rgba(171,123,38,0.12), rgba(2,167,202,0.08), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 18,
    noise: 0.04
  },
  {
    id: "material-191",
    tone: "brown",
    gradient: "linear-gradient(301deg, rgba(171,123,38,0.13), rgba(2,167,202,0.09), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 19,
    noise: 0.045
  },
  {
    id: "material-192",
    tone: "gold",
    gradient: "linear-gradient(312deg, rgba(171,123,38,0.14), rgba(2,167,202,0.1), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 20,
    noise: 0.05
  },
  {
    id: "material-193",
    tone: "teal",
    gradient: "linear-gradient(323deg, rgba(171,123,38,0.15), rgba(2,167,202,0.11), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 21,
    noise: 0.055
  },
  {
    id: "material-194",
    tone: "cyan",
    gradient: "linear-gradient(334deg, rgba(171,123,38,0.16), rgba(2,167,202,0.12), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 22,
    noise: 0.06
  },
  {
    id: "material-195",
    tone: "brown",
    gradient: "linear-gradient(345deg, rgba(171,123,38,0.17), rgba(2,167,202,0.13), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 23,
    noise: 0.065
  },
  {
    id: "material-196",
    tone: "gold",
    gradient: "linear-gradient(356deg, rgba(171,123,38,0.18), rgba(2,167,202,0.07), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 24,
    noise: 0.07
  },
  {
    id: "material-197",
    tone: "teal",
    gradient: "linear-gradient(7deg, rgba(171,123,38,0.19), rgba(2,167,202,0.08), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 25,
    noise: 0.075
  },
  {
    id: "material-198",
    tone: "cyan",
    gradient: "linear-gradient(18deg, rgba(171,123,38,0.11), rgba(2,167,202,0.09), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 8,
    noise: 0.08
  },
  {
    id: "material-199",
    tone: "brown",
    gradient: "linear-gradient(29deg, rgba(171,123,38,0.12), rgba(2,167,202,0.1), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 9,
    noise: 0.085
  },
  {
    id: "material-200",
    tone: "gold",
    gradient: "linear-gradient(40deg, rgba(171,123,38,0.13), rgba(2,167,202,0.11), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 10,
    noise: 0.04
  },
  {
    id: "material-201",
    tone: "teal",
    gradient: "linear-gradient(51deg, rgba(171,123,38,0.14), rgba(2,167,202,0.12), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 11,
    noise: 0.045
  },
  {
    id: "material-202",
    tone: "cyan",
    gradient: "linear-gradient(62deg, rgba(171,123,38,0.15), rgba(2,167,202,0.13), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 12,
    noise: 0.05
  },
  {
    id: "material-203",
    tone: "brown",
    gradient: "linear-gradient(73deg, rgba(171,123,38,0.16), rgba(2,167,202,0.07), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 13,
    noise: 0.055
  },
  {
    id: "material-204",
    tone: "gold",
    gradient: "linear-gradient(84deg, rgba(171,123,38,0.17), rgba(2,167,202,0.08), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 14,
    noise: 0.06
  },
  {
    id: "material-205",
    tone: "teal",
    gradient: "linear-gradient(95deg, rgba(171,123,38,0.18), rgba(2,167,202,0.09), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 15,
    noise: 0.065
  },
  {
    id: "material-206",
    tone: "cyan",
    gradient: "linear-gradient(106deg, rgba(171,123,38,0.19), rgba(2,167,202,0.1), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 16,
    noise: 0.07
  },
  {
    id: "material-207",
    tone: "brown",
    gradient: "linear-gradient(117deg, rgba(171,123,38,0.11), rgba(2,167,202,0.11), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 17,
    noise: 0.075
  },
  {
    id: "material-208",
    tone: "gold",
    gradient: "linear-gradient(128deg, rgba(171,123,38,0.12), rgba(2,167,202,0.12), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 18,
    noise: 0.08
  },
  {
    id: "material-209",
    tone: "teal",
    gradient: "linear-gradient(139deg, rgba(171,123,38,0.13), rgba(2,167,202,0.13), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 19,
    noise: 0.085
  },
  {
    id: "material-210",
    tone: "cyan",
    gradient: "linear-gradient(150deg, rgba(171,123,38,0.14), rgba(2,167,202,0.07), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 20,
    noise: 0.04
  },
  {
    id: "material-211",
    tone: "brown",
    gradient: "linear-gradient(161deg, rgba(171,123,38,0.15), rgba(2,167,202,0.08), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 21,
    noise: 0.045
  },
  {
    id: "material-212",
    tone: "gold",
    gradient: "linear-gradient(172deg, rgba(171,123,38,0.16), rgba(2,167,202,0.09), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 22,
    noise: 0.05
  },
  {
    id: "material-213",
    tone: "teal",
    gradient: "linear-gradient(183deg, rgba(171,123,38,0.17), rgba(2,167,202,0.1), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 23,
    noise: 0.055
  },
  {
    id: "material-214",
    tone: "cyan",
    gradient: "linear-gradient(194deg, rgba(171,123,38,0.18), rgba(2,167,202,0.11), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 24,
    noise: 0.06
  },
  {
    id: "material-215",
    tone: "brown",
    gradient: "linear-gradient(205deg, rgba(171,123,38,0.19), rgba(2,167,202,0.12), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 25,
    noise: 0.065
  },
  {
    id: "material-216",
    tone: "gold",
    gradient: "linear-gradient(216deg, rgba(171,123,38,0.11), rgba(2,167,202,0.13), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 8,
    noise: 0.07
  },
  {
    id: "material-217",
    tone: "teal",
    gradient: "linear-gradient(227deg, rgba(171,123,38,0.12), rgba(2,167,202,0.07), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 9,
    noise: 0.075
  },
  {
    id: "material-218",
    tone: "cyan",
    gradient: "linear-gradient(238deg, rgba(171,123,38,0.13), rgba(2,167,202,0.08), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 10,
    noise: 0.08
  },
  {
    id: "material-219",
    tone: "brown",
    gradient: "linear-gradient(249deg, rgba(171,123,38,0.14), rgba(2,167,202,0.09), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 11,
    noise: 0.085
  },
  {
    id: "material-220",
    tone: "gold",
    gradient: "linear-gradient(260deg, rgba(171,123,38,0.15), rgba(2,167,202,0.1), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 12,
    noise: 0.04
  },
  {
    id: "material-221",
    tone: "teal",
    gradient: "linear-gradient(271deg, rgba(171,123,38,0.16), rgba(2,167,202,0.11), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 13,
    noise: 0.045
  },
  {
    id: "material-222",
    tone: "cyan",
    gradient: "linear-gradient(282deg, rgba(171,123,38,0.17), rgba(2,167,202,0.12), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 14,
    noise: 0.05
  },
  {
    id: "material-223",
    tone: "brown",
    gradient: "linear-gradient(293deg, rgba(171,123,38,0.18), rgba(2,167,202,0.13), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 15,
    noise: 0.055
  },
  {
    id: "material-224",
    tone: "gold",
    gradient: "linear-gradient(304deg, rgba(171,123,38,0.19), rgba(2,167,202,0.07), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 16,
    noise: 0.06
  },
  {
    id: "material-225",
    tone: "teal",
    gradient: "linear-gradient(315deg, rgba(171,123,38,0.11), rgba(2,167,202,0.08), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 17,
    noise: 0.065
  },
  {
    id: "material-226",
    tone: "cyan",
    gradient: "linear-gradient(326deg, rgba(171,123,38,0.12), rgba(2,167,202,0.09), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 18,
    noise: 0.07
  },
  {
    id: "material-227",
    tone: "brown",
    gradient: "linear-gradient(337deg, rgba(171,123,38,0.13), rgba(2,167,202,0.1), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 19,
    noise: 0.075
  },
  {
    id: "material-228",
    tone: "gold",
    gradient: "linear-gradient(348deg, rgba(171,123,38,0.14), rgba(2,167,202,0.11), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 20,
    noise: 0.08
  },
  {
    id: "material-229",
    tone: "teal",
    gradient: "linear-gradient(359deg, rgba(171,123,38,0.15), rgba(2,167,202,0.12), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 21,
    noise: 0.085
  },
  {
    id: "material-230",
    tone: "cyan",
    gradient: "linear-gradient(10deg, rgba(171,123,38,0.16), rgba(2,167,202,0.13), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 22,
    noise: 0.04
  },
  {
    id: "material-231",
    tone: "brown",
    gradient: "linear-gradient(21deg, rgba(171,123,38,0.17), rgba(2,167,202,0.07), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 23,
    noise: 0.045
  },
  {
    id: "material-232",
    tone: "gold",
    gradient: "linear-gradient(32deg, rgba(171,123,38,0.18), rgba(2,167,202,0.08), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 24,
    noise: 0.05
  },
  {
    id: "material-233",
    tone: "teal",
    gradient: "linear-gradient(43deg, rgba(171,123,38,0.19), rgba(2,167,202,0.09), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 25,
    noise: 0.055
  },
  {
    id: "material-234",
    tone: "cyan",
    gradient: "linear-gradient(54deg, rgba(171,123,38,0.11), rgba(2,167,202,0.1), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 8,
    noise: 0.06
  },
  {
    id: "material-235",
    tone: "brown",
    gradient: "linear-gradient(65deg, rgba(171,123,38,0.12), rgba(2,167,202,0.11), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 9,
    noise: 0.065
  },
  {
    id: "material-236",
    tone: "gold",
    gradient: "linear-gradient(76deg, rgba(171,123,38,0.13), rgba(2,167,202,0.12), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 10,
    noise: 0.07
  },
  {
    id: "material-237",
    tone: "teal",
    gradient: "linear-gradient(87deg, rgba(171,123,38,0.14), rgba(2,167,202,0.13), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 11,
    noise: 0.075
  },
  {
    id: "material-238",
    tone: "cyan",
    gradient: "linear-gradient(98deg, rgba(171,123,38,0.15), rgba(2,167,202,0.07), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 12,
    noise: 0.08
  },
  {
    id: "material-239",
    tone: "brown",
    gradient: "linear-gradient(109deg, rgba(171,123,38,0.16), rgba(2,167,202,0.08), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 13,
    noise: 0.085
  },
  {
    id: "material-240",
    tone: "gold",
    gradient: "linear-gradient(120deg, rgba(171,123,38,0.17), rgba(2,167,202,0.09), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 14,
    noise: 0.04
  },
  {
    id: "material-241",
    tone: "teal",
    gradient: "linear-gradient(131deg, rgba(171,123,38,0.18), rgba(2,167,202,0.1), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 15,
    noise: 0.045
  },
  {
    id: "material-242",
    tone: "cyan",
    gradient: "linear-gradient(142deg, rgba(171,123,38,0.19), rgba(2,167,202,0.11), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 16,
    noise: 0.05
  },
  {
    id: "material-243",
    tone: "brown",
    gradient: "linear-gradient(153deg, rgba(171,123,38,0.11), rgba(2,167,202,0.12), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 17,
    noise: 0.055
  },
  {
    id: "material-244",
    tone: "gold",
    gradient: "linear-gradient(164deg, rgba(171,123,38,0.12), rgba(2,167,202,0.13), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 18,
    noise: 0.06
  },
  {
    id: "material-245",
    tone: "teal",
    gradient: "linear-gradient(175deg, rgba(171,123,38,0.13), rgba(2,167,202,0.07), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 19,
    noise: 0.065
  },
  {
    id: "material-246",
    tone: "cyan",
    gradient: "linear-gradient(186deg, rgba(171,123,38,0.14), rgba(2,167,202,0.08), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 20,
    noise: 0.07
  },
  {
    id: "material-247",
    tone: "brown",
    gradient: "linear-gradient(197deg, rgba(171,123,38,0.15), rgba(2,167,202,0.09), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 21,
    noise: 0.075
  },
  {
    id: "material-248",
    tone: "gold",
    gradient: "linear-gradient(208deg, rgba(171,123,38,0.16), rgba(2,167,202,0.1), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 22,
    noise: 0.08
  },
  {
    id: "material-249",
    tone: "teal",
    gradient: "linear-gradient(219deg, rgba(171,123,38,0.17), rgba(2,167,202,0.11), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 23,
    noise: 0.085
  },
  {
    id: "material-250",
    tone: "cyan",
    gradient: "linear-gradient(230deg, rgba(171,123,38,0.18), rgba(2,167,202,0.12), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 24,
    noise: 0.04
  },
  {
    id: "material-251",
    tone: "brown",
    gradient: "linear-gradient(241deg, rgba(171,123,38,0.19), rgba(2,167,202,0.13), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 25,
    noise: 0.045
  },
  {
    id: "material-252",
    tone: "gold",
    gradient: "linear-gradient(252deg, rgba(171,123,38,0.11), rgba(2,167,202,0.07), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 8,
    noise: 0.05
  },
  {
    id: "material-253",
    tone: "teal",
    gradient: "linear-gradient(263deg, rgba(171,123,38,0.12), rgba(2,167,202,0.08), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 9,
    noise: 0.055
  },
  {
    id: "material-254",
    tone: "cyan",
    gradient: "linear-gradient(274deg, rgba(171,123,38,0.13), rgba(2,167,202,0.09), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 10,
    noise: 0.06
  },
  {
    id: "material-255",
    tone: "brown",
    gradient: "linear-gradient(285deg, rgba(171,123,38,0.14), rgba(2,167,202,0.1), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 11,
    noise: 0.065
  },
  {
    id: "material-256",
    tone: "gold",
    gradient: "linear-gradient(296deg, rgba(171,123,38,0.15), rgba(2,167,202,0.11), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 12,
    noise: 0.07
  },
  {
    id: "material-257",
    tone: "teal",
    gradient: "linear-gradient(307deg, rgba(171,123,38,0.16), rgba(2,167,202,0.12), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 13,
    noise: 0.075
  },
  {
    id: "material-258",
    tone: "cyan",
    gradient: "linear-gradient(318deg, rgba(171,123,38,0.17), rgba(2,167,202,0.13), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 14,
    noise: 0.08
  },
  {
    id: "material-259",
    tone: "brown",
    gradient: "linear-gradient(329deg, rgba(171,123,38,0.18), rgba(2,167,202,0.07), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 15,
    noise: 0.085
  },
  {
    id: "material-260",
    tone: "gold",
    gradient: "linear-gradient(340deg, rgba(171,123,38,0.19), rgba(2,167,202,0.08), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 16,
    noise: 0.04
  },
  {
    id: "material-261",
    tone: "teal",
    gradient: "linear-gradient(351deg, rgba(171,123,38,0.11), rgba(2,167,202,0.09), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 17,
    noise: 0.045
  },
  {
    id: "material-262",
    tone: "cyan",
    gradient: "linear-gradient(2deg, rgba(171,123,38,0.12), rgba(2,167,202,0.1), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 18,
    noise: 0.05
  },
  {
    id: "material-263",
    tone: "brown",
    gradient: "linear-gradient(13deg, rgba(171,123,38,0.13), rgba(2,167,202,0.11), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 19,
    noise: 0.055
  },
  {
    id: "material-264",
    tone: "gold",
    gradient: "linear-gradient(24deg, rgba(171,123,38,0.14), rgba(2,167,202,0.12), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 20,
    noise: 0.06
  },
  {
    id: "material-265",
    tone: "teal",
    gradient: "linear-gradient(35deg, rgba(171,123,38,0.15), rgba(2,167,202,0.13), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 21,
    noise: 0.065
  },
  {
    id: "material-266",
    tone: "cyan",
    gradient: "linear-gradient(46deg, rgba(171,123,38,0.16), rgba(2,167,202,0.07), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 22,
    noise: 0.07
  },
  {
    id: "material-267",
    tone: "brown",
    gradient: "linear-gradient(57deg, rgba(171,123,38,0.17), rgba(2,167,202,0.08), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 23,
    noise: 0.075
  },
  {
    id: "material-268",
    tone: "gold",
    gradient: "linear-gradient(68deg, rgba(171,123,38,0.18), rgba(2,167,202,0.09), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 24,
    noise: 0.08
  },
  {
    id: "material-269",
    tone: "teal",
    gradient: "linear-gradient(79deg, rgba(171,123,38,0.19), rgba(2,167,202,0.1), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 25,
    noise: 0.085
  },
  {
    id: "material-270",
    tone: "cyan",
    gradient: "linear-gradient(90deg, rgba(171,123,38,0.11), rgba(2,167,202,0.11), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 8,
    noise: 0.04
  },
  {
    id: "material-271",
    tone: "brown",
    gradient: "linear-gradient(101deg, rgba(171,123,38,0.12), rgba(2,167,202,0.12), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 9,
    noise: 0.045
  },
  {
    id: "material-272",
    tone: "gold",
    gradient: "linear-gradient(112deg, rgba(171,123,38,0.13), rgba(2,167,202,0.13), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 10,
    noise: 0.05
  },
  {
    id: "material-273",
    tone: "teal",
    gradient: "linear-gradient(123deg, rgba(171,123,38,0.14), rgba(2,167,202,0.07), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 11,
    noise: 0.055
  },
  {
    id: "material-274",
    tone: "cyan",
    gradient: "linear-gradient(134deg, rgba(171,123,38,0.15), rgba(2,167,202,0.08), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 12,
    noise: 0.06
  },
  {
    id: "material-275",
    tone: "brown",
    gradient: "linear-gradient(145deg, rgba(171,123,38,0.16), rgba(2,167,202,0.09), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 13,
    noise: 0.065
  },
  {
    id: "material-276",
    tone: "gold",
    gradient: "linear-gradient(156deg, rgba(171,123,38,0.17), rgba(2,167,202,0.1), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 14,
    noise: 0.07
  },
  {
    id: "material-277",
    tone: "teal",
    gradient: "linear-gradient(167deg, rgba(171,123,38,0.18), rgba(2,167,202,0.11), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 15,
    noise: 0.075
  },
  {
    id: "material-278",
    tone: "cyan",
    gradient: "linear-gradient(178deg, rgba(171,123,38,0.19), rgba(2,167,202,0.12), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 16,
    noise: 0.08
  },
  {
    id: "material-279",
    tone: "brown",
    gradient: "linear-gradient(189deg, rgba(171,123,38,0.11), rgba(2,167,202,0.13), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 17,
    noise: 0.085
  },
  {
    id: "material-280",
    tone: "gold",
    gradient: "linear-gradient(200deg, rgba(171,123,38,0.12), rgba(2,167,202,0.07), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 18,
    noise: 0.04
  },
  {
    id: "material-281",
    tone: "teal",
    gradient: "linear-gradient(211deg, rgba(171,123,38,0.13), rgba(2,167,202,0.08), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 19,
    noise: 0.045
  },
  {
    id: "material-282",
    tone: "cyan",
    gradient: "linear-gradient(222deg, rgba(171,123,38,0.14), rgba(2,167,202,0.09), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 20,
    noise: 0.05
  },
  {
    id: "material-283",
    tone: "brown",
    gradient: "linear-gradient(233deg, rgba(171,123,38,0.15), rgba(2,167,202,0.1), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 21,
    noise: 0.055
  },
  {
    id: "material-284",
    tone: "gold",
    gradient: "linear-gradient(244deg, rgba(171,123,38,0.16), rgba(2,167,202,0.11), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 22,
    noise: 0.06
  },
  {
    id: "material-285",
    tone: "teal",
    gradient: "linear-gradient(255deg, rgba(171,123,38,0.17), rgba(2,167,202,0.12), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 23,
    noise: 0.065
  },
  {
    id: "material-286",
    tone: "cyan",
    gradient: "linear-gradient(266deg, rgba(171,123,38,0.18), rgba(2,167,202,0.13), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 24,
    noise: 0.07
  },
  {
    id: "material-287",
    tone: "brown",
    gradient: "linear-gradient(277deg, rgba(171,123,38,0.19), rgba(2,167,202,0.07), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 25,
    noise: 0.075
  },
  {
    id: "material-288",
    tone: "gold",
    gradient: "linear-gradient(288deg, rgba(171,123,38,0.11), rgba(2,167,202,0.08), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 8,
    noise: 0.08
  },
  {
    id: "material-289",
    tone: "teal",
    gradient: "linear-gradient(299deg, rgba(171,123,38,0.12), rgba(2,167,202,0.09), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 9,
    noise: 0.085
  },
  {
    id: "material-290",
    tone: "cyan",
    gradient: "linear-gradient(310deg, rgba(171,123,38,0.13), rgba(2,167,202,0.1), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 10,
    noise: 0.04
  },
  {
    id: "material-291",
    tone: "brown",
    gradient: "linear-gradient(321deg, rgba(171,123,38,0.14), rgba(2,167,202,0.11), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 11,
    noise: 0.045
  },
  {
    id: "material-292",
    tone: "gold",
    gradient: "linear-gradient(332deg, rgba(171,123,38,0.15), rgba(2,167,202,0.12), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 12,
    noise: 0.05
  },
  {
    id: "material-293",
    tone: "teal",
    gradient: "linear-gradient(343deg, rgba(171,123,38,0.16), rgba(2,167,202,0.13), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 13,
    noise: 0.055
  },
  {
    id: "material-294",
    tone: "cyan",
    gradient: "linear-gradient(354deg, rgba(171,123,38,0.17), rgba(2,167,202,0.07), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 14,
    noise: 0.06
  },
  {
    id: "material-295",
    tone: "brown",
    gradient: "linear-gradient(5deg, rgba(171,123,38,0.18), rgba(2,167,202,0.08), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 15,
    noise: 0.065
  },
  {
    id: "material-296",
    tone: "gold",
    gradient: "linear-gradient(16deg, rgba(171,123,38,0.19), rgba(2,167,202,0.09), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 16,
    noise: 0.07
  },
  {
    id: "material-297",
    tone: "teal",
    gradient: "linear-gradient(27deg, rgba(171,123,38,0.11), rgba(2,167,202,0.1), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 17,
    noise: 0.075
  },
  {
    id: "material-298",
    tone: "cyan",
    gradient: "linear-gradient(38deg, rgba(171,123,38,0.12), rgba(2,167,202,0.11), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 18,
    noise: 0.08
  },
  {
    id: "material-299",
    tone: "brown",
    gradient: "linear-gradient(49deg, rgba(171,123,38,0.13), rgba(2,167,202,0.12), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 19,
    noise: 0.085
  },
  {
    id: "material-300",
    tone: "gold",
    gradient: "linear-gradient(60deg, rgba(171,123,38,0.14), rgba(2,167,202,0.13), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 20,
    noise: 0.04
  },
  {
    id: "material-301",
    tone: "teal",
    gradient: "linear-gradient(71deg, rgba(171,123,38,0.15), rgba(2,167,202,0.07), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 21,
    noise: 0.045
  },
  {
    id: "material-302",
    tone: "cyan",
    gradient: "linear-gradient(82deg, rgba(171,123,38,0.16), rgba(2,167,202,0.08), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 22,
    noise: 0.05
  },
  {
    id: "material-303",
    tone: "brown",
    gradient: "linear-gradient(93deg, rgba(171,123,38,0.17), rgba(2,167,202,0.09), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 23,
    noise: 0.055
  },
  {
    id: "material-304",
    tone: "gold",
    gradient: "linear-gradient(104deg, rgba(171,123,38,0.18), rgba(2,167,202,0.1), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 24,
    noise: 0.06
  },
  {
    id: "material-305",
    tone: "teal",
    gradient: "linear-gradient(115deg, rgba(171,123,38,0.19), rgba(2,167,202,0.11), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 25,
    noise: 0.065
  },
  {
    id: "material-306",
    tone: "cyan",
    gradient: "linear-gradient(126deg, rgba(171,123,38,0.11), rgba(2,167,202,0.12), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 8,
    noise: 0.07
  },
  {
    id: "material-307",
    tone: "brown",
    gradient: "linear-gradient(137deg, rgba(171,123,38,0.12), rgba(2,167,202,0.13), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 9,
    noise: 0.075
  },
  {
    id: "material-308",
    tone: "gold",
    gradient: "linear-gradient(148deg, rgba(171,123,38,0.13), rgba(2,167,202,0.07), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 10,
    noise: 0.08
  },
  {
    id: "material-309",
    tone: "teal",
    gradient: "linear-gradient(159deg, rgba(171,123,38,0.14), rgba(2,167,202,0.08), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 11,
    noise: 0.085
  },
  {
    id: "material-310",
    tone: "cyan",
    gradient: "linear-gradient(170deg, rgba(171,123,38,0.15), rgba(2,167,202,0.09), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 12,
    noise: 0.04
  },
  {
    id: "material-311",
    tone: "brown",
    gradient: "linear-gradient(181deg, rgba(171,123,38,0.16), rgba(2,167,202,0.1), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 13,
    noise: 0.045
  },
  {
    id: "material-312",
    tone: "gold",
    gradient: "linear-gradient(192deg, rgba(171,123,38,0.17), rgba(2,167,202,0.11), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 14,
    noise: 0.05
  },
  {
    id: "material-313",
    tone: "teal",
    gradient: "linear-gradient(203deg, rgba(171,123,38,0.18), rgba(2,167,202,0.12), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 15,
    noise: 0.055
  },
  {
    id: "material-314",
    tone: "cyan",
    gradient: "linear-gradient(214deg, rgba(171,123,38,0.19), rgba(2,167,202,0.13), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 16,
    noise: 0.06
  },
  {
    id: "material-315",
    tone: "brown",
    gradient: "linear-gradient(225deg, rgba(171,123,38,0.11), rgba(2,167,202,0.07), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 17,
    noise: 0.065
  },
  {
    id: "material-316",
    tone: "gold",
    gradient: "linear-gradient(236deg, rgba(171,123,38,0.12), rgba(2,167,202,0.08), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 18,
    noise: 0.07
  },
  {
    id: "material-317",
    tone: "teal",
    gradient: "linear-gradient(247deg, rgba(171,123,38,0.13), rgba(2,167,202,0.09), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 19,
    noise: 0.075
  },
  {
    id: "material-318",
    tone: "cyan",
    gradient: "linear-gradient(258deg, rgba(171,123,38,0.14), rgba(2,167,202,0.1), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 20,
    noise: 0.08
  },
  {
    id: "material-319",
    tone: "brown",
    gradient: "linear-gradient(269deg, rgba(171,123,38,0.15), rgba(2,167,202,0.11), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 21,
    noise: 0.085
  },
  {
    id: "material-320",
    tone: "gold",
    gradient: "linear-gradient(280deg, rgba(171,123,38,0.16), rgba(2,167,202,0.12), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 22,
    noise: 0.04
  },
  {
    id: "material-321",
    tone: "teal",
    gradient: "linear-gradient(291deg, rgba(171,123,38,0.17), rgba(2,167,202,0.13), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 23,
    noise: 0.045
  },
  {
    id: "material-322",
    tone: "cyan",
    gradient: "linear-gradient(302deg, rgba(171,123,38,0.18), rgba(2,167,202,0.07), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 24,
    noise: 0.05
  },
  {
    id: "material-323",
    tone: "brown",
    gradient: "linear-gradient(313deg, rgba(171,123,38,0.19), rgba(2,167,202,0.08), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 25,
    noise: 0.055
  },
  {
    id: "material-324",
    tone: "gold",
    gradient: "linear-gradient(324deg, rgba(171,123,38,0.11), rgba(2,167,202,0.09), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 8,
    noise: 0.06
  },
  {
    id: "material-325",
    tone: "teal",
    gradient: "linear-gradient(335deg, rgba(171,123,38,0.12), rgba(2,167,202,0.1), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 9,
    noise: 0.065
  },
  {
    id: "material-326",
    tone: "cyan",
    gradient: "linear-gradient(346deg, rgba(171,123,38,0.13), rgba(2,167,202,0.11), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 10,
    noise: 0.07
  },
  {
    id: "material-327",
    tone: "brown",
    gradient: "linear-gradient(357deg, rgba(171,123,38,0.14), rgba(2,167,202,0.12), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 11,
    noise: 0.075
  },
  {
    id: "material-328",
    tone: "gold",
    gradient: "linear-gradient(8deg, rgba(171,123,38,0.15), rgba(2,167,202,0.13), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 12,
    noise: 0.08
  },
  {
    id: "material-329",
    tone: "teal",
    gradient: "linear-gradient(19deg, rgba(171,123,38,0.16), rgba(2,167,202,0.07), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 13,
    noise: 0.085
  },
  {
    id: "material-330",
    tone: "cyan",
    gradient: "linear-gradient(30deg, rgba(171,123,38,0.17), rgba(2,167,202,0.08), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 14,
    noise: 0.04
  },
  {
    id: "material-331",
    tone: "brown",
    gradient: "linear-gradient(41deg, rgba(171,123,38,0.18), rgba(2,167,202,0.09), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 15,
    noise: 0.045
  },
  {
    id: "material-332",
    tone: "gold",
    gradient: "linear-gradient(52deg, rgba(171,123,38,0.19), rgba(2,167,202,0.1), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 16,
    noise: 0.05
  },
  {
    id: "material-333",
    tone: "teal",
    gradient: "linear-gradient(63deg, rgba(171,123,38,0.11), rgba(2,167,202,0.11), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 17,
    noise: 0.055
  },
  {
    id: "material-334",
    tone: "cyan",
    gradient: "linear-gradient(74deg, rgba(171,123,38,0.12), rgba(2,167,202,0.12), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 18,
    noise: 0.06
  },
  {
    id: "material-335",
    tone: "brown",
    gradient: "linear-gradient(85deg, rgba(171,123,38,0.13), rgba(2,167,202,0.13), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 19,
    noise: 0.065
  },
  {
    id: "material-336",
    tone: "gold",
    gradient: "linear-gradient(96deg, rgba(171,123,38,0.14), rgba(2,167,202,0.07), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 20,
    noise: 0.07
  },
  {
    id: "material-337",
    tone: "teal",
    gradient: "linear-gradient(107deg, rgba(171,123,38,0.15), rgba(2,167,202,0.08), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 21,
    noise: 0.075
  },
  {
    id: "material-338",
    tone: "cyan",
    gradient: "linear-gradient(118deg, rgba(171,123,38,0.16), rgba(2,167,202,0.09), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 22,
    noise: 0.08
  },
  {
    id: "material-339",
    tone: "brown",
    gradient: "linear-gradient(129deg, rgba(171,123,38,0.17), rgba(2,167,202,0.1), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 23,
    noise: 0.085
  },
  {
    id: "material-340",
    tone: "gold",
    gradient: "linear-gradient(140deg, rgba(171,123,38,0.18), rgba(2,167,202,0.11), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 24,
    noise: 0.04
  },
  {
    id: "material-341",
    tone: "teal",
    gradient: "linear-gradient(151deg, rgba(171,123,38,0.19), rgba(2,167,202,0.12), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 25,
    noise: 0.045
  },
  {
    id: "material-342",
    tone: "cyan",
    gradient: "linear-gradient(162deg, rgba(171,123,38,0.11), rgba(2,167,202,0.13), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 8,
    noise: 0.05
  },
  {
    id: "material-343",
    tone: "brown",
    gradient: "linear-gradient(173deg, rgba(171,123,38,0.12), rgba(2,167,202,0.07), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 9,
    noise: 0.055
  },
  {
    id: "material-344",
    tone: "gold",
    gradient: "linear-gradient(184deg, rgba(171,123,38,0.13), rgba(2,167,202,0.08), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 10,
    noise: 0.06
  },
  {
    id: "material-345",
    tone: "teal",
    gradient: "linear-gradient(195deg, rgba(171,123,38,0.14), rgba(2,167,202,0.09), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 11,
    noise: 0.065
  },
  {
    id: "material-346",
    tone: "cyan",
    gradient: "linear-gradient(206deg, rgba(171,123,38,0.15), rgba(2,167,202,0.1), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 12,
    noise: 0.07
  },
  {
    id: "material-347",
    tone: "brown",
    gradient: "linear-gradient(217deg, rgba(171,123,38,0.16), rgba(2,167,202,0.11), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 13,
    noise: 0.075
  },
  {
    id: "material-348",
    tone: "gold",
    gradient: "linear-gradient(228deg, rgba(171,123,38,0.17), rgba(2,167,202,0.12), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 14,
    noise: 0.08
  },
  {
    id: "material-349",
    tone: "teal",
    gradient: "linear-gradient(239deg, rgba(171,123,38,0.18), rgba(2,167,202,0.13), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 15,
    noise: 0.085
  },
  {
    id: "material-350",
    tone: "cyan",
    gradient: "linear-gradient(250deg, rgba(171,123,38,0.19), rgba(2,167,202,0.07), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 16,
    noise: 0.04
  },
  {
    id: "material-351",
    tone: "brown",
    gradient: "linear-gradient(261deg, rgba(171,123,38,0.11), rgba(2,167,202,0.08), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 17,
    noise: 0.045
  },
  {
    id: "material-352",
    tone: "gold",
    gradient: "linear-gradient(272deg, rgba(171,123,38,0.12), rgba(2,167,202,0.09), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 18,
    noise: 0.05
  },
  {
    id: "material-353",
    tone: "teal",
    gradient: "linear-gradient(283deg, rgba(171,123,38,0.13), rgba(2,167,202,0.1), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 19,
    noise: 0.055
  },
  {
    id: "material-354",
    tone: "cyan",
    gradient: "linear-gradient(294deg, rgba(171,123,38,0.14), rgba(2,167,202,0.11), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 20,
    noise: 0.06
  },
  {
    id: "material-355",
    tone: "brown",
    gradient: "linear-gradient(305deg, rgba(171,123,38,0.15), rgba(2,167,202,0.12), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 21,
    noise: 0.065
  },
  {
    id: "material-356",
    tone: "gold",
    gradient: "linear-gradient(316deg, rgba(171,123,38,0.16), rgba(2,167,202,0.13), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 22,
    noise: 0.07
  },
  {
    id: "material-357",
    tone: "teal",
    gradient: "linear-gradient(327deg, rgba(171,123,38,0.17), rgba(2,167,202,0.07), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 23,
    noise: 0.075
  },
  {
    id: "material-358",
    tone: "cyan",
    gradient: "linear-gradient(338deg, rgba(171,123,38,0.18), rgba(2,167,202,0.08), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 24,
    noise: 0.08
  },
  {
    id: "material-359",
    tone: "brown",
    gradient: "linear-gradient(349deg, rgba(171,123,38,0.19), rgba(2,167,202,0.09), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 25,
    noise: 0.085
  },
  {
    id: "material-360",
    tone: "gold",
    gradient: "linear-gradient(0deg, rgba(171,123,38,0.11), rgba(2,167,202,0.1), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 8,
    noise: 0.04
  },
  {
    id: "material-361",
    tone: "teal",
    gradient: "linear-gradient(11deg, rgba(171,123,38,0.12), rgba(2,167,202,0.11), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 9,
    noise: 0.045
  },
  {
    id: "material-362",
    tone: "cyan",
    gradient: "linear-gradient(22deg, rgba(171,123,38,0.13), rgba(2,167,202,0.12), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 10,
    noise: 0.05
  },
  {
    id: "material-363",
    tone: "brown",
    gradient: "linear-gradient(33deg, rgba(171,123,38,0.14), rgba(2,167,202,0.13), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 11,
    noise: 0.055
  },
  {
    id: "material-364",
    tone: "gold",
    gradient: "linear-gradient(44deg, rgba(171,123,38,0.15), rgba(2,167,202,0.07), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 12,
    noise: 0.06
  },
  {
    id: "material-365",
    tone: "teal",
    gradient: "linear-gradient(55deg, rgba(171,123,38,0.16), rgba(2,167,202,0.08), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 13,
    noise: 0.065
  },
  {
    id: "material-366",
    tone: "cyan",
    gradient: "linear-gradient(66deg, rgba(171,123,38,0.17), rgba(2,167,202,0.09), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 14,
    noise: 0.07
  },
  {
    id: "material-367",
    tone: "brown",
    gradient: "linear-gradient(77deg, rgba(171,123,38,0.18), rgba(2,167,202,0.1), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 15,
    noise: 0.075
  },
  {
    id: "material-368",
    tone: "gold",
    gradient: "linear-gradient(88deg, rgba(171,123,38,0.19), rgba(2,167,202,0.11), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 16,
    noise: 0.08
  },
  {
    id: "material-369",
    tone: "teal",
    gradient: "linear-gradient(99deg, rgba(171,123,38,0.11), rgba(2,167,202,0.12), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 17,
    noise: 0.085
  },
  {
    id: "material-370",
    tone: "cyan",
    gradient: "linear-gradient(110deg, rgba(171,123,38,0.12), rgba(2,167,202,0.13), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 18,
    noise: 0.04
  },
  {
    id: "material-371",
    tone: "brown",
    gradient: "linear-gradient(121deg, rgba(171,123,38,0.13), rgba(2,167,202,0.07), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 19,
    noise: 0.045
  },
  {
    id: "material-372",
    tone: "gold",
    gradient: "linear-gradient(132deg, rgba(171,123,38,0.14), rgba(2,167,202,0.08), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 20,
    noise: 0.05
  },
  {
    id: "material-373",
    tone: "teal",
    gradient: "linear-gradient(143deg, rgba(171,123,38,0.15), rgba(2,167,202,0.09), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 21,
    noise: 0.055
  },
  {
    id: "material-374",
    tone: "cyan",
    gradient: "linear-gradient(154deg, rgba(171,123,38,0.16), rgba(2,167,202,0.1), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 22,
    noise: 0.06
  },
  {
    id: "material-375",
    tone: "brown",
    gradient: "linear-gradient(165deg, rgba(171,123,38,0.17), rgba(2,167,202,0.11), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 23,
    noise: 0.065
  },
  {
    id: "material-376",
    tone: "gold",
    gradient: "linear-gradient(176deg, rgba(171,123,38,0.18), rgba(2,167,202,0.12), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 24,
    noise: 0.07
  },
  {
    id: "material-377",
    tone: "teal",
    gradient: "linear-gradient(187deg, rgba(171,123,38,0.19), rgba(2,167,202,0.13), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 25,
    noise: 0.075
  },
  {
    id: "material-378",
    tone: "cyan",
    gradient: "linear-gradient(198deg, rgba(171,123,38,0.11), rgba(2,167,202,0.07), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 8,
    noise: 0.08
  },
  {
    id: "material-379",
    tone: "brown",
    gradient: "linear-gradient(209deg, rgba(171,123,38,0.12), rgba(2,167,202,0.08), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 9,
    noise: 0.085
  },
  {
    id: "material-380",
    tone: "gold",
    gradient: "linear-gradient(220deg, rgba(171,123,38,0.13), rgba(2,167,202,0.09), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 10,
    noise: 0.04
  },
  {
    id: "material-381",
    tone: "teal",
    gradient: "linear-gradient(231deg, rgba(171,123,38,0.14), rgba(2,167,202,0.1), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 11,
    noise: 0.045
  },
  {
    id: "material-382",
    tone: "cyan",
    gradient: "linear-gradient(242deg, rgba(171,123,38,0.15), rgba(2,167,202,0.11), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 12,
    noise: 0.05
  },
  {
    id: "material-383",
    tone: "brown",
    gradient: "linear-gradient(253deg, rgba(171,123,38,0.16), rgba(2,167,202,0.12), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 13,
    noise: 0.055
  },
  {
    id: "material-384",
    tone: "gold",
    gradient: "linear-gradient(264deg, rgba(171,123,38,0.17), rgba(2,167,202,0.13), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 14,
    noise: 0.06
  },
  {
    id: "material-385",
    tone: "teal",
    gradient: "linear-gradient(275deg, rgba(171,123,38,0.18), rgba(2,167,202,0.07), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 15,
    noise: 0.065
  },
  {
    id: "material-386",
    tone: "cyan",
    gradient: "linear-gradient(286deg, rgba(171,123,38,0.19), rgba(2,167,202,0.08), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 16,
    noise: 0.07
  },
  {
    id: "material-387",
    tone: "brown",
    gradient: "linear-gradient(297deg, rgba(171,123,38,0.11), rgba(2,167,202,0.09), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 17,
    noise: 0.075
  },
  {
    id: "material-388",
    tone: "gold",
    gradient: "linear-gradient(308deg, rgba(171,123,38,0.12), rgba(2,167,202,0.1), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 18,
    noise: 0.08
  },
  {
    id: "material-389",
    tone: "teal",
    gradient: "linear-gradient(319deg, rgba(171,123,38,0.13), rgba(2,167,202,0.11), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 19,
    noise: 0.085
  },
  {
    id: "material-390",
    tone: "cyan",
    gradient: "linear-gradient(330deg, rgba(171,123,38,0.14), rgba(2,167,202,0.12), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 20,
    noise: 0.04
  },
  {
    id: "material-391",
    tone: "brown",
    gradient: "linear-gradient(341deg, rgba(171,123,38,0.15), rgba(2,167,202,0.13), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 21,
    noise: 0.045
  },
  {
    id: "material-392",
    tone: "gold",
    gradient: "linear-gradient(352deg, rgba(171,123,38,0.16), rgba(2,167,202,0.07), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 22,
    noise: 0.05
  },
  {
    id: "material-393",
    tone: "teal",
    gradient: "linear-gradient(3deg, rgba(171,123,38,0.17), rgba(2,167,202,0.08), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 23,
    noise: 0.055
  },
  {
    id: "material-394",
    tone: "cyan",
    gradient: "linear-gradient(14deg, rgba(171,123,38,0.18), rgba(2,167,202,0.09), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 24,
    noise: 0.06
  },
  {
    id: "material-395",
    tone: "brown",
    gradient: "linear-gradient(25deg, rgba(171,123,38,0.19), rgba(2,167,202,0.1), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 25,
    noise: 0.065
  },
  {
    id: "material-396",
    tone: "gold",
    gradient: "linear-gradient(36deg, rgba(171,123,38,0.11), rgba(2,167,202,0.11), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 8,
    noise: 0.07
  },
  {
    id: "material-397",
    tone: "teal",
    gradient: "linear-gradient(47deg, rgba(171,123,38,0.12), rgba(2,167,202,0.12), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 9,
    noise: 0.075
  },
  {
    id: "material-398",
    tone: "cyan",
    gradient: "linear-gradient(58deg, rgba(171,123,38,0.13), rgba(2,167,202,0.13), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 10,
    noise: 0.08
  },
  {
    id: "material-399",
    tone: "brown",
    gradient: "linear-gradient(69deg, rgba(171,123,38,0.14), rgba(2,167,202,0.07), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 11,
    noise: 0.085
  },
  {
    id: "material-400",
    tone: "gold",
    gradient: "linear-gradient(80deg, rgba(171,123,38,0.15), rgba(2,167,202,0.08), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 12,
    noise: 0.04
  },
  {
    id: "material-401",
    tone: "teal",
    gradient: "linear-gradient(91deg, rgba(171,123,38,0.16), rgba(2,167,202,0.09), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 13,
    noise: 0.045
  },
  {
    id: "material-402",
    tone: "cyan",
    gradient: "linear-gradient(102deg, rgba(171,123,38,0.17), rgba(2,167,202,0.1), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 14,
    noise: 0.05
  },
  {
    id: "material-403",
    tone: "brown",
    gradient: "linear-gradient(113deg, rgba(171,123,38,0.18), rgba(2,167,202,0.11), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 15,
    noise: 0.055
  },
  {
    id: "material-404",
    tone: "gold",
    gradient: "linear-gradient(124deg, rgba(171,123,38,0.19), rgba(2,167,202,0.12), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 16,
    noise: 0.06
  },
  {
    id: "material-405",
    tone: "teal",
    gradient: "linear-gradient(135deg, rgba(171,123,38,0.11), rgba(2,167,202,0.13), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 17,
    noise: 0.065
  },
  {
    id: "material-406",
    tone: "cyan",
    gradient: "linear-gradient(146deg, rgba(171,123,38,0.12), rgba(2,167,202,0.07), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 18,
    noise: 0.07
  },
  {
    id: "material-407",
    tone: "brown",
    gradient: "linear-gradient(157deg, rgba(171,123,38,0.13), rgba(2,167,202,0.08), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 19,
    noise: 0.075
  },
  {
    id: "material-408",
    tone: "gold",
    gradient: "linear-gradient(168deg, rgba(171,123,38,0.14), rgba(2,167,202,0.09), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 20,
    noise: 0.08
  },
  {
    id: "material-409",
    tone: "teal",
    gradient: "linear-gradient(179deg, rgba(171,123,38,0.15), rgba(2,167,202,0.1), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 21,
    noise: 0.085
  },
  {
    id: "material-410",
    tone: "cyan",
    gradient: "linear-gradient(190deg, rgba(171,123,38,0.16), rgba(2,167,202,0.11), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 22,
    noise: 0.04
  },
  {
    id: "material-411",
    tone: "brown",
    gradient: "linear-gradient(201deg, rgba(171,123,38,0.17), rgba(2,167,202,0.12), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 23,
    noise: 0.045
  },
  {
    id: "material-412",
    tone: "gold",
    gradient: "linear-gradient(212deg, rgba(171,123,38,0.18), rgba(2,167,202,0.13), rgba(2,111,134,0.18))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 24,
    noise: 0.05
  },
  {
    id: "material-413",
    tone: "teal",
    gradient: "linear-gradient(223deg, rgba(171,123,38,0.19), rgba(2,167,202,0.07), rgba(2,111,134,0.19))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.23)",
    blur: 25,
    noise: 0.055
  },
  {
    id: "material-414",
    tone: "cyan",
    gradient: "linear-gradient(234deg, rgba(171,123,38,0.11), rgba(2,167,202,0.08), rgba(2,111,134,0.11))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.24)",
    blur: 8,
    noise: 0.06
  },
  {
    id: "material-415",
    tone: "brown",
    gradient: "linear-gradient(245deg, rgba(171,123,38,0.12), rgba(2,167,202,0.09), rgba(2,111,134,0.12))",
    border: "rgba(2,111,134,0.25)",
    glow: "0 0 24px rgba(2,167,202,0.25)",
    blur: 9,
    noise: 0.065
  },
  {
    id: "material-416",
    tone: "gold",
    gradient: "linear-gradient(256deg, rgba(171,123,38,0.13), rgba(2,167,202,0.1), rgba(2,111,134,0.13))",
    border: "rgba(2,111,134,0.26)",
    glow: "0 0 24px rgba(2,167,202,0.18)",
    blur: 10,
    noise: 0.07
  },
  {
    id: "material-417",
    tone: "teal",
    gradient: "linear-gradient(267deg, rgba(171,123,38,0.14), rgba(2,167,202,0.11), rgba(2,111,134,0.14))",
    border: "rgba(2,111,134,0.27)",
    glow: "0 0 24px rgba(2,167,202,0.19)",
    blur: 11,
    noise: 0.075
  },
  {
    id: "material-418",
    tone: "cyan",
    gradient: "linear-gradient(278deg, rgba(171,123,38,0.15), rgba(2,167,202,0.12), rgba(2,111,134,0.15))",
    border: "rgba(2,111,134,0.28)",
    glow: "0 0 24px rgba(2,167,202,0.2)",
    blur: 12,
    noise: 0.08
  },
  {
    id: "material-419",
    tone: "brown",
    gradient: "linear-gradient(289deg, rgba(171,123,38,0.16), rgba(2,167,202,0.13), rgba(2,111,134,0.16))",
    border: "rgba(2,111,134,0.29)",
    glow: "0 0 24px rgba(2,167,202,0.21)",
    blur: 13,
    noise: 0.085
  },
  {
    id: "material-420",
    tone: "gold",
    gradient: "linear-gradient(300deg, rgba(171,123,38,0.17), rgba(2,167,202,0.07), rgba(2,111,134,0.17))",
    border: "rgba(2,111,134,0.24)",
    glow: "0 0 24px rgba(2,167,202,0.22)",
    blur: 14,
    noise: 0.04
  },
] as const;

export const PITCH_MATERIAL_PRESET_BY_ID: Readonly<Record<string, PitchMaterialPreset>> =
  PITCH_MATERIAL_PRESETS.reduce<Record<string, PitchMaterialPreset>>((acc, preset) => {
    acc[preset.id] = preset;
    return acc;
  }, {});

export function pickPitchMaterialPreset(index: number): PitchMaterialPreset {
  if (PITCH_MATERIAL_PRESETS.length === 0) {
    throw new Error("PITCH_MATERIAL_PRESETS is empty.");
  }
  const safeIndex = Math.abs(index) % PITCH_MATERIAL_PRESETS.length;
  return PITCH_MATERIAL_PRESETS[safeIndex]!;
}

export function listPitchMaterialPresetsByTone(tone: PitchMaterialPreset["tone"]): readonly PitchMaterialPreset[] {
  return PITCH_MATERIAL_PRESETS.filter((preset) => preset.tone === tone);
}
