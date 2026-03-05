import { resolveMotionDataAttrs, resolveMotionGate, type ReducedMotionInput } from "./reducedMotion.js";
import { MOTION_LIMITS, MOTION_EASINGS, toMs } from "./tokens.js";

export interface MotionPrimitive {
  readonly className: string;
  readonly attrs: Record<string, string>;
  readonly style: Record<string, string>;
}

export interface MotionPrimitiveOptions extends ReducedMotionInput {
  readonly heroAlreadyPlayed?: boolean;
}

function makeBaseAttrs(
  gate: ReturnType<typeof resolveMotionGate>,
  primitive: string
): Record<string, string> {
  return {
    ...resolveMotionDataAttrs(gate),
    "data-ui-motion-primitive": primitive
  };
}

export function hoverLift(options: MotionPrimitiveOptions = {}): MotionPrimitive {
  const gate = resolveMotionGate(options);
  const distance = gate.allowAnimation
    ? gate.profile === "perf"
      ? MOTION_LIMITS.hoverLiftPerfPx
      : MOTION_LIMITS.hoverLiftPx
    : 0;

  return {
    className: "ui-motion-hover-lift",
    attrs: makeBaseAttrs(gate, "hover-lift"),
    style: {
      "--ui-motion-hover-distance": `${distance}px`,
      transitionProperty: "transform, box-shadow",
      transitionDuration: gate.allowAnimation ? toMs(gate.tokens.micro.durationMs) : "0ms",
      transitionTimingFunction: gate.tokens.micro.easing,
      willChange: gate.allowAnimation ? "transform" : "auto"
    }
  };
}

export function sheenMicro(options: MotionPrimitiveOptions = {}): MotionPrimitive {
  const gate = resolveMotionGate(options);
  const run = gate.allowAnimation;

  return {
    className: "ui-motion-sheen-micro",
    attrs: makeBaseAttrs(gate, "sheen-micro"),
    style: {
      backgroundImage:
        "linear-gradient(132deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.18) 42%, rgba(255,255,255,0.06) 55%, rgba(255,255,255,0) 78%)",
      backgroundSize: "220% 220%",
      backgroundPosition: "180% 50%",
      animationName: run ? "ui-motion-sheen-micro" : "none",
      animationDuration: run ? toMs(gate.tokens.base.durationMs) : "0ms",
      animationTimingFunction: MOTION_EASINGS.settle,
      animationFillMode: "both",
      animationIterationCount: "1"
    }
  };
}

export function pressedInset(options: MotionPrimitiveOptions = {}): MotionPrimitive {
  const gate = resolveMotionGate(options);

  return {
    className: "ui-motion-pressed-inset",
    attrs: makeBaseAttrs(gate, "pressed-inset"),
    style: {
      transform: "translateY(0)",
      boxShadow: "inset 0 1px 0 rgba(255,255,255,0.18), inset 0 -2px 4px rgba(0,0,0,0.26)",
      transitionProperty: "transform, box-shadow",
      transitionDuration: gate.allowAnimation ? toMs(gate.tokens.micro.durationMs) : "0ms",
      transitionTimingFunction: gate.tokens.micro.easing
    }
  };
}

export function enterFadeUp(options: MotionPrimitiveOptions = {}): MotionPrimitive {
  const gate = resolveMotionGate(options);
  const distance = gate.allowAnimation
    ? gate.profile === "perf"
      ? MOTION_LIMITS.enterFadeUpPerfPx
      : MOTION_LIMITS.enterFadeUpPx
    : 0;

  return {
    className: "ui-motion-enter-fade-up",
    attrs: makeBaseAttrs(gate, "enter-fade-up"),
    style: {
      "--ui-motion-enter-distance": `${distance}px`,
      animationName: gate.allowAnimation ? "ui-motion-enter-fade-up" : "none",
      animationDuration: gate.allowAnimation ? toMs(gate.tokens.micro.durationMs) : "0ms",
      animationTimingFunction: gate.tokens.micro.easing,
      animationFillMode: "both"
    }
  };
}

export function heroSweep(options: MotionPrimitiveOptions = {}): MotionPrimitive {
  const gate = resolveMotionGate(options);
  const runHero = gate.allowHero && !options.heroAlreadyPlayed;

  return {
    className: "ui-motion-hero-sweep",
    attrs: {
      ...makeBaseAttrs(gate, "hero-sweep"),
      "data-ui-hero-policy": "single-per-screen",
      "data-ui-hero-sweep": runHero ? "run" : "skip"
    },
    style: {
      "--ui-motion-hero-travel": `${MOTION_LIMITS.heroSweepTravelPercent}%`,
      backgroundSize: `${MOTION_LIMITS.heroSweepTravelPercent}% 100%`,
      animationName: runHero ? "ui-motion-hero-sweep" : "none",
      animationDuration: runHero ? toMs(gate.tokens.hero.durationMs) : "0ms",
      animationTimingFunction: gate.tokens.hero.easing,
      animationFillMode: "both",
      animationIterationCount: "1"
    }
  };
}

export function skeletonShimmer(options: MotionPrimitiveOptions = {}): MotionPrimitive {
  const gate = resolveMotionGate(options);
  const run = gate.allowShimmer;

  return {
    className: "ui-motion-skeleton-shimmer",
    attrs: {
      ...makeBaseAttrs(gate, "skeleton-shimmer"),
      "data-ui-shimmer": run ? "on" : "off"
    },
    style: {
      "--ui-motion-skeleton-travel": `${MOTION_LIMITS.skeletonShimmerTravelPercent}%`,
      backgroundImage:
        "linear-gradient(98deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.08) 42%, rgba(255,255,255,0.22) 50%, rgba(255,255,255,0.08) 58%, rgba(255,255,255,0) 100%)",
      backgroundSize: `${MOTION_LIMITS.skeletonShimmerTravelPercent}% 100%`,
      animationName: run ? "ui-motion-skeleton-shimmer" : "none",
      animationDuration: run ? toMs(gate.tokens.base.durationMs * 4) : "0ms",
      animationTimingFunction: "linear",
      animationIterationCount: run ? "infinite" : "1"
    }
  };
}
