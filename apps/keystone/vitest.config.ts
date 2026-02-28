import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.{ts,tsx,mjs,cjs}"],
    environment: "node",
    watch: false,
    globals: false,
    reporters: ["default"]
  }
});
