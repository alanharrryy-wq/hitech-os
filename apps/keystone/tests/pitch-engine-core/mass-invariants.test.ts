import { describe, expect, it } from "vitest";
import {
  canonicalizePitchProgram,
  canonicalizeSequence,
  deserializePitchProgram,
  deserializeSequence,
  hashPitchProgram,
  hashSequence,
  resolveDirectorCapability,
  serializePitchProgram,
  serializeSequence,
  validatePitchProgram,
  validateSequence
} from "../../lib/pitch-engine/index.js";
import { createPitchProgram, createSequence } from "./fixtures.js";

describe("mass invariants", () => {
  it("program variant 001 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.001",
      title: "Mass Program 1",
      tags: ["tag1", "tag1", "tag1"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 387,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 131, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-1"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 523,
          markers: ["CTA", "CTA-1"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 002 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.002",
      title: "Mass Program 2",
      tags: ["tag2", "tag2", "tag2"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 524,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 162, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-2"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 696,
          markers: ["CTA", "CTA-2"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 003 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.003",
      title: "Mass Program 3",
      tags: ["tag3", "tag3", "tag3"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 661,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 193, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-3"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 869,
          markers: ["CTA", "CTA-3"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 004 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.004",
      title: "Mass Program 4",
      tags: ["tag4", "tag4", "tag4"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 798,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 224, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-4"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1042,
          markers: ["CTA", "CTA-4"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 005 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.005",
      title: "Mass Program 5",
      tags: ["tag5", "tag5", "tag5"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 935,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 255, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-5"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1215,
          markers: ["CTA", "CTA-5"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 006 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.006",
      title: "Mass Program 6",
      tags: ["tag6", "tag6", "tag6"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1072,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 286, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-6"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1388,
          markers: ["CTA", "CTA-6"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 007 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.007",
      title: "Mass Program 7",
      tags: ["tag7", "tag0", "tag7"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1209,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 317, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-7"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1561,
          markers: ["CTA", "CTA-7"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 008 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.008",
      title: "Mass Program 8",
      tags: ["tag8", "tag1", "tag8"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1346,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 348, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-8"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1734,
          markers: ["CTA", "CTA-8"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 009 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.009",
      title: "Mass Program 9",
      tags: ["tag9", "tag2", "tag9"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1483,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 379, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-9"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1907,
          markers: ["CTA", "CTA-9"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 010 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.010",
      title: "Mass Program 10",
      tags: ["tag10", "tag3", "tag10"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1620,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 410, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-10"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2080,
          markers: ["CTA", "CTA-10"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 011 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.011",
      title: "Mass Program 11",
      tags: ["tag0", "tag4", "tag0"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1757,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 441, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-11"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2253,
          markers: ["CTA", "CTA-11"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 012 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.012",
      title: "Mass Program 12",
      tags: ["tag1", "tag5", "tag1"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1894,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 472, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-12"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2426,
          markers: ["CTA", "CTA-12"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 013 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.013",
      title: "Mass Program 13",
      tags: ["tag2", "tag6", "tag2"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2031,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 503, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-13"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2599,
          markers: ["CTA", "CTA-13"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 014 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.014",
      title: "Mass Program 14",
      tags: ["tag3", "tag0", "tag3"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2168,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 534, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-14"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2772,
          markers: ["CTA", "CTA-14"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 015 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.015",
      title: "Mass Program 15",
      tags: ["tag4", "tag1", "tag4"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2305,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 565, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-15"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2945,
          markers: ["CTA", "CTA-15"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 016 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.016",
      title: "Mass Program 16",
      tags: ["tag5", "tag2", "tag5"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2442,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 596, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-16"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3118,
          markers: ["CTA", "CTA-16"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 017 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.017",
      title: "Mass Program 17",
      tags: ["tag6", "tag3", "tag6"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2579,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 627, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-17"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3291,
          markers: ["CTA", "CTA-17"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 018 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.018",
      title: "Mass Program 18",
      tags: ["tag7", "tag4", "tag7"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2716,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 658, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-18"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3464,
          markers: ["CTA", "CTA-18"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 019 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.019",
      title: "Mass Program 19",
      tags: ["tag8", "tag5", "tag8"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2853,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 689, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-19"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3637,
          markers: ["CTA", "CTA-19"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 020 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.020",
      title: "Mass Program 20",
      tags: ["tag9", "tag6", "tag9"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2990,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 720, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-20"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3810,
          markers: ["CTA", "CTA-20"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 021 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.021",
      title: "Mass Program 21",
      tags: ["tag10", "tag0", "tag10"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3127,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 751, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-21"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3983,
          markers: ["CTA", "CTA-21"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 022 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.022",
      title: "Mass Program 22",
      tags: ["tag0", "tag1", "tag0"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3264,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 782, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-22"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4156,
          markers: ["CTA", "CTA-22"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 023 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.023",
      title: "Mass Program 23",
      tags: ["tag1", "tag2", "tag1"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3401,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 813, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-23"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4329,
          markers: ["CTA", "CTA-23"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 024 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.024",
      title: "Mass Program 24",
      tags: ["tag2", "tag3", "tag2"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3538,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 844, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-24"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4502,
          markers: ["CTA", "CTA-24"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 025 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.025",
      title: "Mass Program 25",
      tags: ["tag3", "tag4", "tag3"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3675,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 875, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-25"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4675,
          markers: ["CTA", "CTA-25"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 026 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.026",
      title: "Mass Program 26",
      tags: ["tag4", "tag5", "tag4"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3812,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 906, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-26"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4848,
          markers: ["CTA", "CTA-26"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 027 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.027",
      title: "Mass Program 27",
      tags: ["tag5", "tag6", "tag5"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3949,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 937, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-27"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5021,
          markers: ["CTA", "CTA-27"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 028 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.028",
      title: "Mass Program 28",
      tags: ["tag6", "tag0", "tag6"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4086,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 968, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-28"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5194,
          markers: ["CTA", "CTA-28"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 029 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.029",
      title: "Mass Program 29",
      tags: ["tag7", "tag1", "tag7"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4223,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 999, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-29"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5367,
          markers: ["CTA", "CTA-29"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 030 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.030",
      title: "Mass Program 30",
      tags: ["tag8", "tag2", "tag8"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4360,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1030, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-30"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5540,
          markers: ["CTA", "CTA-30"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 031 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.031",
      title: "Mass Program 31",
      tags: ["tag9", "tag3", "tag9"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4497,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1061, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-31"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5713,
          markers: ["CTA", "CTA-31"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 032 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.032",
      title: "Mass Program 32",
      tags: ["tag10", "tag4", "tag10"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4634,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1092, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-32"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5886,
          markers: ["CTA", "CTA-32"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 033 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.033",
      title: "Mass Program 33",
      tags: ["tag0", "tag5", "tag0"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4771,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1123, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-33"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6059,
          markers: ["CTA", "CTA-33"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 034 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.034",
      title: "Mass Program 34",
      tags: ["tag1", "tag6", "tag1"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4908,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1154, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-34"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6232,
          markers: ["CTA", "CTA-34"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 035 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.035",
      title: "Mass Program 35",
      tags: ["tag2", "tag0", "tag2"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5045,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1185, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-35"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6405,
          markers: ["CTA", "CTA-35"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 036 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.036",
      title: "Mass Program 36",
      tags: ["tag3", "tag1", "tag3"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5182,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1216, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-36"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6578,
          markers: ["CTA", "CTA-36"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 037 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.037",
      title: "Mass Program 37",
      tags: ["tag4", "tag2", "tag4"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5319,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1247, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-37"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6751,
          markers: ["CTA", "CTA-37"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 038 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.038",
      title: "Mass Program 38",
      tags: ["tag5", "tag3", "tag5"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5456,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1278, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-38"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6924,
          markers: ["CTA", "CTA-38"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 039 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.039",
      title: "Mass Program 39",
      tags: ["tag6", "tag4", "tag6"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5593,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 109, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-39"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 7097,
          markers: ["CTA", "CTA-39"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 040 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.040",
      title: "Mass Program 40",
      tags: ["tag7", "tag5", "tag7"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5730,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 140, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-40"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 7270,
          markers: ["CTA", "CTA-40"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 041 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.041",
      title: "Mass Program 41",
      tags: ["tag8", "tag6", "tag8"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5867,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 171, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-41"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 443,
          markers: ["CTA", "CTA-41"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 042 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.042",
      title: "Mass Program 42",
      tags: ["tag9", "tag0", "tag9"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 6004,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 202, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-42"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 616,
          markers: ["CTA", "CTA-42"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 043 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.043",
      title: "Mass Program 43",
      tags: ["tag10", "tag1", "tag10"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 6141,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 233, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-43"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 789,
          markers: ["CTA", "CTA-43"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 044 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.044",
      title: "Mass Program 44",
      tags: ["tag0", "tag2", "tag0"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 278,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 264, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-44"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 962,
          markers: ["CTA", "CTA-44"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 045 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.045",
      title: "Mass Program 45",
      tags: ["tag1", "tag3", "tag1"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 415,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 295, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-45"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1135,
          markers: ["CTA", "CTA-45"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 046 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.046",
      title: "Mass Program 46",
      tags: ["tag2", "tag4", "tag2"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 552,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 326, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-46"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1308,
          markers: ["CTA", "CTA-46"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 047 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.047",
      title: "Mass Program 47",
      tags: ["tag3", "tag5", "tag3"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 689,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 357, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-47"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1481,
          markers: ["CTA", "CTA-47"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 048 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.048",
      title: "Mass Program 48",
      tags: ["tag4", "tag6", "tag4"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 826,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 388, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-48"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1654,
          markers: ["CTA", "CTA-48"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 049 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.049",
      title: "Mass Program 49",
      tags: ["tag5", "tag0", "tag5"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 963,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 419, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-49"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1827,
          markers: ["CTA", "CTA-49"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 050 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.050",
      title: "Mass Program 50",
      tags: ["tag6", "tag1", "tag6"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1100,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 450, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-50"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2000,
          markers: ["CTA", "CTA-50"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 051 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.051",
      title: "Mass Program 51",
      tags: ["tag7", "tag2", "tag7"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1237,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 481, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-51"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2173,
          markers: ["CTA", "CTA-51"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 052 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.052",
      title: "Mass Program 52",
      tags: ["tag8", "tag3", "tag8"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1374,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 512, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-52"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2346,
          markers: ["CTA", "CTA-52"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 053 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.053",
      title: "Mass Program 53",
      tags: ["tag9", "tag4", "tag9"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1511,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 543, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-53"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2519,
          markers: ["CTA", "CTA-53"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 054 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.054",
      title: "Mass Program 54",
      tags: ["tag10", "tag5", "tag10"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1648,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 574, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-54"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2692,
          markers: ["CTA", "CTA-54"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 055 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.055",
      title: "Mass Program 55",
      tags: ["tag0", "tag6", "tag0"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1785,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 605, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-55"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2865,
          markers: ["CTA", "CTA-55"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 056 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.056",
      title: "Mass Program 56",
      tags: ["tag1", "tag0", "tag1"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1922,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 636, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-56"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3038,
          markers: ["CTA", "CTA-56"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 057 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.057",
      title: "Mass Program 57",
      tags: ["tag2", "tag1", "tag2"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2059,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 667, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-57"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3211,
          markers: ["CTA", "CTA-57"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 058 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.058",
      title: "Mass Program 58",
      tags: ["tag3", "tag2", "tag3"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2196,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 698, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-58"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3384,
          markers: ["CTA", "CTA-58"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 059 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.059",
      title: "Mass Program 59",
      tags: ["tag4", "tag3", "tag4"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2333,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 729, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-59"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3557,
          markers: ["CTA", "CTA-59"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 060 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.060",
      title: "Mass Program 60",
      tags: ["tag5", "tag4", "tag5"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2470,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 760, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-60"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3730,
          markers: ["CTA", "CTA-60"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 061 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.061",
      title: "Mass Program 61",
      tags: ["tag6", "tag5", "tag6"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2607,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 791, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-61"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3903,
          markers: ["CTA", "CTA-61"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 062 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.062",
      title: "Mass Program 62",
      tags: ["tag7", "tag6", "tag7"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2744,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 822, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-62"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4076,
          markers: ["CTA", "CTA-62"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 063 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.063",
      title: "Mass Program 63",
      tags: ["tag8", "tag0", "tag8"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2881,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 853, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-63"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4249,
          markers: ["CTA", "CTA-63"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 064 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.064",
      title: "Mass Program 64",
      tags: ["tag9", "tag1", "tag9"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3018,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 884, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-64"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4422,
          markers: ["CTA", "CTA-64"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 065 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.065",
      title: "Mass Program 65",
      tags: ["tag10", "tag2", "tag10"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3155,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 915, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-65"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4595,
          markers: ["CTA", "CTA-65"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 066 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.066",
      title: "Mass Program 66",
      tags: ["tag0", "tag3", "tag0"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3292,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 946, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-66"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4768,
          markers: ["CTA", "CTA-66"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 067 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.067",
      title: "Mass Program 67",
      tags: ["tag1", "tag4", "tag1"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3429,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 977, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-67"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4941,
          markers: ["CTA", "CTA-67"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 068 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.068",
      title: "Mass Program 68",
      tags: ["tag2", "tag5", "tag2"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3566,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1008, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-68"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5114,
          markers: ["CTA", "CTA-68"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 069 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.069",
      title: "Mass Program 69",
      tags: ["tag3", "tag6", "tag3"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3703,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1039, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-69"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5287,
          markers: ["CTA", "CTA-69"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 070 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.070",
      title: "Mass Program 70",
      tags: ["tag4", "tag0", "tag4"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3840,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1070, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-70"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5460,
          markers: ["CTA", "CTA-70"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 071 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.071",
      title: "Mass Program 71",
      tags: ["tag5", "tag1", "tag5"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3977,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1101, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-71"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5633,
          markers: ["CTA", "CTA-71"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 072 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.072",
      title: "Mass Program 72",
      tags: ["tag6", "tag2", "tag6"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4114,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1132, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-72"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5806,
          markers: ["CTA", "CTA-72"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 073 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.073",
      title: "Mass Program 73",
      tags: ["tag7", "tag3", "tag7"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4251,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1163, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-73"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5979,
          markers: ["CTA", "CTA-73"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 074 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.074",
      title: "Mass Program 74",
      tags: ["tag8", "tag4", "tag8"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4388,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1194, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-74"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6152,
          markers: ["CTA", "CTA-74"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 075 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.075",
      title: "Mass Program 75",
      tags: ["tag9", "tag5", "tag9"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4525,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1225, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-75"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6325,
          markers: ["CTA", "CTA-75"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 076 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.076",
      title: "Mass Program 76",
      tags: ["tag10", "tag6", "tag10"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4662,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1256, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-76"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6498,
          markers: ["CTA", "CTA-76"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 077 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.077",
      title: "Mass Program 77",
      tags: ["tag0", "tag0", "tag0"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4799,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1287, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-77"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6671,
          markers: ["CTA", "CTA-77"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 078 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.078",
      title: "Mass Program 78",
      tags: ["tag1", "tag1", "tag1"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4936,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 118, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-78"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6844,
          markers: ["CTA", "CTA-78"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 079 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.079",
      title: "Mass Program 79",
      tags: ["tag2", "tag2", "tag2"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5073,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 149, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-79"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 7017,
          markers: ["CTA", "CTA-79"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 080 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.080",
      title: "Mass Program 80",
      tags: ["tag3", "tag3", "tag3"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5210,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 180, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-80"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 7190,
          markers: ["CTA", "CTA-80"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 081 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.081",
      title: "Mass Program 81",
      tags: ["tag4", "tag4", "tag4"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5347,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 211, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-81"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 363,
          markers: ["CTA", "CTA-81"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 082 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.082",
      title: "Mass Program 82",
      tags: ["tag5", "tag5", "tag5"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5484,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 242, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-82"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 536,
          markers: ["CTA", "CTA-82"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 083 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.083",
      title: "Mass Program 83",
      tags: ["tag6", "tag6", "tag6"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5621,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 273, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-83"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 709,
          markers: ["CTA", "CTA-83"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 084 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.084",
      title: "Mass Program 84",
      tags: ["tag7", "tag0", "tag7"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5758,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 304, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-84"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 882,
          markers: ["CTA", "CTA-84"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 085 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.085",
      title: "Mass Program 85",
      tags: ["tag8", "tag1", "tag8"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5895,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 335, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-85"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1055,
          markers: ["CTA", "CTA-85"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 086 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.086",
      title: "Mass Program 86",
      tags: ["tag9", "tag2", "tag9"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 6032,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 366, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-86"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1228,
          markers: ["CTA", "CTA-86"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 087 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.087",
      title: "Mass Program 87",
      tags: ["tag10", "tag3", "tag10"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 6169,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 397, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-87"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1401,
          markers: ["CTA", "CTA-87"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 088 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.088",
      title: "Mass Program 88",
      tags: ["tag0", "tag4", "tag0"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 306,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 428, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-88"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1574,
          markers: ["CTA", "CTA-88"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 089 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.089",
      title: "Mass Program 89",
      tags: ["tag1", "tag5", "tag1"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 443,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 459, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-89"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1747,
          markers: ["CTA", "CTA-89"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 090 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.090",
      title: "Mass Program 90",
      tags: ["tag2", "tag6", "tag2"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 580,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 490, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-90"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1920,
          markers: ["CTA", "CTA-90"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 091 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.091",
      title: "Mass Program 91",
      tags: ["tag3", "tag0", "tag3"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 717,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 521, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-91"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2093,
          markers: ["CTA", "CTA-91"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 092 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.092",
      title: "Mass Program 92",
      tags: ["tag4", "tag1", "tag4"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 854,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 552, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-92"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2266,
          markers: ["CTA", "CTA-92"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 093 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.093",
      title: "Mass Program 93",
      tags: ["tag5", "tag2", "tag5"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 991,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 583, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-93"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2439,
          markers: ["CTA", "CTA-93"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 094 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.094",
      title: "Mass Program 94",
      tags: ["tag6", "tag3", "tag6"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1128,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 614, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-94"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2612,
          markers: ["CTA", "CTA-94"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 095 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.095",
      title: "Mass Program 95",
      tags: ["tag7", "tag4", "tag7"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1265,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 645, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-95"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2785,
          markers: ["CTA", "CTA-95"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 096 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.096",
      title: "Mass Program 96",
      tags: ["tag8", "tag5", "tag8"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1402,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 676, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-96"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2958,
          markers: ["CTA", "CTA-96"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 097 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.097",
      title: "Mass Program 97",
      tags: ["tag9", "tag6", "tag9"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1539,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 707, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-97"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3131,
          markers: ["CTA", "CTA-97"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 098 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.098",
      title: "Mass Program 98",
      tags: ["tag10", "tag0", "tag10"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1676,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 738, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-98"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3304,
          markers: ["CTA", "CTA-98"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 099 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.099",
      title: "Mass Program 99",
      tags: ["tag0", "tag1", "tag0"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1813,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 769, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-99"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3477,
          markers: ["CTA", "CTA-99"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 100 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.100",
      title: "Mass Program 100",
      tags: ["tag1", "tag2", "tag1"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1950,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 800, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-100"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3650,
          markers: ["CTA", "CTA-100"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 101 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.101",
      title: "Mass Program 101",
      tags: ["tag2", "tag3", "tag2"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2087,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 831, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-101"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3823,
          markers: ["CTA", "CTA-101"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 102 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.102",
      title: "Mass Program 102",
      tags: ["tag3", "tag4", "tag3"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2224,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 862, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-102"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3996,
          markers: ["CTA", "CTA-102"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 103 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.103",
      title: "Mass Program 103",
      tags: ["tag4", "tag5", "tag4"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2361,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 893, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-103"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4169,
          markers: ["CTA", "CTA-103"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 104 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.104",
      title: "Mass Program 104",
      tags: ["tag5", "tag6", "tag5"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2498,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 924, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-104"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4342,
          markers: ["CTA", "CTA-104"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 105 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.105",
      title: "Mass Program 105",
      tags: ["tag6", "tag0", "tag6"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2635,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 955, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-105"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4515,
          markers: ["CTA", "CTA-105"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 106 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.106",
      title: "Mass Program 106",
      tags: ["tag7", "tag1", "tag7"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2772,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 986, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-106"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4688,
          markers: ["CTA", "CTA-106"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 107 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.107",
      title: "Mass Program 107",
      tags: ["tag8", "tag2", "tag8"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2909,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1017, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-107"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4861,
          markers: ["CTA", "CTA-107"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 108 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.108",
      title: "Mass Program 108",
      tags: ["tag9", "tag3", "tag9"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3046,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1048, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-108"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5034,
          markers: ["CTA", "CTA-108"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 109 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.109",
      title: "Mass Program 109",
      tags: ["tag10", "tag4", "tag10"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3183,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1079, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-109"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5207,
          markers: ["CTA", "CTA-109"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 110 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.110",
      title: "Mass Program 110",
      tags: ["tag0", "tag5", "tag0"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3320,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1110, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-110"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5380,
          markers: ["CTA", "CTA-110"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 111 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.111",
      title: "Mass Program 111",
      tags: ["tag1", "tag6", "tag1"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3457,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1141, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-111"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5553,
          markers: ["CTA", "CTA-111"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 112 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.112",
      title: "Mass Program 112",
      tags: ["tag2", "tag0", "tag2"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3594,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1172, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-112"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5726,
          markers: ["CTA", "CTA-112"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 113 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.113",
      title: "Mass Program 113",
      tags: ["tag3", "tag1", "tag3"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3731,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1203, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-113"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5899,
          markers: ["CTA", "CTA-113"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 114 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.114",
      title: "Mass Program 114",
      tags: ["tag4", "tag2", "tag4"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3868,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1234, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-114"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6072,
          markers: ["CTA", "CTA-114"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 115 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.115",
      title: "Mass Program 115",
      tags: ["tag5", "tag3", "tag5"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4005,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1265, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-115"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6245,
          markers: ["CTA", "CTA-115"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 116 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.116",
      title: "Mass Program 116",
      tags: ["tag6", "tag4", "tag6"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4142,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1296, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-116"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6418,
          markers: ["CTA", "CTA-116"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 117 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.117",
      title: "Mass Program 117",
      tags: ["tag7", "tag5", "tag7"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4279,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 127, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-117"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6591,
          markers: ["CTA", "CTA-117"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 118 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.118",
      title: "Mass Program 118",
      tags: ["tag8", "tag6", "tag8"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4416,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 158, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-118"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6764,
          markers: ["CTA", "CTA-118"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 119 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.119",
      title: "Mass Program 119",
      tags: ["tag9", "tag0", "tag9"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4553,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 189, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-119"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6937,
          markers: ["CTA", "CTA-119"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 120 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.120",
      title: "Mass Program 120",
      tags: ["tag10", "tag1", "tag10"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4690,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 220, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-120"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 7110,
          markers: ["CTA", "CTA-120"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 121 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.121",
      title: "Mass Program 121",
      tags: ["tag0", "tag2", "tag0"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4827,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 251, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-121"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 7283,
          markers: ["CTA", "CTA-121"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 122 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.122",
      title: "Mass Program 122",
      tags: ["tag1", "tag3", "tag1"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4964,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 282, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-122"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 456,
          markers: ["CTA", "CTA-122"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 123 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.123",
      title: "Mass Program 123",
      tags: ["tag2", "tag4", "tag2"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5101,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 313, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-123"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 629,
          markers: ["CTA", "CTA-123"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 124 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.124",
      title: "Mass Program 124",
      tags: ["tag3", "tag5", "tag3"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5238,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 344, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-124"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 802,
          markers: ["CTA", "CTA-124"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 125 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.125",
      title: "Mass Program 125",
      tags: ["tag4", "tag6", "tag4"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5375,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 375, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-125"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 975,
          markers: ["CTA", "CTA-125"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 126 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.126",
      title: "Mass Program 126",
      tags: ["tag5", "tag0", "tag5"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5512,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 406, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-126"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1148,
          markers: ["CTA", "CTA-126"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 127 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.127",
      title: "Mass Program 127",
      tags: ["tag6", "tag1", "tag6"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5649,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 437, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-127"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1321,
          markers: ["CTA", "CTA-127"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 128 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.128",
      title: "Mass Program 128",
      tags: ["tag7", "tag2", "tag7"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5786,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 468, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-128"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1494,
          markers: ["CTA", "CTA-128"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 129 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.129",
      title: "Mass Program 129",
      tags: ["tag8", "tag3", "tag8"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5923,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 499, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-129"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1667,
          markers: ["CTA", "CTA-129"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 130 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.130",
      title: "Mass Program 130",
      tags: ["tag9", "tag4", "tag9"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 6060,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 530, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-130"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1840,
          markers: ["CTA", "CTA-130"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 131 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.131",
      title: "Mass Program 131",
      tags: ["tag10", "tag5", "tag10"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 6197,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 561, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-131"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2013,
          markers: ["CTA", "CTA-131"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 132 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.132",
      title: "Mass Program 132",
      tags: ["tag0", "tag6", "tag0"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 334,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 592, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-132"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2186,
          markers: ["CTA", "CTA-132"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 133 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.133",
      title: "Mass Program 133",
      tags: ["tag1", "tag0", "tag1"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 471,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 623, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-133"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2359,
          markers: ["CTA", "CTA-133"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 134 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.134",
      title: "Mass Program 134",
      tags: ["tag2", "tag1", "tag2"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 608,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 654, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-134"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2532,
          markers: ["CTA", "CTA-134"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 135 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.135",
      title: "Mass Program 135",
      tags: ["tag3", "tag2", "tag3"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 745,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 685, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-135"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2705,
          markers: ["CTA", "CTA-135"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 136 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.136",
      title: "Mass Program 136",
      tags: ["tag4", "tag3", "tag4"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 882,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 716, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-136"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2878,
          markers: ["CTA", "CTA-136"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 137 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.137",
      title: "Mass Program 137",
      tags: ["tag5", "tag4", "tag5"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1019,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 747, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-137"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3051,
          markers: ["CTA", "CTA-137"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 138 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.138",
      title: "Mass Program 138",
      tags: ["tag6", "tag5", "tag6"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1156,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 778, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-138"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3224,
          markers: ["CTA", "CTA-138"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 139 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.139",
      title: "Mass Program 139",
      tags: ["tag7", "tag6", "tag7"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1293,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 809, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-139"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3397,
          markers: ["CTA", "CTA-139"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 140 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.140",
      title: "Mass Program 140",
      tags: ["tag8", "tag0", "tag8"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1430,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 840, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-140"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3570,
          markers: ["CTA", "CTA-140"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 141 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.141",
      title: "Mass Program 141",
      tags: ["tag9", "tag1", "tag9"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1567,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 871, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-141"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3743,
          markers: ["CTA", "CTA-141"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 142 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.142",
      title: "Mass Program 142",
      tags: ["tag10", "tag2", "tag10"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1704,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 902, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-142"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3916,
          markers: ["CTA", "CTA-142"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 143 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.143",
      title: "Mass Program 143",
      tags: ["tag0", "tag3", "tag0"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1841,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 933, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-143"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4089,
          markers: ["CTA", "CTA-143"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 144 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.144",
      title: "Mass Program 144",
      tags: ["tag1", "tag4", "tag1"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1978,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 964, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-144"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4262,
          markers: ["CTA", "CTA-144"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 145 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.145",
      title: "Mass Program 145",
      tags: ["tag2", "tag5", "tag2"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2115,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 995, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-145"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4435,
          markers: ["CTA", "CTA-145"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 146 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.146",
      title: "Mass Program 146",
      tags: ["tag3", "tag6", "tag3"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2252,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1026, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-146"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4608,
          markers: ["CTA", "CTA-146"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 147 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.147",
      title: "Mass Program 147",
      tags: ["tag4", "tag0", "tag4"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2389,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1057, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-147"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4781,
          markers: ["CTA", "CTA-147"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 148 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.148",
      title: "Mass Program 148",
      tags: ["tag5", "tag1", "tag5"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2526,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1088, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-148"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4954,
          markers: ["CTA", "CTA-148"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 149 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.149",
      title: "Mass Program 149",
      tags: ["tag6", "tag2", "tag6"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2663,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1119, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-149"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5127,
          markers: ["CTA", "CTA-149"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 150 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.150",
      title: "Mass Program 150",
      tags: ["tag7", "tag3", "tag7"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2800,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1150, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-150"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5300,
          markers: ["CTA", "CTA-150"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 151 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.151",
      title: "Mass Program 151",
      tags: ["tag8", "tag4", "tag8"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2937,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1181, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-151"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5473,
          markers: ["CTA", "CTA-151"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 152 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.152",
      title: "Mass Program 152",
      tags: ["tag9", "tag5", "tag9"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3074,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1212, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-152"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5646,
          markers: ["CTA", "CTA-152"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 153 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.153",
      title: "Mass Program 153",
      tags: ["tag10", "tag6", "tag10"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3211,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1243, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-153"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5819,
          markers: ["CTA", "CTA-153"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 154 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.154",
      title: "Mass Program 154",
      tags: ["tag0", "tag0", "tag0"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3348,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1274, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-154"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5992,
          markers: ["CTA", "CTA-154"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 155 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.155",
      title: "Mass Program 155",
      tags: ["tag1", "tag1", "tag1"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3485,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 105, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-155"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6165,
          markers: ["CTA", "CTA-155"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 156 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.156",
      title: "Mass Program 156",
      tags: ["tag2", "tag2", "tag2"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3622,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 136, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-156"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6338,
          markers: ["CTA", "CTA-156"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 157 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.157",
      title: "Mass Program 157",
      tags: ["tag3", "tag3", "tag3"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3759,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 167, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-157"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6511,
          markers: ["CTA", "CTA-157"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 158 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.158",
      title: "Mass Program 158",
      tags: ["tag4", "tag4", "tag4"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3896,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 198, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-158"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6684,
          markers: ["CTA", "CTA-158"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 159 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.159",
      title: "Mass Program 159",
      tags: ["tag5", "tag5", "tag5"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4033,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 229, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-159"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6857,
          markers: ["CTA", "CTA-159"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 160 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.160",
      title: "Mass Program 160",
      tags: ["tag6", "tag6", "tag6"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4170,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 260, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-160"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 7030,
          markers: ["CTA", "CTA-160"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 161 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.161",
      title: "Mass Program 161",
      tags: ["tag7", "tag0", "tag7"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4307,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 291, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-161"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 7203,
          markers: ["CTA", "CTA-161"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 162 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.162",
      title: "Mass Program 162",
      tags: ["tag8", "tag1", "tag8"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4444,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 322, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-162"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 376,
          markers: ["CTA", "CTA-162"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 163 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.163",
      title: "Mass Program 163",
      tags: ["tag9", "tag2", "tag9"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4581,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 353, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-163"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 549,
          markers: ["CTA", "CTA-163"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 164 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.164",
      title: "Mass Program 164",
      tags: ["tag10", "tag3", "tag10"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4718,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 384, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-164"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 722,
          markers: ["CTA", "CTA-164"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 165 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.165",
      title: "Mass Program 165",
      tags: ["tag0", "tag4", "tag0"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4855,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 415, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-165"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 895,
          markers: ["CTA", "CTA-165"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 166 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.166",
      title: "Mass Program 166",
      tags: ["tag1", "tag5", "tag1"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 4992,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 446, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-166"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1068,
          markers: ["CTA", "CTA-166"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 167 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.167",
      title: "Mass Program 167",
      tags: ["tag2", "tag6", "tag2"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5129,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 477, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-167"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1241,
          markers: ["CTA", "CTA-167"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 168 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.168",
      title: "Mass Program 168",
      tags: ["tag3", "tag0", "tag3"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5266,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 508, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-168"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1414,
          markers: ["CTA", "CTA-168"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 169 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.169",
      title: "Mass Program 169",
      tags: ["tag4", "tag1", "tag4"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5403,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 539, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-169"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1587,
          markers: ["CTA", "CTA-169"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 170 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.170",
      title: "Mass Program 170",
      tags: ["tag5", "tag2", "tag5"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5540,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 570, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-170"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1760,
          markers: ["CTA", "CTA-170"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 171 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.171",
      title: "Mass Program 171",
      tags: ["tag6", "tag3", "tag6"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5677,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 601, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-171"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 1933,
          markers: ["CTA", "CTA-171"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 172 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.172",
      title: "Mass Program 172",
      tags: ["tag7", "tag4", "tag7"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5814,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 632, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-172"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2106,
          markers: ["CTA", "CTA-172"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 173 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.173",
      title: "Mass Program 173",
      tags: ["tag8", "tag5", "tag8"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 5951,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 663, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-173"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2279,
          markers: ["CTA", "CTA-173"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 174 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.174",
      title: "Mass Program 174",
      tags: ["tag9", "tag6", "tag9"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 6088,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 694, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-174"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2452,
          markers: ["CTA", "CTA-174"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 175 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.175",
      title: "Mass Program 175",
      tags: ["tag10", "tag0", "tag10"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 6225,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 725, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-175"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2625,
          markers: ["CTA", "CTA-175"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 176 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.176",
      title: "Mass Program 176",
      tags: ["tag0", "tag1", "tag0"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 362,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 756, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-176"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2798,
          markers: ["CTA", "CTA-176"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 177 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.177",
      title: "Mass Program 177",
      tags: ["tag1", "tag2", "tag1"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 499,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 787, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-177"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 2971,
          markers: ["CTA", "CTA-177"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 178 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.178",
      title: "Mass Program 178",
      tags: ["tag2", "tag3", "tag2"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 636,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 818, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-178"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3144,
          markers: ["CTA", "CTA-178"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 179 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.179",
      title: "Mass Program 179",
      tags: ["tag3", "tag4", "tag3"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 773,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 849, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-179"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3317,
          markers: ["CTA", "CTA-179"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 180 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.180",
      title: "Mass Program 180",
      tags: ["tag4", "tag5", "tag4"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 910,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 880, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-180"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3490,
          markers: ["CTA", "CTA-180"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 181 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.181",
      title: "Mass Program 181",
      tags: ["tag5", "tag6", "tag5"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1047,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 911, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-181"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3663,
          markers: ["CTA", "CTA-181"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 182 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.182",
      title: "Mass Program 182",
      tags: ["tag6", "tag0", "tag6"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1184,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 942, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-182"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 3836,
          markers: ["CTA", "CTA-182"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 183 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.183",
      title: "Mass Program 183",
      tags: ["tag7", "tag1", "tag7"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1321,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 973, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-183"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4009,
          markers: ["CTA", "CTA-183"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 184 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.184",
      title: "Mass Program 184",
      tags: ["tag8", "tag2", "tag8"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1458,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1004, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-184"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4182,
          markers: ["CTA", "CTA-184"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 185 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.185",
      title: "Mass Program 185",
      tags: ["tag9", "tag3", "tag9"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1595,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1035, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-185"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4355,
          markers: ["CTA", "CTA-185"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 186 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.186",
      title: "Mass Program 186",
      tags: ["tag10", "tag4", "tag10"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1732,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1066, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-186"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4528,
          markers: ["CTA", "CTA-186"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 187 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.187",
      title: "Mass Program 187",
      tags: ["tag0", "tag5", "tag0"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 1869,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1097, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-187"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4701,
          markers: ["CTA", "CTA-187"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 188 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.188",
      title: "Mass Program 188",
      tags: ["tag1", "tag6", "tag1"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2006,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1128, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-188"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 4874,
          markers: ["CTA", "CTA-188"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 189 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.189",
      title: "Mass Program 189",
      tags: ["tag2", "tag0", "tag2"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2143,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1159, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-189"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5047,
          markers: ["CTA", "CTA-189"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 190 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.190",
      title: "Mass Program 190",
      tags: ["tag3", "tag1", "tag3"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2280,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1190, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-190"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5220,
          markers: ["CTA", "CTA-190"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 191 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.191",
      title: "Mass Program 191",
      tags: ["tag4", "tag2", "tag4"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2417,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1221, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-191"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5393,
          markers: ["CTA", "CTA-191"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 192 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.192",
      title: "Mass Program 192",
      tags: ["tag5", "tag3", "tag5"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2554,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1252, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-192"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5566,
          markers: ["CTA", "CTA-192"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 193 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.193",
      title: "Mass Program 193",
      tags: ["tag6", "tag4", "tag6"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2691,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 1283, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-193"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5739,
          markers: ["CTA", "CTA-193"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 194 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.194",
      title: "Mass Program 194",
      tags: ["tag7", "tag5", "tag7"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2828,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 114, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-194"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 5912,
          markers: ["CTA", "CTA-194"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 195 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.195",
      title: "Mass Program 195",
      tags: ["tag8", "tag6", "tag8"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 2965,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 145, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-195"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6085,
          markers: ["CTA", "CTA-195"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 196 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.196",
      title: "Mass Program 196",
      tags: ["tag9", "tag0", "tag9"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3102,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 176, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-196"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6258,
          markers: ["CTA", "CTA-196"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 197 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.197",
      title: "Mass Program 197",
      tags: ["tag10", "tag1", "tag10"],
      capabilityRequest: { director: "lite" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3239,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 207, easing: "easeIn" },
          markers: ["Reveal", "Settle", "Marker-197"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6431,
          markers: ["CTA", "CTA-197"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 198 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.198",
      title: "Mass Program 198",
      tags: ["tag0", "tag2", "tag0"],
      capabilityRequest: { director: "full" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3376,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 238, easing: "easeOut" },
          markers: ["Reveal", "Settle", "Marker-198"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6604,
          markers: ["CTA", "CTA-198"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 199 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.199",
      title: "Mass Program 199",
      tags: ["tag1", "tag3", "tag1"],
      capabilityRequest: { director: "debug" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3513,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 269, easing: "easeInOut" },
          markers: ["Reveal", "Settle", "Marker-199"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6777,
          markers: ["CTA", "CTA-199"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("program variant 200 roundtrip hash invariant", () => {
    const program = createPitchProgram({
      programId: "program.mass.200",
      title: "Mass Program 200",
      tags: ["tag2", "tag4", "tag2"],
      capabilityRequest: { director: "off" },
      steps: [
        {
          ...createPitchProgram().steps[0],
          durationMs: 3650,
          transition: { ...createPitchProgram().steps[0]!.transition, ms: 300, easing: "linear" },
          markers: ["Reveal", "Settle", "Marker-200"]
        },
        {
          ...createPitchProgram().steps[1],
          durationMs: 6950,
          markers: ["CTA", "CTA-200"]
        }
      ]
    });
    const canonical = canonicalizePitchProgram(program);
    const serialized = serializePitchProgram(canonical);
    const reparsed = deserializePitchProgram(serialized);
    const validation = validatePitchProgram(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashPitchProgram(canonical)).toBe(hashPitchProgram(reparsed));
  });

  it("sequence variant 001 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.001",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 1", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-1", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 1", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 219, label: "Settle" },
          { tMs: 323, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 002 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.002",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 2", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-2", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 2", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 238, label: "Settle" },
          { tMs: 346, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 003 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.003",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 3", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-3", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 3", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 257, label: "Settle" },
          { tMs: 369, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 004 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.004",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 4", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-4", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 4", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 276, label: "Settle" },
          { tMs: 392, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 005 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.005",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 5", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-5", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 5", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 295, label: "Settle" },
          { tMs: 415, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 006 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.006",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 6", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-6", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 6", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 314, label: "Settle" },
          { tMs: 438, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 007 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.007",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 7", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-7", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 7", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 333, label: "Settle" },
          { tMs: 461, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 008 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.008",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 8", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-8", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 8", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 352, label: "Settle" },
          { tMs: 484, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 009 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.009",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 9", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-9", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 9", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 371, label: "Settle" },
          { tMs: 507, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 010 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.010",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 10", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-10", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 10", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 390, label: "Settle" },
          { tMs: 530, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 011 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.011",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 11", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-11", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 11", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 409, label: "Settle" },
          { tMs: 553, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 012 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.012",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 12", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-12", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 12", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 428, label: "Settle" },
          { tMs: 576, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 013 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.013",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 13", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-13", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 13", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 447, label: "Settle" },
          { tMs: 599, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 014 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.014",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 14", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-14", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 14", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 466, label: "Settle" },
          { tMs: 622, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 015 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.015",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 15", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-15", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 15", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 485, label: "Settle" },
          { tMs: 645, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 016 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.016",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 16", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-16", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 16", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 504, label: "Settle" },
          { tMs: 668, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 017 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.017",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 17", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-17", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 17", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 523, label: "Settle" },
          { tMs: 691, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 018 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.018",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 18", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-18", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 18", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 542, label: "Settle" },
          { tMs: 714, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 019 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.019",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 19", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-19", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 19", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 561, label: "Settle" },
          { tMs: 737, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 020 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.020",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 20", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-20", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 20", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 580, label: "Settle" },
          { tMs: 760, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 021 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.021",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 21", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-21", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 21", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 599, label: "Settle" },
          { tMs: 783, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 022 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.022",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 22", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-22", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 22", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 618, label: "Settle" },
          { tMs: 806, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 023 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.023",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 23", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-23", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 23", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 637, label: "Settle" },
          { tMs: 829, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 024 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.024",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 24", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-24", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 24", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 656, label: "Settle" },
          { tMs: 852, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 025 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.025",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 25", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-25", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 25", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 675, label: "Settle" },
          { tMs: 875, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 026 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.026",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 26", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-26", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 26", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 694, label: "Settle" },
          { tMs: 898, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 027 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.027",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 27", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-27", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 27", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 713, label: "Settle" },
          { tMs: 921, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 028 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.028",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 28", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-28", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 28", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 732, label: "Settle" },
          { tMs: 944, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 029 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.029",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 29", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-29", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 29", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 751, label: "Settle" },
          { tMs: 967, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 030 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.030",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 30", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-30", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 30", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 770, label: "Settle" },
          { tMs: 990, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 031 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.031",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 31", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-31", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 31", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 789, label: "Settle" },
          { tMs: 1013, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 032 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.032",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 32", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-32", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 32", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 808, label: "Settle" },
          { tMs: 1036, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 033 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.033",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 33", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-33", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 33", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 827, label: "Settle" },
          { tMs: 1059, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 034 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.034",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 34", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-34", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 34", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 846, label: "Settle" },
          { tMs: 1082, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 035 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.035",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 35", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-35", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 35", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 865, label: "Settle" },
          { tMs: 1105, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 036 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.036",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 36", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-36", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 36", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 884, label: "Settle" },
          { tMs: 1128, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 037 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.037",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 37", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-37", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 37", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 903, label: "Settle" },
          { tMs: 1151, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 038 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.038",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 38", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-38", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 38", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 922, label: "Settle" },
          { tMs: 1174, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 039 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.039",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 39", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-39", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 39", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 941, label: "Settle" },
          { tMs: 1197, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 040 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.040",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 40", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-40", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 40", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 960, label: "Settle" },
          { tMs: 1220, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 041 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.041",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 41", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-41", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 41", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 979, label: "Settle" },
          { tMs: 1243, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 042 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.042",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 42", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-42", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 42", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 998, label: "Settle" },
          { tMs: 1266, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 043 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.043",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 43", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-43", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 43", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1017, label: "Settle" },
          { tMs: 1289, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 044 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.044",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 44", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-44", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 44", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1036, label: "Settle" },
          { tMs: 1312, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 045 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.045",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 45", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-45", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 45", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1055, label: "Settle" },
          { tMs: 1335, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 046 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.046",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 46", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-46", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 46", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1074, label: "Settle" },
          { tMs: 1358, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 047 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.047",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 47", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-47", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 47", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1093, label: "Settle" },
          { tMs: 1381, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 048 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.048",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 48", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-48", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 48", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1112, label: "Settle" },
          { tMs: 1404, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 049 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.049",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 49", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-49", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 49", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1131, label: "Settle" },
          { tMs: 1427, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 050 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.050",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 50", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-50", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 50", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1150, label: "Settle" },
          { tMs: 1450, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 051 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.051",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 51", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-51", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 51", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1169, label: "Settle" },
          { tMs: 1473, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 052 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.052",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 52", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-52", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 52", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1188, label: "Settle" },
          { tMs: 1496, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 053 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.053",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 53", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-53", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 53", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1207, label: "Settle" },
          { tMs: 1519, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 054 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.054",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 54", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-54", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 54", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1226, label: "Settle" },
          { tMs: 1542, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 055 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.055",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 55", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-55", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 55", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1245, label: "Settle" },
          { tMs: 1565, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 056 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.056",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 56", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-56", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 56", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1264, label: "Settle" },
          { tMs: 1588, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 057 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.057",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 57", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-57", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 57", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1283, label: "Settle" },
          { tMs: 1611, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 058 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.058",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 58", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-58", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 58", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1302, label: "Settle" },
          { tMs: 1634, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 059 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.059",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 59", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-59", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 59", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1321, label: "Settle" },
          { tMs: 1657, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 060 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.060",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 60", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-60", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 60", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1340, label: "Settle" },
          { tMs: 1680, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 061 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.061",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 61", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-61", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 61", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1359, label: "Settle" },
          { tMs: 1703, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 062 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.062",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 62", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-62", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 62", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1378, label: "Settle" },
          { tMs: 1726, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 063 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.063",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 63", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-63", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 63", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1397, label: "Settle" },
          { tMs: 1749, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 064 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.064",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 64", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-64", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 64", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1416, label: "Settle" },
          { tMs: 1772, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 065 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.065",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 65", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-65", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 65", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1435, label: "Settle" },
          { tMs: 1795, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 066 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.066",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 66", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-66", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 66", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1454, label: "Settle" },
          { tMs: 1818, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 067 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.067",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 67", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-67", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 67", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1473, label: "Settle" },
          { tMs: 1841, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 068 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.068",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 68", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-68", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 68", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1492, label: "Settle" },
          { tMs: 1864, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 069 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.069",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 69", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-69", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 69", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1511, label: "Settle" },
          { tMs: 1887, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 070 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.070",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 70", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-70", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 70", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1530, label: "Settle" },
          { tMs: 1910, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 071 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.071",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 71", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-71", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 71", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1549, label: "Settle" },
          { tMs: 1933, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 072 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.072",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 72", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-72", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 72", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1568, label: "Settle" },
          { tMs: 1956, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 073 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.073",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 73", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-73", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 73", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1587, label: "Settle" },
          { tMs: 1979, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 074 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.074",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 74", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-74", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 74", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1606, label: "Settle" },
          { tMs: 2002, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 075 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.075",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 75", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-75", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 75", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1625, label: "Settle" },
          { tMs: 2025, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 076 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.076",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 76", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-76", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 76", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1644, label: "Settle" },
          { tMs: 2048, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 077 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.077",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 77", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-77", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 77", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1663, label: "Settle" },
          { tMs: 2071, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 078 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.078",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 78", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-78", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 78", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1682, label: "Settle" },
          { tMs: 2094, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 079 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.079",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 79", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-79", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 79", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1701, label: "Settle" },
          { tMs: 2117, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 080 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.080",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 80", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-80", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 80", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1720, label: "Settle" },
          { tMs: 2140, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 081 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.081",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 81", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-81", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 81", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1739, label: "Settle" },
          { tMs: 2163, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 082 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.082",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 82", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-82", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 82", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1758, label: "Settle" },
          { tMs: 2186, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 083 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.083",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 83", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-83", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 83", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1777, label: "Settle" },
          { tMs: 2209, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 084 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.084",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 84", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-84", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 84", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1796, label: "Settle" },
          { tMs: 2232, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 085 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.085",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 85", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-85", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 85", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1815, label: "Settle" },
          { tMs: 2255, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 086 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.086",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 86", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-86", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 86", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1834, label: "Settle" },
          { tMs: 2278, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 087 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.087",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 87", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-87", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 87", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1853, label: "Settle" },
          { tMs: 2301, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 088 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.088",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 88", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-88", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 88", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1872, label: "Settle" },
          { tMs: 2324, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 089 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.089",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 89", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-89", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 89", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1891, label: "Settle" },
          { tMs: 2347, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 090 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.090",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 90", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-90", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 90", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1910, label: "Settle" },
          { tMs: 2370, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 091 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.091",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 91", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-91", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 91", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1929, label: "Settle" },
          { tMs: 2393, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 092 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.092",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 92", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-92", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 92", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1948, label: "Settle" },
          { tMs: 2416, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 093 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.093",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 93", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-93", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 93", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1967, label: "Settle" },
          { tMs: 2439, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 094 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.094",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 94", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-94", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 94", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 1986, label: "Settle" },
          { tMs: 2462, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 095 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.095",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 95", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-95", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 95", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2005, label: "Settle" },
          { tMs: 2485, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 096 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.096",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 96", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-96", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 96", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2024, label: "Settle" },
          { tMs: 2508, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 097 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.097",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 97", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-97", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 97", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2043, label: "Settle" },
          { tMs: 2531, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 098 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.098",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 98", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-98", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 98", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2062, label: "Settle" },
          { tMs: 2554, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 099 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.099",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 99", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-99", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 99", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2081, label: "Settle" },
          { tMs: 2577, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 100 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.100",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 100", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-100", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 100", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2100, label: "Settle" },
          { tMs: 2600, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 101 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.101",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 101", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-101", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 101", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2119, label: "Settle" },
          { tMs: 2623, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 102 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.102",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 102", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-102", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 102", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2138, label: "Settle" },
          { tMs: 2646, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 103 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.103",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 103", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-103", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 103", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2157, label: "Settle" },
          { tMs: 2669, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 104 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.104",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 104", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-104", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 104", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2176, label: "Settle" },
          { tMs: 2692, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 105 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.105",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 105", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-105", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 105", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2195, label: "Settle" },
          { tMs: 2715, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 106 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.106",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 106", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-106", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 106", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2214, label: "Settle" },
          { tMs: 2738, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 107 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.107",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 107", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-107", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 107", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2233, label: "Settle" },
          { tMs: 2761, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 108 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.108",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 108", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-108", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 108", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2252, label: "Settle" },
          { tMs: 2784, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 109 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.109",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 109", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-109", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 109", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2271, label: "Settle" },
          { tMs: 2807, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 110 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.110",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 110", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-110", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 110", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2290, label: "Settle" },
          { tMs: 2830, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 111 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.111",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 111", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-111", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 111", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2309, label: "Settle" },
          { tMs: 2853, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 112 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.112",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 112", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-112", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 112", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2328, label: "Settle" },
          { tMs: 2876, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 113 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.113",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 113", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-113", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 113", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2347, label: "Settle" },
          { tMs: 2899, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 114 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.114",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 114", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-114", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 114", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2366, label: "Settle" },
          { tMs: 2922, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 115 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.115",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 115", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-115", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 115", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2385, label: "Settle" },
          { tMs: 2945, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 116 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.116",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 116", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-116", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 116", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2404, label: "Settle" },
          { tMs: 2968, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 117 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.117",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 117", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-117", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 117", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2423, label: "Settle" },
          { tMs: 2991, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 118 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.118",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 118", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-118", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 118", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2442, label: "Settle" },
          { tMs: 3014, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 119 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.119",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 119", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-119", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 119", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2461, label: "Settle" },
          { tMs: 3037, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 120 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.120",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 120", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-120", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 120", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2480, label: "Settle" },
          { tMs: 3060, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 121 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.121",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 121", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-121", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 121", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2499, label: "Settle" },
          { tMs: 3083, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 122 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.122",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 122", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-122", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 122", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2518, label: "Settle" },
          { tMs: 3106, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 123 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.123",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 123", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-123", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 123", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2537, label: "Settle" },
          { tMs: 3129, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 124 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.124",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 124", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-124", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 124", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2556, label: "Settle" },
          { tMs: 3152, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 125 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.125",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 125", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-125", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 125", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2575, label: "Settle" },
          { tMs: 3175, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 126 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.126",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 126", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-126", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 126", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2594, label: "Settle" },
          { tMs: 3198, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 127 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.127",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 127", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-127", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 127", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2613, label: "Settle" },
          { tMs: 3221, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 128 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.128",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 128", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-128", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 128", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2632, label: "Settle" },
          { tMs: 3244, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 129 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.129",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 129", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-129", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 129", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2651, label: "Settle" },
          { tMs: 3267, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 130 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.130",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 130", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-130", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 130", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2670, label: "Settle" },
          { tMs: 3290, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 131 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.131",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 131", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-131", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 131", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 2689, label: "Settle" },
          { tMs: 313, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 132 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.132",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 132", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-132", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 132", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 208, label: "Settle" },
          { tMs: 336, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 133 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.133",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 133", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-133", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 133", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 227, label: "Settle" },
          { tMs: 359, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 134 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.134",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 134", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-134", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 134", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 246, label: "Settle" },
          { tMs: 382, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 135 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.135",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 135", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-135", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 135", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 265, label: "Settle" },
          { tMs: 405, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 136 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.136",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 136", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-136", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 136", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 284, label: "Settle" },
          { tMs: 428, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 137 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.137",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 137", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-137", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 137", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 303, label: "Settle" },
          { tMs: 451, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 138 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.138",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 138", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-138", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 138", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 322, label: "Settle" },
          { tMs: 474, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 139 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.139",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 139", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-139", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 139", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 341, label: "Settle" },
          { tMs: 497, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 140 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.140",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 140", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-140", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 140", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 360, label: "Settle" },
          { tMs: 520, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 141 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.141",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 141", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-141", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 141", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 379, label: "Settle" },
          { tMs: 543, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 142 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.142",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 142", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-142", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 142", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 398, label: "Settle" },
          { tMs: 566, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 143 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.143",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 143", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-143", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 143", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 417, label: "Settle" },
          { tMs: 589, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 144 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.144",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 144", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-144", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 144", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 436, label: "Settle" },
          { tMs: 612, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 145 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.145",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 145", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-145", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 145", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 455, label: "Settle" },
          { tMs: 635, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 146 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.146",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 146", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-146", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 146", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 474, label: "Settle" },
          { tMs: 658, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 147 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.147",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 147", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-147", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 147", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 493, label: "Settle" },
          { tMs: 681, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 148 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.148",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 148", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-148", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 148", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 512, label: "Settle" },
          { tMs: 704, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 149 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.149",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 149", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-149", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 149", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 531, label: "Settle" },
          { tMs: 727, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 150 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.150",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 150", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-150", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 150", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 550, label: "Settle" },
          { tMs: 750, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 151 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.151",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 151", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-151", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 151", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 569, label: "Settle" },
          { tMs: 773, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 152 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.152",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.80, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 152", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-152", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 152", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 588, label: "Settle" },
          { tMs: 796, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 153 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.153",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.00, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 153", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-153", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 153", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 607, label: "Settle" },
          { tMs: 819, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 154 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.154",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.10, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 154", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-154", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.00, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 154", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 626, label: "Settle" },
          { tMs: 842, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 155 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.155",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.20, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 155", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-155", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.03, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 155", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 645, label: "Settle" },
          { tMs: 865, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 156 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.156",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.30, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 156", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-156", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.06, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 156", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 664, label: "Settle" },
          { tMs: 888, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 157 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.157",
      timelineDSL: {
        tracks: ["motion", "camera", "overlay", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.40, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 157", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-157", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.09, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 157", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 683, label: "Settle" },
          { tMs: 911, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 8 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 158 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.158",
      timelineDSL: {
        tracks: ["overlay", "layers", "camera", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.50, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 158", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-158", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.12, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 158", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 702, label: "Settle" },
          { tMs: 934, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 9 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 159 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.159",
      timelineDSL: {
        tracks: ["layers", "camera", "overlay", "motion"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.60, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 159", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-159", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.15, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 159", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 721, label: "Settle" },
          { tMs: 957, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 10 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("sequence variant 160 canonical hash invariant", () => {
    const sequence = createSequence({
      sequenceId: "sequence.mass.160",
      timelineDSL: {
        tracks: ["camera", "overlay", "motion", "layers"],
        keyframes: [
          { tMs: 0, track: "camera", key: "zoom", value: 1.70, easing: "linear" },
          { tMs: 600, track: "overlay", key: "headline", value: "Headline 160", easing: "easeOut" },
          { tMs: 1200, track: "motion", key: "heroEntrance", value: "entry-160", easing: "easeIn" },
          { tMs: 1800, track: "layers", key: "intensity", value: 0.9, easing: "linear" },
          { tMs: 2400, track: "camera", key: "panX", value: 0.18, easing: "easeInOut" },
          { tMs: 3000, track: "motion", key: "parallax", value: 0.8, easing: "linear" },
          { tMs: 3600, track: "overlay", key: "cta", value: "CTA 160", easing: "easeInOut" }
        ],
        markers: [
          { tMs: 0, label: "Reveal" },
          { tMs: 740, label: "Settle" },
          { tMs: 980, label: "CTA" }
        ]
      },
      rules: {
        ...createSequence().rules,
        motionBudget: { maxHeroMotions: 2, maxTrackKeyframes: 7 }
      }
    });
    const canonical = canonicalizeSequence(sequence);
    const serialized = serializeSequence(canonical);
    const reparsed = deserializeSequence(serialized);
    const validation = validateSequence(reparsed);
    expect(validation.ok).toBe(true);
    expect(hashSequence(canonical)).toBe(hashSequence(reparsed));
  });

  it("capability variant 001 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 002 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 003 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 004 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 005 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 006 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 007 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 008 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 009 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 010 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 011 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 012 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 013 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 014 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 015 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 016 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 017 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 018 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 019 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 020 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 021 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 022 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 023 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 024 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 025 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 026 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 027 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 028 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 029 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 030 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 031 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 032 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 033 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 034 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 035 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 036 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 037 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 038 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 039 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 040 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 041 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 042 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 043 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 044 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 045 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 046 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 047 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 048 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 049 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 050 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 051 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 052 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 053 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 054 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 055 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 056 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 057 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 058 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 059 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 060 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 061 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 062 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 063 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 064 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 065 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 066 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 067 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 068 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 069 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 070 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 071 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 072 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 073 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 074 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 075 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 076 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 077 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "full" },
      env: { PITCH_CAP_DIRECTOR: "lite" },
      query: { capDirector: "full" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("lite");
    expect(result.applied).toBe("lite");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 078 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "debug" },
      env: { PITCH_CAP_DIRECTOR: "full" },
      query: { capDirector: "lite" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("full");
    expect(result.applied).toBe("full");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 079 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "off" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "off" },
      nodeEnv: "development"
    });
    expect(result.requested).toBe("debug");
    expect(result.applied).toBe("debug");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

  it("capability variant 080 priority + gate invariant", () => {
    const result = resolveDirectorCapability({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "off" },
      query: { capDirector: "debug" },
      nodeEnv: "production"
    });
    expect(result.requested).toBe("off");
    expect(result.applied).toBe("off");
    expect(result.auditTrail).toHaveLength(4);
    expect(result.auditTrail[0]?.source).toBe("env");
  });

});
