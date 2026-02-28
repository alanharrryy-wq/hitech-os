import path from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  esbuild: {
    jsx: "automatic",
    jsxImportSource: "react"
  },
  resolve: {
    alias: {
      "@hitech/contracts": path.resolve(__dirname, "../../packages/contracts/src/index.ts"),
      "@hitech/ui-kit": path.resolve(__dirname, "../../packages/ui-kit/src/index.ts"),
      "@hitech/ui-kit/styles.css": path.resolve(__dirname, "../../packages/ui-kit/src/styles.css")
    }
  },
  test: {
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
    environment: "node",
    globals: true
  }
});
