import { defineConfig } from "@playwright/test";

const BASE_URL = process.env["UI_IMPROVEMENT_BASE_URL"] ?? "http://127.0.0.1:3100";
const USE_EXTERNAL_BASE_URL = Boolean(process.env["UI_IMPROVEMENT_BASE_URL"]);
const SERVER_MODE = process.env["UI_IMPROVEMENT_SERVER_MODE"] === "dev" ? "dev" : "prod";

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
    },
    {
      name: "keystone-layer-system",
      testMatch: /layer-system-validation\.spec\.ts/
    }
  ],
  ...(!USE_EXTERNAL_BASE_URL
    ? {
        webServer: {
          command: SERVER_MODE === "dev" ? "pnpm run dev" : "pnpm run build && pnpm run start",
          url: BASE_URL,
          timeout: 300_000,
          reuseExistingServer: true,
          stdout: "pipe",
          stderr: "pipe"
        }
      }
    : {})
});
