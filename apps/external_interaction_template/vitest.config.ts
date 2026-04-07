import { defineConfig } from "vitest/config";
import path from "path";
import { fileURLToPath } from "url";

const rootDir = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  resolve: {
    alias: {
      "@": path.join(rootDir, "src"),
      "@components": path.join(rootDir, "components")
    }
  },
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts"]
  }
});
