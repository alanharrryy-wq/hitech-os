import { applyLuxuryMaterial } from "./applyLuxuryMaterial.js";
import { applyLuxuryStyle } from "./applyLuxuryStyle.js";
import {
  ACCENT_SCENARIOS,
  SEMANTIC_INTENT_MATRIX,
  STYLE_SCENARIOS
} from "./fixtures.js";
import {
  createBudgetSnapshot,
  evaluateGovernanceBudget,
  governanceWarnings,
  mergeSnapshots
} from "./governancePolicy.js";
import { resolveMaterialRuntime } from "./materials/materialEngine.js";
import {
  enforceAccentBudget,
  resolveSemanticAccent
} from "./semantics/semanticMap.js";
import { getLuxuryTokens } from "./tokens/index.js";
import type { StyleId } from "./types.js";

interface SelfTestResult {
  readonly passed: number;
  readonly failed: number;
  readonly failures: readonly string[];
}

type TestFn = () => void;

function assert(condition: boolean, message: string): void {
  if (!condition) {
    throw new Error(message);
  }
}

function assertEquals(actual: string | number | boolean, expected: string | number | boolean, message: string): void {
  if (actual !== expected) {
    throw new Error(`${message} | expected=${String(expected)} actual=${String(actual)}`);
  }
}

function runNamedTests(cases: readonly [string, TestFn][]): SelfTestResult {
  const failures: string[] = [];
  let passed = 0;

  for (const [name, run] of cases) {
    try {
      run();
      passed += 1;
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      failures.push(`${name}: ${detail}`);
    }
  }

  return {
    passed,
    failed: failures.length,
    failures
  };
}

const styleIds: readonly StyleId[] = ["LIQUID_GLASS", "GOLD_NOIR_TERMINAL", "GRAPHITE_PRISM_ISO"];
const defaultAccentUsage = ACCENT_SCENARIOS[0] ?? {
  screenAccents: ["neutral"] as const,
  chartAccents: ["neutral"] as const
};

function createSemanticTests(): readonly [string, TestFn][] {
  const cases: [string, TestFn][] = [];

  for (const styleId of styleIds) {
    for (const intent of SEMANTIC_INTENT_MATRIX) {
      cases.push([
        `semantic:${styleId}:${intent}:surface`,
        () => {
          const accent = resolveSemanticAccent(styleId, intent, "surface");
          assert(Boolean(accent.color), "surface accent color must be present");
          if (styleId === "GRAPHITE_PRISM_ISO") {
            assert(accent.gradient === undefined, "Graphite gradient must not be assigned to surface target");
          }
        }
      ]);

      cases.push([
        `semantic:${styleId}:${intent}:chart`,
        () => {
          const accent = resolveSemanticAccent(styleId, intent, "chartStroke");
          if (styleId === "GRAPHITE_PRISM_ISO") {
            assert(Boolean(accent.gradient), "Graphite chart accent must include data gradient");
            assertEquals(accent.gradient?.scope ?? "", "chart-data-only", "Graphite gradient scope must be chart-data-only");
          } else {
            assert(accent.gradient === undefined, "Non-graphite styles must not emit chart gradients");
          }
        }
      ]);
    }
  }

  return cases;
}

function createAccentBudgetTests(): readonly [string, TestFn][] {
  const cases: [string, TestFn][] = [];

  for (const usage of ACCENT_SCENARIOS) {
    cases.push([
      `accent-budget:screen:${usage.screenAccents.join("-")}`,
      () => {
        const budget = enforceAccentBudget(usage.screenAccents, "screen");
        assert(budget.selected.length <= 3, "screen budget must cap at 3 accents");
      }
    ]);

    cases.push([
      `accent-budget:chart:${usage.chartAccents.join("-")}`,
      () => {
        const budget = enforceAccentBudget(usage.chartAccents, "chart");
        assert(budget.selected.length <= 4, "chart budget must cap at 4 accents");
      }
    ]);
  }

  return cases;
}

function createMaterialRuntimeTests(): readonly [string, TestFn][] {
  const cases: [string, TestFn][] = [];

  for (const scenario of STYLE_SCENARIOS) {
    cases.push([
      `material-runtime:${scenario.styleId}:${scenario.surfaceId}:${scenario.perfProfile}`,
      () => {
        const styled = applyLuxuryStyle({
          styleId: scenario.styleId,
          surfaceId: scenario.surfaceId,
          perfProfile: scenario.perfProfile,
          motionLevel: scenario.motionLevel,
          accentUsage: defaultAccentUsage,
          blurSupported: true
        });

        assert(Boolean(styled.materialId), "material id should resolve");
        assert(Boolean(styled.cssVars["--lux-surface-bg"]), "surface background var should exist");
        assert(styled.surfaceAccents.length <= 3, "surface accents should be budget-safe");

        const fallbackRuntime = resolveMaterialRuntime(styled.materialId, "default", false);
        assertEquals(fallbackRuntime.flags.blurMode, "fallback", "fallback runtime must disable blur mode");
      }
    ]);
  }

  return cases;
}

function createGovernanceTests(): readonly [string, TestFn][] {
  const cases: [string, TestFn][] = [];

  for (const styleId of styleIds) {
    cases.push([
      `governance:budget:${styleId}:ok`,
      () => {
        const tokens = getLuxuryTokens(styleId);
        const snapshot = createBudgetSnapshot({
          motionLevel: "micro",
          surfaceAccents: ["deal", "risk"],
          chartAccents: ["deal", "cash"],
          glowAlpha: tokens.glowBudget.maxAlpha,
          glowBlurPx: tokens.glowBudget.maxBlurPx,
          glowLayers: tokens.glowBudget.maxLayersPerSurface,
          goldCoverageRatio: tokens.goldUsage.maxCoverageRatio,
          goldAccentCount: tokens.goldUsage.maxAccentsPerSurface
        });

        const report = evaluateGovernanceBudget(styleId, tokens, snapshot);
        assertEquals(report.status, "OK", "governance report should remain OK on hard bounds");
      }
    ]);

    cases.push([
      `governance:budget:${styleId}:warn`,
      () => {
        const tokens = getLuxuryTokens(styleId);
        const over = createBudgetSnapshot({
          motionLevel: "hero",
          surfaceAccents: ["deal", "cash", "evidence", "risk"],
          chartAccents: ["deal", "cash", "evidence", "outcome", "risk"],
          glowAlpha: tokens.glowBudget.maxAlpha + 0.01,
          glowBlurPx: tokens.glowBudget.maxBlurPx + 1,
          glowLayers: tokens.glowBudget.maxLayersPerSurface + 1,
          goldCoverageRatio: tokens.goldUsage.maxCoverageRatio + 0.01,
          goldAccentCount: tokens.goldUsage.maxAccentsPerSurface + 1
        });

        const report = evaluateGovernanceBudget(styleId, tokens, over);
        assertEquals(report.status, "WARN", "governance report should warn on overflow");
        assert(governanceWarnings(report).length >= 1, "overflow report should emit warnings");
      }
    ]);
  }

  cases.push([
    "governance:merge-snapshots",
    () => {
      const left = createBudgetSnapshot({
        motionLevel: "micro",
        surfaceAccents: ["deal"],
        chartAccents: ["deal"],
        glowAlpha: 0.02,
        glowBlurPx: 4,
        glowLayers: 1,
        goldCoverageRatio: 0,
        goldAccentCount: 0
      });
      const right = createBudgetSnapshot({
        motionLevel: "hero",
        surfaceAccents: ["cash", "risk"],
        chartAccents: ["cash", "risk"],
        glowAlpha: 0.08,
        glowBlurPx: 10,
        glowLayers: 1,
        goldCoverageRatio: 0.04,
        goldAccentCount: 1
      });

      const merged = mergeSnapshots(left, right);
      assertEquals(merged.heroMotionCount, 1, "merged hero motion count should sum to 1");
      assertEquals(merged.screenAccentCount, 3, "merged screen accent count should sum");
      assertEquals(merged.glowBlurPx, 10, "merged glow blur should keep max value");
    }
  ]);

  return cases;
}

function createApplyStyleMatrixTests(): readonly [string, TestFn][] {
  const cases: [string, TestFn][] = [];

  for (const scenario of STYLE_SCENARIOS) {
    for (const usage of ACCENT_SCENARIOS) {
      cases.push([
        `apply-style:${scenario.styleId}:${scenario.surfaceId}:${usage.screenAccents.length}:${usage.chartAccents.length}`,
        () => {
          const style = applyLuxuryStyle({
            styleId: scenario.styleId,
            surfaceId: scenario.surfaceId,
            perfProfile: scenario.perfProfile,
            motionLevel: scenario.motionLevel,
            accentUsage: usage,
            blurSupported: scenario.perfProfile !== "perf"
          });

          assert(Boolean(style.dataAttributes["data-lux-style"]), "style attribute should be present");
          assert(Boolean(style.dataAttributes["data-lux-surface"]), "surface attribute should be present");
          assert(style.surfaceAccents.length <= 3, "surface accent list should remain budget-safe");
          assert(style.chartAccents.length <= 4, "chart accent list should remain budget-safe");
          assert(style.warnings.length >= 0, "warnings should be enumerable");

          if (scenario.perfProfile === "perf") {
            assertEquals(style.material.runtimeFlags.blurEnabled, false, "perf profile should disable blur");
          }
        }
      ]);
    }
  }

  return cases;
}

function createApplyMaterialTests(): readonly [string, TestFn][] {
  return [
    [
      "apply-material:glass-default",
      () => {
        const result = applyLuxuryMaterial({
          materialId: "glass/card",
          perfProfile: "default",
          blurSupported: true
        });
        assertEquals(result.dataAttributes["data-lux-material"] ?? "", "glass/card", "material id attribute should match input");
        assert(Boolean(result.cssVars["--lux-surface-bg"]), "surface bg var must be present");
      }
    ],
    [
      "apply-material:glass-fallback",
      () => {
        const result = applyLuxuryMaterial({
          materialId: "glass/card",
          perfProfile: "default",
          blurSupported: false
        });
        assertEquals(result.runtimeFlags.blurMode, "fallback", "unsupported blur must switch to fallback mode");
      }
    ],
    [
      "apply-material:ink-perf",
      () => {
        const result = applyLuxuryMaterial({
          materialId: "ink/drawer",
          perfProfile: "perf"
        });
        assertEquals(result.runtimeFlags.specularEnabled, false, "perf profile should disable specular highlights");
        assert(result.safeguards.includes("perf-profile-disables-expensive-effects"), "perf safeguard should be reported");
      }
    ]
  ];
}

function runAllLuxuryKernelTests(): SelfTestResult {
  const cases: [string, TestFn][] = [
    ...createSemanticTests(),
    ...createAccentBudgetTests(),
    ...createMaterialRuntimeTests(),
    ...createGovernanceTests(),
    ...createApplyStyleMatrixTests(),
    ...createApplyMaterialTests()
  ];

  return runNamedTests(cases);
}

export const luxuryKernelSelfTestReport: SelfTestResult = runAllLuxuryKernelTests();
