import { defineConfig } from "@playwright/test";

const BASE_URL = process.env["UI_IMPROVEMENT_BASE_URL"] ?? "http://127.0.0.1:3110";
const USE_EXTERNAL_BASE_URL = Boolean(process.env["UI_IMPROVEMENT_BASE_URL"]);
const SERVER_MODE = process.env["UI_IMPROVEMENT_SERVER_MODE"] === "prod" ? "prod" : "dev";

export default defineConfig({
  testDir: "./visual-tests",
  timeout: 180_000,
  expect: {
    timeout: 15_000
  },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["line"]],
  use: {
    baseURL: BASE_URL,
    colorScheme: "light",
    locale: "en-US",
    timezoneId: "UTC",
    trace: "off",
    video: "off",
    screenshot: "off"
  },
  projects: [
    {
      name: "keystone-scenes",
      testMatch: /ui-improvement\.spec\.ts/
    }
  ],
  ...(!USE_EXTERNAL_BASE_URL
    ? {
        webServer: {
          command:
            SERVER_MODE === "dev"
              ? "pnpm exec next dev -p 3110"
              : "pnpm run build && pnpm exec next start -p 3110",
          url: BASE_URL,
          timeout: 300_000,
          reuseExistingServer: false,
          stdout: "pipe",
          stderr: "pipe"
        }
      }
    : {})
});
