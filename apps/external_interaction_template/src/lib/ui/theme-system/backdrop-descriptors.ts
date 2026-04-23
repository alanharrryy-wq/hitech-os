import type { UiThemeId } from "@/lib/ui/theme-system/types";

export interface BackdropParticleDescriptor {
  id: string;
  x: number;
  y: number;
  size: number;
  opacity: number;
  driftX: number;
  driftY: number;
  blur: number;
  delay: number;
  cadenceBand: 3 | 5 | 10;
}

export interface BackdropSparkleDescriptor {
  id: string;
  x: number;
  y: number;
  size: number;
  opacity: number;
  delay: number;
  cadenceBand: 5 | 10;
}

export interface BackdropDescriptorSet {
  nearParticles: readonly BackdropParticleDescriptor[];
  farParticles: readonly BackdropParticleDescriptor[];
  sparkles: readonly BackdropSparkleDescriptor[];
}

function xmur3(seed: string): () => number {
  let h = 1779033703 ^ seed.length;
  for (let i = 0; i < seed.length; i += 1) {
    h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  return () => {
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    return (h ^= h >>> 16) >>> 0;
  };
}

function mulberry32(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function seeded(seed: string): () => number {
  const seedHash = xmur3(seed)();
  return mulberry32(seedHash);
}

function sampleCadenceBand(random: () => number): 3 | 5 | 10 {
  const value = random();
  if (value < 0.22) return 3;
  if (value < 0.54) return 5;
  return 10;
}

function round(value: number, fractionDigits = 3): number {
  return Number(value.toFixed(fractionDigits));
}

function createParticles({
  seed,
  count,
  sizeRange,
  opacityRange,
  driftRange,
  blurRange
}: {
  seed: string;
  count: number;
  sizeRange: [number, number];
  opacityRange: [number, number];
  driftRange: [number, number];
  blurRange: [number, number];
}): readonly BackdropParticleDescriptor[] {
  const random = seeded(seed);

  return Array.from({ length: count }, (_, index) => {
    const size = sizeRange[0] + (sizeRange[1] - sizeRange[0]) * random();
    const opacity = opacityRange[0] + (opacityRange[1] - opacityRange[0]) * random();
    const driftX = driftRange[0] + (driftRange[1] - driftRange[0]) * random();
    const driftY = driftRange[0] + (driftRange[1] - driftRange[0]) * random();
    const blur = blurRange[0] + (blurRange[1] - blurRange[0]) * random();

    return {
      id: `${seed}-particle-${index}`,
      x: round(4 + random() * 92, 2),
      y: round(5 + random() * 90, 2),
      size: round(size, 2),
      opacity: round(opacity, 3),
      driftX: round(driftX, 2),
      driftY: round(driftY, 2),
      blur: round(blur, 2),
      delay: round(random() * 2.4, 3),
      cadenceBand: sampleCadenceBand(random)
    };
  });
}

function createSparkles({
  seed,
  count,
  sizeRange,
  opacityRange
}: {
  seed: string;
  count: number;
  sizeRange: [number, number];
  opacityRange: [number, number];
}): readonly BackdropSparkleDescriptor[] {
  const random = seeded(seed);

  return Array.from({ length: count }, (_, index) => ({
    id: `${seed}-sparkle-${index}`,
    x: round(6 + random() * 88, 2),
    y: round(8 + random() * 84, 2),
    size: round(sizeRange[0] + (sizeRange[1] - sizeRange[0]) * random(), 2),
    opacity: round(opacityRange[0] + (opacityRange[1] - opacityRange[0]) * random(), 3),
    delay: round(random() * 2.2, 3),
    cadenceBand: random() < 0.6 ? 5 : 10
  }));
}

function createDescriptorSet(themeId: UiThemeId): BackdropDescriptorSet {
  switch (themeId) {
    case "aurora":
      return {
        nearParticles: createParticles({
          seed: "aurora-near",
          count: 28,
          sizeRange: [0.2, 0.58],
          opacityRange: [0.24, 0.62],
          driftRange: [-26, 26],
          blurRange: [0.25, 1.35]
        }),
        farParticles: createParticles({
          seed: "aurora-far",
          count: 44,
          sizeRange: [0.1, 0.35],
          opacityRange: [0.12, 0.36],
          driftRange: [-22, 22],
          blurRange: [0.45, 1.85]
        }),
        sparkles: createSparkles({
          seed: "aurora-sparkle",
          count: 12,
          sizeRange: [0.12, 0.34],
          opacityRange: [0.24, 0.62]
        })
      };
    case "neon":
      return {
        nearParticles: createParticles({
          seed: "neon-near",
          count: 26,
          sizeRange: [0.22, 0.6],
          opacityRange: [0.24, 0.66],
          driftRange: [-24, 24],
          blurRange: [0.2, 1.25]
        }),
        farParticles: createParticles({
          seed: "neon-far",
          count: 40,
          sizeRange: [0.1, 0.32],
          opacityRange: [0.12, 0.38],
          driftRange: [-21, 21],
          blurRange: [0.4, 1.8]
        }),
        sparkles: createSparkles({
          seed: "neon-sparkle",
          count: 13,
          sizeRange: [0.12, 0.34],
          opacityRange: [0.26, 0.68]
        })
      };
    case "slot_01":
      return {
        nearParticles: createParticles({
          seed: "slot01-near",
          count: 14,
          sizeRange: [0.14, 0.36],
          opacityRange: [0.18, 0.38],
          driftRange: [-14, 14],
          blurRange: [0.2, 1.2]
        }),
        farParticles: createParticles({
          seed: "slot01-far",
          count: 24,
          sizeRange: [0.08, 0.24],
          opacityRange: [0.08, 0.24],
          driftRange: [-12, 12],
          blurRange: [0.4, 1.6]
        }),
        sparkles: createSparkles({
          seed: "slot01-sparkle",
          count: 7,
          sizeRange: [0.1, 0.24],
          opacityRange: [0.16, 0.38]
        })
      };
    case "slot_02":
      return {
        nearParticles: createParticles({
          seed: "slot02-near",
          count: 14,
          sizeRange: [0.14, 0.36],
          opacityRange: [0.18, 0.38],
          driftRange: [-14, 14],
          blurRange: [0.2, 1.2]
        }),
        farParticles: createParticles({
          seed: "slot02-far",
          count: 24,
          sizeRange: [0.08, 0.24],
          opacityRange: [0.08, 0.24],
          driftRange: [-12, 12],
          blurRange: [0.4, 1.6]
        }),
        sparkles: createSparkles({
          seed: "slot02-sparkle",
          count: 7,
          sizeRange: [0.1, 0.24],
          opacityRange: [0.16, 0.38]
        })
      };
    default:
      return {
        nearParticles: createParticles({
          seed: "solstice-near",
          count: 20,
          sizeRange: [0.18, 0.5],
          opacityRange: [0.2, 0.5],
          driftRange: [-20, 20],
          blurRange: [0.2, 1.25]
        }),
        farParticles: createParticles({
          seed: "solstice-far",
          count: 34,
          sizeRange: [0.1, 0.3],
          opacityRange: [0.1, 0.32],
          driftRange: [-18, 18],
          blurRange: [0.35, 1.65]
        }),
        sparkles: createSparkles({
          seed: "solstice-sparkle",
          count: 9,
          sizeRange: [0.1, 0.28],
          opacityRange: [0.18, 0.44]
        })
      };
  }
}

export const BACKDROP_DESCRIPTORS: Record<UiThemeId, BackdropDescriptorSet> = {
  aurora: createDescriptorSet("aurora"),
  solstice: createDescriptorSet("solstice"),
  neon: createDescriptorSet("neon"),
  slot_01: createDescriptorSet("slot_01"),
  slot_02: createDescriptorSet("slot_02")
};

export function getBackdropDescriptors(themeId: UiThemeId): BackdropDescriptorSet {
  return BACKDROP_DESCRIPTORS[themeId];
}
