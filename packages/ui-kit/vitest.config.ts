import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
    exclude: [
      "tests/layers/layerIds.contract.test.ts",
      "tests/layers/layersCss.budget.test.ts",
      "tests/layers/resolveLayerFlags.allowlist.exhaustive.test.ts",
      "tests/layers/resolveLayerFlags.perf-budget.test.ts",
      "tests/layers/resolveLayerFlags.precedence.test.ts"
    ],
    environment: "node",
    globals: true
  }
});
