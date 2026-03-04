export interface LayerResolutionScenario {
  readonly id: string;
  readonly route: string;
  readonly profile: string;
  readonly layers?: string;
  readonly debug?: string;
  readonly expected: {
    readonly source: "layers" | "profile" | "default";
    readonly profile: "neutral" | "fx" | "perf";
    readonly debug: boolean;
    readonly enabled: readonly string[];
    readonly enabledCount: number;
    readonly motionEnabled: boolean;
  };
}

export const LAYER_RESOLUTION_SCENARIOS: readonly LayerResolutionScenario[] = [
  {
    id: "LAYER_SCENARIO_0001",
    route: "/pitch",
    profile: "neutral",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0002",
    route: "/pitch",
    profile: "neutral",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0003",
    route: "/pitch",
    profile: "neutral",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0004",
    route: "/pitch",
    profile: "neutral",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0005",
    route: "/pitch",
    profile: "neutral",
    layers: "",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0006",
    route: "/pitch",
    profile: "neutral",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0007",
    route: "/pitch",
    profile: "neutral",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0008",
    route: "/pitch",
    profile: "neutral",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0009",
    route: "/pitch",
    profile: "neutral",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0010",
    route: "/pitch",
    profile: "neutral",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0011",
    route: "/pitch",
    profile: "neutral",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0012",
    route: "/pitch",
    profile: "neutral",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0013",
    route: "/pitch",
    profile: "neutral",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0014",
    route: "/pitch",
    profile: "neutral",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0015",
    route: "/pitch",
    profile: "neutral",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0016",
    route: "/pitch",
    profile: "neutral",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0017",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0018",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0019",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0020",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0021",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0022",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0023",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0024",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0025",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0026",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0027",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0028",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0029",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0030",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0031",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0032",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0033",
    route: "/pitch",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0034",
    route: "/pitch",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0035",
    route: "/pitch",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0036",
    route: "/pitch",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0037",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0038",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0039",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0040",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0041",
    route: "/pitch",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0042",
    route: "/pitch",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0043",
    route: "/pitch",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0044",
    route: "/pitch",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0045",
    route: "/pitch",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0046",
    route: "/pitch",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0047",
    route: "/pitch",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0048",
    route: "/pitch",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0049",
    route: "/pitch",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0050",
    route: "/pitch",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0051",
    route: "/pitch",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0052",
    route: "/pitch",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0053",
    route: "/pitch",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0054",
    route: "/pitch",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0055",
    route: "/pitch",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0056",
    route: "/pitch",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0057",
    route: "/pitch",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0058",
    route: "/pitch",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0059",
    route: "/pitch",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0060",
    route: "/pitch",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0061",
    route: "/pitch",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0062",
    route: "/pitch",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0063",
    route: "/pitch",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0064",
    route: "/pitch",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0065",
    route: "/pitch",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0066",
    route: "/pitch",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0067",
    route: "/pitch",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0068",
    route: "/pitch",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0069",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0070",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0071",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0072",
    route: "/pitch",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0073",
    route: "/pitch",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0074",
    route: "/pitch",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0075",
    route: "/pitch",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0076",
    route: "/pitch",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0077",
    route: "/pitch",
    profile: "neutral",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0078",
    route: "/pitch",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0079",
    route: "/pitch",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0080",
    route: "/pitch",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0081",
    route: "/pitch",
    profile: "fx",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0082",
    route: "/pitch",
    profile: "fx",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0083",
    route: "/pitch",
    profile: "fx",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0084",
    route: "/pitch",
    profile: "fx",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0085",
    route: "/pitch",
    profile: "fx",
    layers: "",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0086",
    route: "/pitch",
    profile: "fx",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0087",
    route: "/pitch",
    profile: "fx",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0088",
    route: "/pitch",
    profile: "fx",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0089",
    route: "/pitch",
    profile: "fx",
    layers: "none",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0090",
    route: "/pitch",
    profile: "fx",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0091",
    route: "/pitch",
    profile: "fx",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0092",
    route: "/pitch",
    profile: "fx",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0093",
    route: "/pitch",
    profile: "fx",
    layers: "all",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0094",
    route: "/pitch",
    profile: "fx",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0095",
    route: "/pitch",
    profile: "fx",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0096",
    route: "/pitch",
    profile: "fx",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0097",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0098",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0099",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0100",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0101",
    route: "/pitch",
    profile: "fx",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0102",
    route: "/pitch",
    profile: "fx",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0103",
    route: "/pitch",
    profile: "fx",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0104",
    route: "/pitch",
    profile: "fx",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0105",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0106",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0107",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0108",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0109",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0110",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0111",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0112",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0113",
    route: "/pitch",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0114",
    route: "/pitch",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0115",
    route: "/pitch",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0116",
    route: "/pitch",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0117",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0118",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0119",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0120",
    route: "/pitch",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0121",
    route: "/pitch",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0122",
    route: "/pitch",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0123",
    route: "/pitch",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0124",
    route: "/pitch",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0125",
    route: "/pitch",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0126",
    route: "/pitch",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0127",
    route: "/pitch",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0128",
    route: "/pitch",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0129",
    route: "/pitch",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0130",
    route: "/pitch",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0131",
    route: "/pitch",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0132",
    route: "/pitch",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0133",
    route: "/pitch",
    profile: "fx",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0134",
    route: "/pitch",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0135",
    route: "/pitch",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0136",
    route: "/pitch",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0137",
    route: "/pitch",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0138",
    route: "/pitch",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0139",
    route: "/pitch",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0140",
    route: "/pitch",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0141",
    route: "/pitch",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0142",
    route: "/pitch",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0143",
    route: "/pitch",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0144",
    route: "/pitch",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0145",
    route: "/pitch",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0146",
    route: "/pitch",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0147",
    route: "/pitch",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0148",
    route: "/pitch",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0149",
    route: "/pitch",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0150",
    route: "/pitch",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0151",
    route: "/pitch",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0152",
    route: "/pitch",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0153",
    route: "/pitch",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0154",
    route: "/pitch",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0155",
    route: "/pitch",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0156",
    route: "/pitch",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0157",
    route: "/pitch",
    profile: "fx",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0158",
    route: "/pitch",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0159",
    route: "/pitch",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0160",
    route: "/pitch",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0161",
    route: "/pitch",
    profile: "perf",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0162",
    route: "/pitch",
    profile: "perf",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0163",
    route: "/pitch",
    profile: "perf",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0164",
    route: "/pitch",
    profile: "perf",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0165",
    route: "/pitch",
    profile: "perf",
    layers: "",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0166",
    route: "/pitch",
    profile: "perf",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0167",
    route: "/pitch",
    profile: "perf",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0168",
    route: "/pitch",
    profile: "perf",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0169",
    route: "/pitch",
    profile: "perf",
    layers: "none",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0170",
    route: "/pitch",
    profile: "perf",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0171",
    route: "/pitch",
    profile: "perf",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0172",
    route: "/pitch",
    profile: "perf",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0173",
    route: "/pitch",
    profile: "perf",
    layers: "all",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0174",
    route: "/pitch",
    profile: "perf",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0175",
    route: "/pitch",
    profile: "perf",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0176",
    route: "/pitch",
    profile: "perf",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0177",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0178",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0179",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0180",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0181",
    route: "/pitch",
    profile: "perf",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0182",
    route: "/pitch",
    profile: "perf",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0183",
    route: "/pitch",
    profile: "perf",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0184",
    route: "/pitch",
    profile: "perf",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0185",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0186",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0187",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0188",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0189",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0190",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0191",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0192",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0193",
    route: "/pitch",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0194",
    route: "/pitch",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0195",
    route: "/pitch",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0196",
    route: "/pitch",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0197",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0198",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0199",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0200",
    route: "/pitch",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0201",
    route: "/pitch",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0202",
    route: "/pitch",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0203",
    route: "/pitch",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0204",
    route: "/pitch",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0205",
    route: "/pitch",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0206",
    route: "/pitch",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0207",
    route: "/pitch",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0208",
    route: "/pitch",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0209",
    route: "/pitch",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0210",
    route: "/pitch",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0211",
    route: "/pitch",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0212",
    route: "/pitch",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0213",
    route: "/pitch",
    profile: "perf",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0214",
    route: "/pitch",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0215",
    route: "/pitch",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0216",
    route: "/pitch",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0217",
    route: "/pitch",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0218",
    route: "/pitch",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0219",
    route: "/pitch",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0220",
    route: "/pitch",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0221",
    route: "/pitch",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0222",
    route: "/pitch",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0223",
    route: "/pitch",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0224",
    route: "/pitch",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0225",
    route: "/pitch",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0226",
    route: "/pitch",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0227",
    route: "/pitch",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0228",
    route: "/pitch",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0229",
    route: "/pitch",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0230",
    route: "/pitch",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0231",
    route: "/pitch",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0232",
    route: "/pitch",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0233",
    route: "/pitch",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0234",
    route: "/pitch",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0235",
    route: "/pitch",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0236",
    route: "/pitch",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0237",
    route: "/pitch",
    profile: "perf",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0238",
    route: "/pitch",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0239",
    route: "/pitch",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0240",
    route: "/pitch",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0241",
    route: "/pitch",
    profile: "invalid",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0242",
    route: "/pitch",
    profile: "invalid",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0243",
    route: "/pitch",
    profile: "invalid",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0244",
    route: "/pitch",
    profile: "invalid",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0245",
    route: "/pitch",
    profile: "invalid",
    layers: "",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0246",
    route: "/pitch",
    profile: "invalid",
    layers: "",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0247",
    route: "/pitch",
    profile: "invalid",
    layers: "",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0248",
    route: "/pitch",
    profile: "invalid",
    layers: "",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0249",
    route: "/pitch",
    profile: "invalid",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0250",
    route: "/pitch",
    profile: "invalid",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0251",
    route: "/pitch",
    profile: "invalid",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0252",
    route: "/pitch",
    profile: "invalid",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0253",
    route: "/pitch",
    profile: "invalid",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0254",
    route: "/pitch",
    profile: "invalid",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0255",
    route: "/pitch",
    profile: "invalid",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0256",
    route: "/pitch",
    profile: "invalid",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0257",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0258",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0259",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0260",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0261",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0262",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0263",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0264",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0265",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0266",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0267",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0268",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0269",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0270",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0271",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0272",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0273",
    route: "/pitch",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0274",
    route: "/pitch",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0275",
    route: "/pitch",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0276",
    route: "/pitch",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0277",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0278",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0279",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0280",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0281",
    route: "/pitch",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0282",
    route: "/pitch",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0283",
    route: "/pitch",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0284",
    route: "/pitch",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0285",
    route: "/pitch",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0286",
    route: "/pitch",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0287",
    route: "/pitch",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0288",
    route: "/pitch",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0289",
    route: "/pitch",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0290",
    route: "/pitch",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0291",
    route: "/pitch",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0292",
    route: "/pitch",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0293",
    route: "/pitch",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0294",
    route: "/pitch",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0295",
    route: "/pitch",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0296",
    route: "/pitch",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0297",
    route: "/pitch",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0298",
    route: "/pitch",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0299",
    route: "/pitch",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0300",
    route: "/pitch",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0301",
    route: "/pitch",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0302",
    route: "/pitch",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0303",
    route: "/pitch",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0304",
    route: "/pitch",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0305",
    route: "/pitch",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0306",
    route: "/pitch",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0307",
    route: "/pitch",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0308",
    route: "/pitch",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0309",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0310",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0311",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0312",
    route: "/pitch",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0313",
    route: "/pitch",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0314",
    route: "/pitch",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0315",
    route: "/pitch",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0316",
    route: "/pitch",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0317",
    route: "/pitch",
    profile: "invalid",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0318",
    route: "/pitch",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0319",
    route: "/pitch",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0320",
    route: "/pitch",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0321",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0322",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0323",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0324",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0325",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0326",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0327",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0328",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0329",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0330",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0331",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0332",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0333",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0334",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0335",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0336",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0337",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0338",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0339",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0340",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0341",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0342",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0343",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0344",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0345",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0346",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0347",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0348",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0349",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0350",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0351",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0352",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0353",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0354",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0355",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0356",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0357",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0358",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0359",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0360",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0361",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0362",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0363",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0364",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0365",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0366",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0367",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0368",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0369",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0370",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0371",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0372",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0373",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0374",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0375",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0376",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0377",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0378",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0379",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0380",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0381",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0382",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0383",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0384",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0385",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0386",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0387",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0388",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0389",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0390",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0391",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0392",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0393",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0394",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0395",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0396",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0397",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0398",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0399",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0400",
    route: "/pitch/01-double-engine",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0401",
    route: "/pitch/01-double-engine",
    profile: "fx",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0402",
    route: "/pitch/01-double-engine",
    profile: "fx",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0403",
    route: "/pitch/01-double-engine",
    profile: "fx",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0404",
    route: "/pitch/01-double-engine",
    profile: "fx",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0405",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0406",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0407",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0408",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0409",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "none",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0410",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0411",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0412",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0413",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "all",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0414",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0415",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0416",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0417",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0418",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0419",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0420",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0421",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0422",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0423",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0424",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0425",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0426",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0427",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0428",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0429",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0430",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0431",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0432",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0433",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0434",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0435",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0436",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0437",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0438",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0439",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0440",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0441",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0442",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0443",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0444",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0445",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0446",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0447",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0448",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0449",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0450",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0451",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0452",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0453",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0454",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0455",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0456",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0457",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0458",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0459",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0460",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0461",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0462",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0463",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0464",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0465",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0466",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0467",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0468",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0469",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0470",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0471",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0472",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0473",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0474",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0475",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0476",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0477",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0478",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0479",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0480",
    route: "/pitch/01-double-engine",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0481",
    route: "/pitch/01-double-engine",
    profile: "perf",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0482",
    route: "/pitch/01-double-engine",
    profile: "perf",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0483",
    route: "/pitch/01-double-engine",
    profile: "perf",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0484",
    route: "/pitch/01-double-engine",
    profile: "perf",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0485",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0486",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0487",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0488",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0489",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "none",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0490",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0491",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0492",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0493",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "all",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0494",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0495",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0496",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0497",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0498",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0499",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0500",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0501",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0502",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0503",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0504",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0505",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0506",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0507",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0508",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0509",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0510",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0511",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0512",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0513",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0514",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0515",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0516",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0517",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0518",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0519",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0520",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0521",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0522",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0523",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0524",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0525",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0526",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0527",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0528",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0529",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0530",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0531",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0532",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0533",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0534",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0535",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0536",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0537",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0538",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0539",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0540",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0541",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0542",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0543",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0544",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0545",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0546",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0547",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0548",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0549",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0550",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0551",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0552",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0553",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0554",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0555",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0556",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0557",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0558",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0559",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0560",
    route: "/pitch/01-double-engine",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0561",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0562",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0563",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0564",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0565",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0566",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0567",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0568",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0569",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0570",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0571",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0572",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0573",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0574",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0575",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0576",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0577",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0578",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0579",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0580",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0581",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0582",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0583",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0584",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0585",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0586",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0587",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0588",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0589",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0590",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0591",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0592",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0593",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0594",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0595",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0596",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0597",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0598",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0599",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0600",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0601",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0602",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0603",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0604",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0605",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0606",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0607",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0608",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0609",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0610",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0611",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0612",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0613",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0614",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0615",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0616",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0617",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0618",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0619",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0620",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0621",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0622",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0623",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0624",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0625",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0626",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0627",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0628",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0629",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0630",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0631",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0632",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0633",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0634",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0635",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0636",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0637",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0638",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0639",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0640",
    route: "/pitch/01-double-engine",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0641",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0642",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0643",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0644",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0645",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0646",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0647",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0648",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0649",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0650",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0651",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0652",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0653",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0654",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0655",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0656",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0657",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0658",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0659",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0660",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0661",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0662",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0663",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0664",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0665",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0666",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0667",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0668",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0669",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0670",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0671",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0672",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0673",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0674",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0675",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0676",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0677",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0678",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0679",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0680",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0681",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0682",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0683",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0684",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0685",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0686",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0687",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0688",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0689",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0690",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0691",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0692",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0693",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0694",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0695",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0696",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0697",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0698",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0699",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0700",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0701",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0702",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0703",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0704",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0705",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0706",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0707",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0708",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0709",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0710",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0711",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0712",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0713",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0714",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0715",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0716",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0717",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0718",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0719",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0720",
    route: "/pitch/02-industrial-flow",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0721",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0722",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0723",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0724",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0725",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0726",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0727",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0728",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0729",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "none",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0730",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0731",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0732",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0733",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "all",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0734",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0735",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0736",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0737",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0738",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0739",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0740",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0741",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0742",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0743",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0744",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0745",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0746",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0747",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0748",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0749",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0750",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0751",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0752",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0753",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0754",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0755",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0756",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0757",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0758",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0759",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0760",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0761",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0762",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0763",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0764",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0765",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0766",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0767",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0768",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0769",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0770",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0771",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0772",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0773",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0774",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0775",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0776",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0777",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0778",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0779",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0780",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0781",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0782",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0783",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0784",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0785",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0786",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0787",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0788",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0789",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0790",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0791",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0792",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0793",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0794",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0795",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0796",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0797",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0798",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0799",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0800",
    route: "/pitch/02-industrial-flow",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0801",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0802",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0803",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0804",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0805",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0806",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0807",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0808",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0809",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "none",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0810",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0811",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0812",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0813",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "all",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0814",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0815",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0816",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0817",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0818",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0819",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0820",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0821",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0822",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0823",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0824",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0825",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0826",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0827",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0828",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0829",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0830",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0831",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0832",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0833",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0834",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0835",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0836",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0837",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0838",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0839",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0840",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0841",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0842",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0843",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0844",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0845",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0846",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0847",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0848",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0849",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0850",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0851",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0852",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0853",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0854",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0855",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0856",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0857",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0858",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0859",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0860",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0861",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0862",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0863",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0864",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0865",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0866",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0867",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0868",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0869",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0870",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0871",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0872",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0873",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0874",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0875",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0876",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0877",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0878",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0879",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0880",
    route: "/pitch/02-industrial-flow",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0881",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0882",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0883",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0884",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0885",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0886",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0887",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0888",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0889",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0890",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0891",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0892",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0893",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0894",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0895",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0896",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0897",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0898",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0899",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0900",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0901",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0902",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0903",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0904",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0905",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0906",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0907",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0908",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0909",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0910",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0911",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0912",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0913",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0914",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0915",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0916",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0917",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0918",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0919",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0920",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0921",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0922",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0923",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0924",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0925",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0926",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0927",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0928",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0929",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0930",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0931",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0932",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0933",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0934",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0935",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0936",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0937",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0938",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0939",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0940",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0941",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0942",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0943",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0944",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0945",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0946",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0947",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0948",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0949",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0950",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0951",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0952",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0953",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0954",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0955",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0956",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0957",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0958",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0959",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0960",
    route: "/pitch/02-industrial-flow",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0961",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0962",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0963",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0964",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0965",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0966",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0967",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0968",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0969",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0970",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0971",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0972",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0973",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0974",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0975",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0976",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_0977",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0978",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0979",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0980",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0981",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0982",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0983",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0984",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0985",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0986",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0987",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0988",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0989",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0990",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0991",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0992",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0993",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0994",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0995",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0996",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0997",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0998",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_0999",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1000",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1001",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1002",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1003",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1004",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1005",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1006",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1007",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1008",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1009",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1010",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1011",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1012",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1013",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1014",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1015",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1016",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1017",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1018",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1019",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1020",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1021",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1022",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1023",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1024",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1025",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1026",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1027",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1028",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1029",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1030",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1031",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1032",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1033",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1034",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1035",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1036",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1037",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1038",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1039",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1040",
    route: "/pitch/03-hitech-os",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1041",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1042",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1043",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1044",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1045",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1046",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1047",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1048",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1049",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "none",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1050",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1051",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1052",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1053",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "all",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1054",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1055",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1056",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1057",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1058",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1059",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1060",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1061",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1062",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1063",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1064",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1065",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1066",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1067",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1068",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1069",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1070",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1071",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1072",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1073",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1074",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1075",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1076",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1077",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1078",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1079",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1080",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1081",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1082",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1083",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1084",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1085",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1086",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1087",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1088",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1089",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1090",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1091",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1092",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1093",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1094",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1095",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1096",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1097",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1098",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1099",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1100",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1101",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1102",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1103",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1104",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1105",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1106",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1107",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1108",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1109",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1110",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1111",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1112",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1113",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1114",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1115",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1116",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1117",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1118",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1119",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1120",
    route: "/pitch/03-hitech-os",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1121",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1122",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1123",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1124",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1125",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1126",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1127",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1128",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1129",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "none",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1130",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1131",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1132",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1133",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "all",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1134",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1135",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1136",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1137",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1138",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1139",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1140",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1141",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1142",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1143",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1144",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1145",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1146",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1147",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1148",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1149",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1150",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1151",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1152",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1153",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1154",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1155",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1156",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1157",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1158",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1159",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1160",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1161",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1162",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1163",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1164",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1165",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1166",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1167",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1168",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1169",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1170",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1171",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1172",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1173",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1174",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1175",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1176",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1177",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1178",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1179",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1180",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1181",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1182",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1183",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1184",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1185",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1186",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1187",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1188",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1189",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1190",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1191",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1192",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1193",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1194",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1195",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1196",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1197",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1198",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1199",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1200",
    route: "/pitch/03-hitech-os",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1201",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1202",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1203",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1204",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1205",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1206",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1207",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1208",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1209",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1210",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1211",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1212",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1213",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1214",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1215",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1216",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1217",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1218",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1219",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1220",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1221",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1222",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1223",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1224",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1225",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1226",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1227",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1228",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1229",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1230",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1231",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1232",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1233",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1234",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1235",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1236",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1237",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1238",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1239",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1240",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1241",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1242",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1243",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1244",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1245",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1246",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1247",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1248",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1249",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1250",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1251",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1252",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1253",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1254",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1255",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1256",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1257",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1258",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1259",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1260",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1261",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1262",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1263",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1264",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1265",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1266",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1267",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1268",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1269",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1270",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1271",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1272",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1273",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1274",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1275",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1276",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1277",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1278",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1279",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1280",
    route: "/pitch/03-hitech-os",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1281",
    route: "/pitch/04-valuation",
    profile: "neutral",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1282",
    route: "/pitch/04-valuation",
    profile: "neutral",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1283",
    route: "/pitch/04-valuation",
    profile: "neutral",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1284",
    route: "/pitch/04-valuation",
    profile: "neutral",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1285",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1286",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1287",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1288",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1289",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1290",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1291",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1292",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1293",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1294",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1295",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1296",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1297",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1298",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1299",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1300",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1301",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1302",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1303",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1304",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1305",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1306",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1307",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1308",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1309",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1310",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1311",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1312",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1313",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1314",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1315",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1316",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1317",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1318",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1319",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1320",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1321",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1322",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1323",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1324",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1325",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1326",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1327",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1328",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1329",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1330",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1331",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1332",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1333",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1334",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1335",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1336",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1337",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1338",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1339",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1340",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1341",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1342",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1343",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1344",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1345",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1346",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1347",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1348",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1349",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1350",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1351",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1352",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1353",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1354",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1355",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1356",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1357",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1358",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1359",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1360",
    route: "/pitch/04-valuation",
    profile: "neutral",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1361",
    route: "/pitch/04-valuation",
    profile: "fx",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1362",
    route: "/pitch/04-valuation",
    profile: "fx",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1363",
    route: "/pitch/04-valuation",
    profile: "fx",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1364",
    route: "/pitch/04-valuation",
    profile: "fx",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1365",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1366",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1367",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1368",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.horizon",
        "stage.noise",
        "card.innerStroke",
        "card.shadowAmbient",
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 9,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1369",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "none",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1370",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1371",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1372",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1373",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "all",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1374",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1375",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1376",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1377",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1378",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1379",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1380",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1381",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1382",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1383",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1384",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1385",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1386",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1387",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1388",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1389",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1390",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1391",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1392",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1393",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1394",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1395",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1396",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1397",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1398",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1399",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1400",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1401",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1402",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1403",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1404",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1405",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1406",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1407",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1408",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1409",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1410",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1411",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1412",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1413",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1414",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1415",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1416",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1417",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1418",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1419",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1420",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1421",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1422",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1423",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1424",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1425",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1426",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1427",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1428",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1429",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1430",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1431",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1432",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1433",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1434",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1435",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1436",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1437",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1438",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1439",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "fx",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1440",
    route: "/pitch/04-valuation",
    profile: "fx",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "fx",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1441",
    route: "/pitch/04-valuation",
    profile: "perf",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1442",
    route: "/pitch/04-valuation",
    profile: "perf",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1443",
    route: "/pitch/04-valuation",
    profile: "perf",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1444",
    route: "/pitch/04-valuation",
    profile: "perf",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1445",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1446",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "",
    debug: "0",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1447",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "",
    debug: "1",
    expected: {
      source: "profile",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1448",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "",
    debug: "true",
    expected: {
      source: "profile",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "card.innerStroke",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1449",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "none",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1450",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1451",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1452",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1453",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "all",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1454",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1455",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1456",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1457",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1458",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1459",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1460",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1461",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1462",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1463",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1464",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1465",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1466",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1467",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1468",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1469",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1470",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1471",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1472",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1473",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1474",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1475",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1476",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1477",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1478",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1479",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1480",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1481",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1482",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1483",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1484",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1485",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1486",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1487",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1488",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1489",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1490",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1491",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1492",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1493",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1494",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1495",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1496",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1497",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1498",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1499",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1500",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1501",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1502",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1503",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1504",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1505",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1506",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1507",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1508",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1509",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1510",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1511",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1512",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1513",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1514",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1515",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1516",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1517",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1518",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1519",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "perf",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1520",
    route: "/pitch/04-valuation",
    profile: "perf",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "perf",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1521",
    route: "/pitch/04-valuation",
    profile: "invalid",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1522",
    route: "/pitch/04-valuation",
    profile: "invalid",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1523",
    route: "/pitch/04-valuation",
    profile: "invalid",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1524",
    route: "/pitch/04-valuation",
    profile: "invalid",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1525",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1526",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "",
    debug: "0",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1527",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "",
    debug: "1",
    expected: {
      source: "default",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1528",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "",
    debug: "true",
    expected: {
      source: "default",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1529",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "none",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1530",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "none",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1531",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "none",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1532",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "none",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1533",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "all",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1534",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "all",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1535",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "all",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1536",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "all",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 13,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1537",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1538",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1539",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1540",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1541",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1542",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1543",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1544",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1545",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1546",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1547",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1548",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,stage.vignette",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "stage.noise",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1549",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1550",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1551",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1552",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,unknown.layer",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1553",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1554",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1555",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1556",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "unknown.layer,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1557",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1558",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1559",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1560",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.noise,stage.noise",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.noise",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1561",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1562",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1563",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1564",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "card.blur,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1565",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1566",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1567",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1568",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "inset.shadow,card.grain,card.specular",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.specular",
        "card.grain",
        "inset.shadow",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1569",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1570",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1571",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1572",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "  stage.haze , stage.scanlines  ",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.scanlines",
      ],
      enabledCount: 2,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1573",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1574",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1575",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1576",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: ",,stage.horizon,,",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.horizon",
      ],
      enabledCount: 1,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1577",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1578",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1579",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1580",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "frame.bezel,stage.vignette,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.vignette",
        "frame.bezel",
        "card.innerStroke",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1581",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1582",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1583",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1584",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "motion.enabled,unknown,stage.haze,stage.haze",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "motion.enabled",
      ],
      enabledCount: 2,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1585",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1586",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1587",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1588",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "card.shadowAmbient,card.blur,card.innerStroke",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "card.blur",
        "card.innerStroke",
        "card.shadowAmbient",
      ],
      enabledCount: 3,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1589",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1590",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1591",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1592",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "stage.haze,stage.vignette,stage.noise,stage.scanlines,stage.horizon",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "stage.haze",
        "stage.vignette",
        "stage.noise",
        "stage.scanlines",
        "stage.horizon",
      ],
      enabledCount: 5,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1593",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1594",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1595",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1596",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "frame.bezel,card.blur,card.innerStroke,card.specular,card.grain,card.shadowAmbient,inset.shadow,motion.enabled",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
        "frame.bezel",
        "card.blur",
        "card.innerStroke",
        "card.specular",
        "card.grain",
        "card.shadowAmbient",
        "inset.shadow",
        "motion.enabled",
      ],
      enabledCount: 8,
      motionEnabled: true
    }
  },
  {
    id: "LAYER_SCENARIO_1597",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "unknown.layer.only",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1598",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "0",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1599",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "1",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: true,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
  {
    id: "LAYER_SCENARIO_1600",
    route: "/pitch/04-valuation",
    profile: "invalid",
    layers: "unknown.layer.only",
    debug: "true",
    expected: {
      source: "layers",
      profile: "neutral",
      debug: false,
      enabled: [
      ],
      enabledCount: 0,
      motionEnabled: false
    }
  },
] as const;

