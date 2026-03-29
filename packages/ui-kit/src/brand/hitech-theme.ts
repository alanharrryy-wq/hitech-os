export type HitechBrandColorName =
  | "gold"
  | "tealDeep"
  | "cyan"
  | "amberDark"
  | "ink"
  | "inkSoft"
  | "paper"
  | "paperSoft";

export type HitechTone = "neutral" | "primary" | "secondary" | "critical" | "hold" | "pass" | "block";

export interface HitechColorScale {
  readonly 25: string;
  readonly 50: string;
  readonly 100: string;
  readonly 200: string;
  readonly 300: string;
  readonly 400: string;
  readonly 500: string;
  readonly 600: string;
  readonly 700: string;
  readonly 800: string;
  readonly 900: string;
}

export interface HitechGradientRecipe {
  readonly id: string;
  readonly value: string;
  readonly subtleValue: string;
}

export interface HitechGlowRecipe {
  readonly id: string;
  readonly value: string;
  readonly strongValue: string;
}

export interface HitechStrokeRecipe {
  readonly id: string;
  readonly value: string;
}

export interface HitechNoiseRecipe {
  readonly id: string;
  readonly value: string;
}

export interface HitechThemeModule {
  readonly id: "hitech-premium";
  readonly colors: Record<HitechBrandColorName, string>;
  readonly scales: {
    readonly gold: HitechColorScale;
    readonly teal: HitechColorScale;
    readonly cyan: HitechColorScale;
    readonly amber: HitechColorScale;
    readonly neutral: HitechColorScale;
  };
  readonly gradients: readonly HitechGradientRecipe[];
  readonly glows: readonly HitechGlowRecipe[];
  readonly strokes: readonly HitechStrokeRecipe[];
  readonly noise: readonly HitechNoiseRecipe[];
  readonly cssVariables: Readonly<Record<string, string>>;
  readonly cssText: string;
}

export const HITECH_BRAND_COLORS: Readonly<Record<HitechBrandColorName, string>> = {
  gold: "#AB7B26",
  tealDeep: "#026F86",
  cyan: "#02A7CA",
  amberDark: "#553E13",
  ink: "#11151A",
  inkSoft: "#1A2028",
  paper: "#F4F8FB",
  paperSoft: "#DDE7EF"
};

export const HITECH_STATUS_COLORS = {
  pass: "#02A7CA",
  hold: "#AB7B26",
  block: "#553E13",
  critical: "#9D2E2E"
} as const;

const GOLD_SCALE: HitechColorScale = {
  25: "#FBF6EB",
  50: "#F7ECD7",
  100: "#EED9AD",
  200: "#E6C783",
  300: "#D9AF59",
  400: "#C9953B",
  500: "#AB7B26",
  600: "#8B601D",
  700: "#6B4915",
  800: "#4B320D",
  900: "#2A1A05"
};

const TEAL_SCALE: HitechColorScale = {
  25: "#E8F4F7",
  50: "#D2E9EE",
  100: "#A4D4DD",
  200: "#76BECC",
  300: "#49A8BB",
  400: "#1D93A2",
  500: "#026F86",
  600: "#025A6C",
  700: "#014552",
  800: "#01303A",
  900: "#001C21"
};

const CYAN_SCALE: HitechColorScale = {
  25: "#E9F9FC",
  50: "#D3F3F9",
  100: "#A6E6F2",
  200: "#79DAEC",
  300: "#4CCDE5",
  400: "#1FC1DE",
  500: "#02A7CA",
  600: "#0186A1",
  700: "#016477",
  800: "#00424E",
  900: "#002125"
};

const AMBER_SCALE: HitechColorScale = {
  25: "#F5F0E6",
  50: "#ECE0CC",
  100: "#D8C199",
  200: "#C5A266",
  300: "#B18333",
  400: "#916920",
  500: "#553E13",
  600: "#45320F",
  700: "#35250B",
  800: "#241907",
  900: "#140D03"
};

const NEUTRAL_SCALE: HitechColorScale = {
  25: "#F4F8FB",
  50: "#EAF0F5",
  100: "#DDE7EF",
  200: "#CBD9E5",
  300: "#B7C7D4",
  400: "#8FA2B3",
  500: "#687C8E",
  600: "#4D6172",
  700: "#344757",
  800: "#1F2E3C",
  900: "#11151A"
};

function hexToRgbTriplet(hex: string): string {
  const normalized = hex.replace("#", "");
  const chunk = normalized.length === 3
    ? normalized
        .split("")
        .map((entry) => `${entry}${entry}`)
        .join("")
    : normalized;

  const value = Number.parseInt(chunk, 16);
  const red = (value >> 16) & 255;
  const green = (value >> 8) & 255;
  const blue = value & 255;
  return `${red} ${green} ${blue}`;
}

function hexToRgbTuple(hex: string): [number, number, number] {
  const normalized = hex.replace("#", "");
  const chunk = normalized.length === 3
    ? normalized
        .split("")
        .map((entry) => `${entry}${entry}`)
        .join("")
    : normalized;

  const value = Number.parseInt(chunk, 16);
  const red = (value >> 16) & 255;
  const green = (value >> 8) & 255;
  const blue = value & 255;
  return [red, green, blue];
}

function rgba(hex: string, alpha: number): string {
  const [r, g, b] = hexToRgbTuple(hex);
  return `rgba(${r}, ${g}, ${b}, ${alpha.toFixed(3)})`;
}

const BASE_GRADIENTS: readonly HitechGradientRecipe[] = [
  {
    id: "aurora-gold-cyan",
    value: `linear-gradient(132deg, ${rgba(HITECH_BRAND_COLORS.amberDark, 0.92)} 0%, ${rgba(HITECH_BRAND_COLORS.gold, 0.92)} 28%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.7)} 68%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.9)} 100%)`,
    subtleValue: `linear-gradient(132deg, ${rgba(HITECH_BRAND_COLORS.amberDark, 0.42)} 0%, ${rgba(HITECH_BRAND_COLORS.gold, 0.36)} 36%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.32)} 70%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.45)} 100%)`
  },
  {
    id: "control-room-horizon",
    value: `linear-gradient(180deg, ${rgba(HITECH_BRAND_COLORS.ink, 0.95)} 0%, ${rgba(HITECH_BRAND_COLORS.inkSoft, 0.88)} 40%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.6)} 76%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.6)} 100%)`,
    subtleValue: `linear-gradient(180deg, ${rgba(HITECH_BRAND_COLORS.ink, 0.8)} 0%, ${rgba(HITECH_BRAND_COLORS.inkSoft, 0.72)} 44%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.34)} 82%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.3)} 100%)`
  },
  {
    id: "bezel-angled",
    value: `linear-gradient(112deg, ${rgba(HITECH_BRAND_COLORS.paper, 0.64)} 0%, ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.3)} 18%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.24)} 56%, ${rgba(HITECH_BRAND_COLORS.ink, 0.35)} 100%)`,
    subtleValue: `linear-gradient(112deg, ${rgba(HITECH_BRAND_COLORS.paper, 0.32)} 0%, ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.2)} 22%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.16)} 66%, ${rgba(HITECH_BRAND_COLORS.ink, 0.22)} 100%)`
  },
  {
    id: "pharma-coolflow",
    value: `linear-gradient(140deg, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.98)} 2%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.92)} 44%, ${rgba(HITECH_BRAND_COLORS.paper, 0.72)} 100%)`,
    subtleValue: `linear-gradient(140deg, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.4)} 2%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.38)} 52%, ${rgba(HITECH_BRAND_COLORS.paper, 0.34)} 100%)`
  },
  {
    id: "risk-amber-gold",
    value: `linear-gradient(120deg, ${rgba(HITECH_BRAND_COLORS.amberDark, 0.96)} 0%, ${rgba(HITECH_BRAND_COLORS.gold, 0.76)} 48%, ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.62)} 100%)`,
    subtleValue: `linear-gradient(120deg, ${rgba(HITECH_BRAND_COLORS.amberDark, 0.42)} 0%, ${rgba(HITECH_BRAND_COLORS.gold, 0.35)} 52%, ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.35)} 100%)`
  },
  {
    id: "neon-ridge",
    value: `linear-gradient(92deg, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.85)} 0%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.88)} 51%, ${rgba(HITECH_BRAND_COLORS.gold, 0.5)} 100%)`,
    subtleValue: `linear-gradient(92deg, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.32)} 0%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.36)} 56%, ${rgba(HITECH_BRAND_COLORS.gold, 0.24)} 100%)`
  },
  {
    id: "liquid-panel",
    value: `radial-gradient(circle at 20% 20%, ${rgba(HITECH_BRAND_COLORS.paper, 0.36)} 0%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.24)} 40%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.38)} 70%, ${rgba(HITECH_BRAND_COLORS.ink, 0.8)} 100%)`,
    subtleValue: `radial-gradient(circle at 20% 20%, ${rgba(HITECH_BRAND_COLORS.paper, 0.24)} 0%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.16)} 44%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.24)} 72%, ${rgba(HITECH_BRAND_COLORS.ink, 0.56)} 100%)`
  },
  {
    id: "halo-band",
    value: `linear-gradient(90deg, ${rgba(HITECH_BRAND_COLORS.gold, 0.15)} 0%, ${rgba(HITECH_BRAND_COLORS.gold, 0.66)} 20%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.75)} 56%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.5)} 100%)`,
    subtleValue: `linear-gradient(90deg, ${rgba(HITECH_BRAND_COLORS.gold, 0.08)} 0%, ${rgba(HITECH_BRAND_COLORS.gold, 0.34)} 20%, ${rgba(HITECH_BRAND_COLORS.cyan, 0.36)} 56%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.26)} 100%)`
  },
  {
    id: "glass-plaque",
    value: `linear-gradient(160deg, ${rgba(HITECH_BRAND_COLORS.paper, 0.6)} 0%, ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.3)} 30%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.18)} 78%, ${rgba(HITECH_BRAND_COLORS.ink, 0.4)} 100%)`,
    subtleValue: `linear-gradient(160deg, ${rgba(HITECH_BRAND_COLORS.paper, 0.32)} 0%, ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.2)} 34%, ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.14)} 80%, ${rgba(HITECH_BRAND_COLORS.ink, 0.26)} 100%)`
  },
  {
    id: "compliance-alert",
    value: `linear-gradient(145deg, ${rgba(HITECH_STATUS_COLORS.critical, 0.92)} 0%, ${rgba(HITECH_BRAND_COLORS.amberDark, 0.85)} 42%, ${rgba(HITECH_BRAND_COLORS.gold, 0.68)} 100%)`,
    subtleValue: `linear-gradient(145deg, ${rgba(HITECH_STATUS_COLORS.critical, 0.38)} 0%, ${rgba(HITECH_BRAND_COLORS.amberDark, 0.35)} 42%, ${rgba(HITECH_BRAND_COLORS.gold, 0.26)} 100%)`
  }
];

const BASE_GLOWS: readonly HitechGlowRecipe[] = [
  {
    id: "cyan-halo",
    value: `0 0 0.5rem ${rgba(HITECH_BRAND_COLORS.cyan, 0.35)}, 0 0 2.2rem ${rgba(HITECH_BRAND_COLORS.cyan, 0.25)}`,
    strongValue: `0 0 0.75rem ${rgba(HITECH_BRAND_COLORS.cyan, 0.54)}, 0 0 3rem ${rgba(HITECH_BRAND_COLORS.cyan, 0.34)}`
  },
  {
    id: "teal-field",
    value: `0 0 0.44rem ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.32)}, 0 0 1.8rem ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.28)}`,
    strongValue: `0 0 0.7rem ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.52)}, 0 0 2.6rem ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.36)}`
  },
  {
    id: "gold-rim",
    value: `0 0 0.34rem ${rgba(HITECH_BRAND_COLORS.gold, 0.32)}, 0 0 1.4rem ${rgba(HITECH_BRAND_COLORS.gold, 0.24)}`,
    strongValue: `0 0 0.62rem ${rgba(HITECH_BRAND_COLORS.gold, 0.54)}, 0 0 2rem ${rgba(HITECH_BRAND_COLORS.gold, 0.34)}`
  },
  {
    id: "amber-safety",
    value: `0 0 0.3rem ${rgba(HITECH_BRAND_COLORS.amberDark, 0.35)}, 0 0 1.6rem ${rgba(HITECH_BRAND_COLORS.amberDark, 0.24)}`,
    strongValue: `0 0 0.58rem ${rgba(HITECH_BRAND_COLORS.amberDark, 0.52)}, 0 0 2.2rem ${rgba(HITECH_BRAND_COLORS.amberDark, 0.32)}`
  },
  {
    id: "critical-alert",
    value: `0 0 0.36rem ${rgba(HITECH_STATUS_COLORS.critical, 0.38)}, 0 0 1.6rem ${rgba(HITECH_STATUS_COLORS.critical, 0.22)}`,
    strongValue: `0 0 0.64rem ${rgba(HITECH_STATUS_COLORS.critical, 0.56)}, 0 0 2.6rem ${rgba(HITECH_STATUS_COLORS.critical, 0.34)}`
  }
];

const BASE_STROKES: readonly HitechStrokeRecipe[] = [
  {
    id: "hairline-neutral",
    value: `inset 0 0 0 1px ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.38)}`
  },
  {
    id: "hairline-cyan",
    value: `inset 0 0 0 1px ${rgba(HITECH_BRAND_COLORS.cyan, 0.48)}`
  },
  {
    id: "hairline-gold",
    value: `inset 0 0 0 1px ${rgba(HITECH_BRAND_COLORS.gold, 0.48)}`
  },
  {
    id: "double-frame",
    value: `inset 0 0 0 1px ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.42)}, inset 0 0 0 2px ${rgba(HITECH_BRAND_COLORS.tealDeep, 0.18)}`
  },
  {
    id: "bezel-rich",
    value: `inset 0 1px 0 ${rgba(HITECH_BRAND_COLORS.paper, 0.5)}, inset 0 -1px 0 ${rgba(HITECH_BRAND_COLORS.ink, 0.45)}`
  }
];

const BASE_NOISE: readonly HitechNoiseRecipe[] = [
  {
    id: "grain-fine",
    value: `radial-gradient(${rgba(HITECH_BRAND_COLORS.ink, 0.08)} 0.34px, transparent 0.34px)`
  },
  {
    id: "grain-medium",
    value: `radial-gradient(${rgba(HITECH_BRAND_COLORS.ink, 0.11)} 0.42px, transparent 0.42px)`
  },
  {
    id: "grain-bright",
    value: `radial-gradient(${rgba(HITECH_BRAND_COLORS.paper, 0.13)} 0.48px, transparent 0.48px)`
  },
  {
    id: "scanline-soft",
    value: `linear-gradient(transparent 0, transparent calc(100% - 1px), ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.16)} calc(100% - 1px), ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.16)} 100%)`
  },
  {
    id: "scanline-neon",
    value: `linear-gradient(transparent 0, transparent calc(100% - 1px), ${rgba(HITECH_BRAND_COLORS.cyan, 0.16)} calc(100% - 1px), ${rgba(HITECH_BRAND_COLORS.cyan, 0.16)} 100%)`
  }
];

function createRamp<T extends { id: string }>(
  source: readonly T[],
  count: number,
  map: (entry: T, index: number) => T
): readonly T[] {
  if (source.length === 0) {
    return [];
  }

  const output: T[] = [];
  for (let index = 0; index < count; index += 1) {
    const base = source[index % source.length]!;
    output.push(map(base, index));
  }
  return output;
}

function withSuffix(id: string, index: number): string {
  const bucket = index + 1;
  return `${id}-${String(bucket).padStart(3, "0")}`;
}

const gradients = createRamp(BASE_GRADIENTS, 96, (entry, index) => {
  const alphaShift = 0.04 * ((index % 6) - 3);
  const baseOpacity = Math.max(0.14, 0.64 + alphaShift);
  const topOpacity = Math.max(0.2, 0.88 + alphaShift);
  return {
    id: withSuffix(entry.id, index),
    value: `${entry.value}, radial-gradient(circle at ${(index * 17) % 100}% ${(index * 19) % 100}%, ${rgba(HITECH_BRAND_COLORS.paper, baseOpacity * 0.3)} 0%, transparent 60%)`,
    subtleValue: `${entry.subtleValue}, radial-gradient(circle at ${(index * 13) % 100}% ${(index * 7) % 100}%, ${rgba(HITECH_BRAND_COLORS.paperSoft, topOpacity * 0.14)} 0%, transparent 65%)`
  };
});

const glows = createRamp(BASE_GLOWS, 72, (entry, index) => {
  const step = 0.02 * (index % 5);
  const softened = entry.value.replace(/0\.(\d+)/g, (match) => {
    const parsed = Number.parseFloat(match);
    return `${Math.max(0.04, parsed - step).toFixed(3)}`;
  });
  const stronger = entry.strongValue.replace(/0\.(\d+)/g, (match) => {
    const parsed = Number.parseFloat(match);
    return `${Math.min(0.95, parsed + step).toFixed(3)}`;
  });
  return {
    id: withSuffix(entry.id, index),
    value: softened,
    strongValue: stronger
  };
});

const strokes = createRamp(BASE_STROKES, 54, (entry, index) => {
  const offset = (index % 4) + 1;
  return {
    id: withSuffix(entry.id, index),
    value: `${entry.value}, inset 0 ${offset}px ${offset * 2}px ${rgba(HITECH_BRAND_COLORS.ink, 0.11 + index * 0.002)}`
  };
});

const noise = createRamp(BASE_NOISE, 48, (entry, index) => {
  const size = 2 + (index % 6);
  return {
    id: withSuffix(entry.id, index),
    value: entry.value,
    size
  };
}).map((entry) => ({
  id: entry.id,
  value: entry.value
}));

function pushScaleVariables(target: Record<string, string>, prefix: string, scale: HitechColorScale): void {
  target[`--hitech-${prefix}-025`] = scale[25];
  target[`--hitech-${prefix}-050`] = scale[50];
  target[`--hitech-${prefix}-100`] = scale[100];
  target[`--hitech-${prefix}-200`] = scale[200];
  target[`--hitech-${prefix}-300`] = scale[300];
  target[`--hitech-${prefix}-400`] = scale[400];
  target[`--hitech-${prefix}-500`] = scale[500];
  target[`--hitech-${prefix}-600`] = scale[600];
  target[`--hitech-${prefix}-700`] = scale[700];
  target[`--hitech-${prefix}-800`] = scale[800];
  target[`--hitech-${prefix}-900`] = scale[900];
}

function createCssVariables(): Record<string, string> {
  const vars: Record<string, string> = {
    "--hitech-color-gold": HITECH_BRAND_COLORS.gold,
    "--hitech-color-teal": HITECH_BRAND_COLORS.tealDeep,
    "--hitech-color-cyan": HITECH_BRAND_COLORS.cyan,
    "--hitech-color-amber-dark": HITECH_BRAND_COLORS.amberDark,
    "--hitech-color-ink": HITECH_BRAND_COLORS.ink,
    "--hitech-color-ink-soft": HITECH_BRAND_COLORS.inkSoft,
    "--hitech-color-paper": HITECH_BRAND_COLORS.paper,
    "--hitech-color-paper-soft": HITECH_BRAND_COLORS.paperSoft,
    "--hitech-rgb-gold": hexToRgbTriplet(HITECH_BRAND_COLORS.gold),
    "--hitech-rgb-teal": hexToRgbTriplet(HITECH_BRAND_COLORS.tealDeep),
    "--hitech-rgb-cyan": hexToRgbTriplet(HITECH_BRAND_COLORS.cyan),
    "--hitech-rgb-amber-dark": hexToRgbTriplet(HITECH_BRAND_COLORS.amberDark),
    "--hitech-rgb-ink": hexToRgbTriplet(HITECH_BRAND_COLORS.ink),
    "--hitech-rgb-paper": hexToRgbTriplet(HITECH_BRAND_COLORS.paper),
    "--hitech-rgb-paper-soft": hexToRgbTriplet(HITECH_BRAND_COLORS.paperSoft),
    "--hitech-radius-card": "20px",
    "--hitech-radius-panel": "16px",
    "--hitech-radius-control": "999px",
    "--hitech-shadow-ambient": `0 12px 32px ${rgba(HITECH_BRAND_COLORS.ink, 0.38)}`,
    "--hitech-shadow-floating": `0 24px 52px ${rgba(HITECH_BRAND_COLORS.ink, 0.34)}`,
    "--hitech-shadow-neon": `0 0 1rem ${rgba(HITECH_BRAND_COLORS.cyan, 0.3)}, 0 0 3rem ${rgba(HITECH_BRAND_COLORS.cyan, 0.2)}`,
    "--hitech-stroke": `inset 0 0 0 1px ${rgba(HITECH_BRAND_COLORS.paperSoft, 0.4)}`,
    "--hitech-stroke-strong": `inset 0 0 0 1px ${rgba(HITECH_BRAND_COLORS.cyan, 0.6)}`,
    "--hitech-noise":
      BASE_NOISE[0]?.value ??
      "radial-gradient(rgba(0, 0, 0, 0) 0.5px, transparent 0.5px)"
  };

  pushScaleVariables(vars, "gold", GOLD_SCALE);
  pushScaleVariables(vars, "teal", TEAL_SCALE);
  pushScaleVariables(vars, "cyan", CYAN_SCALE);
  pushScaleVariables(vars, "amber", AMBER_SCALE);
  pushScaleVariables(vars, "neutral", NEUTRAL_SCALE);

  for (const [index, gradient] of gradients.entries()) {
    vars[`--hitech-gradient-${String(index + 1).padStart(3, "0")}`] = gradient.value;
    vars[`--hitech-gradient-subtle-${String(index + 1).padStart(3, "0")}`] = gradient.subtleValue;
  }

  for (const [index, glow] of glows.entries()) {
    vars[`--hitech-glow-${String(index + 1).padStart(3, "0")}`] = glow.value;
    vars[`--hitech-glow-strong-${String(index + 1).padStart(3, "0")}`] = glow.strongValue;
  }

  for (const [index, stroke] of strokes.entries()) {
    vars[`--hitech-stroke-${String(index + 1).padStart(3, "0")}`] = stroke.value;
  }

  for (const [index, grain] of noise.entries()) {
    vars[`--hitech-noise-${String(index + 1).padStart(3, "0")}`] = grain.value;
  }

  return vars;
}

function createCssText(vars: Readonly<Record<string, string>>): string {
  const lines = Object.entries(vars)
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([key, value]) => `  ${key}: ${value};`);

  return [":root {", ...lines, "}"].join("\n");
}

const cssVariables = createCssVariables();
const cssText = createCssText(cssVariables);

export const HITECH_THEME: HitechThemeModule = {
  id: "hitech-premium",
  colors: HITECH_BRAND_COLORS,
  scales: {
    gold: GOLD_SCALE,
    teal: TEAL_SCALE,
    cyan: CYAN_SCALE,
    amber: AMBER_SCALE,
    neutral: NEUTRAL_SCALE
  },
  gradients,
  glows,
  strokes,
  noise,
  cssVariables,
  cssText
};

export function getHitechGradient(id: string): HitechGradientRecipe | undefined {
  return HITECH_THEME.gradients.find((recipe) => recipe.id === id);
}

export function getHitechGlow(id: string): HitechGlowRecipe | undefined {
  return HITECH_THEME.glows.find((recipe) => recipe.id === id);
}

export function getHitechStroke(id: string): HitechStrokeRecipe | undefined {
  return HITECH_THEME.strokes.find((recipe) => recipe.id === id);
}

export function getHitechNoise(id: string): HitechNoiseRecipe | undefined {
  return HITECH_THEME.noise.find((recipe) => recipe.id === id);
}

export function resolveHitechToneColor(tone: HitechTone): string {
  switch (tone) {
    case "primary":
      return HITECH_BRAND_COLORS.cyan;
    case "secondary":
      return HITECH_BRAND_COLORS.gold;
    case "critical":
      return HITECH_STATUS_COLORS.critical;
    case "hold":
      return HITECH_STATUS_COLORS.hold;
    case "pass":
      return HITECH_STATUS_COLORS.pass;
    case "block":
      return HITECH_STATUS_COLORS.block;
    default:
      return HITECH_BRAND_COLORS.paperSoft;
  }
}

export function getHitechCssVariable(name: string): string {
  return `var(${name})`;
}

export function getHitechGradientVar(index: number): string {
  const safe = Math.max(1, Math.min(index, HITECH_THEME.gradients.length));
  return `var(--hitech-gradient-${String(safe).padStart(3, "0")})`;
}

export function getHitechGlowVar(index: number, strong = false): string {
  const safe = Math.max(1, Math.min(index, HITECH_THEME.glows.length));
  const prefix = strong ? "--hitech-glow-strong" : "--hitech-glow";
  return `var(${prefix}-${String(safe).padStart(3, "0")})`;
}

export function getHitechStrokeVar(index: number): string {
  const safe = Math.max(1, Math.min(index, HITECH_THEME.strokes.length));
  return `var(--hitech-stroke-${String(safe).padStart(3, "0")})`;
}

export function getHitechNoiseVar(index: number): string {
  const safe = Math.max(1, Math.min(index, HITECH_THEME.noise.length));
  return `var(--hitech-noise-${String(safe).padStart(3, "0")})`;
}

export function getHitechThemeCssText(): string {
  return cssText;
}

export function getHitechThemeCssVariables(): Readonly<Record<string, string>> {
  return cssVariables;
}
