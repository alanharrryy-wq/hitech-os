import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { createHydrationConsoleGuard, type HydrationConsoleGuard } from "./hydration-console-guard";

interface VisualScene {
  readonly id: string;
  readonly route: string;
}

const SCENES: readonly VisualScene[] = [
  {
    id: "pitch-index",
    route: "/pitch?layers=none"
  },
  {
    id: "double-engine-debug-query",
    route: "/pitch/01-double-engine?layers=none&debug=1"
  },
  {
    id: "industrial-flow",
    route: "/pitch/02-industrial-flow?layers=none"
  },
  {
    id: "hitech-os",
    route: "/pitch/03-hitech-os?layers=none"
  },
  {
    id: "valuation",
    route: "/pitch/04-valuation?layers=none"
  }
];

function hashBuffer(buffer: Buffer): string {
  return createHash("sha256").update(buffer).digest("hex");
}

let hydrationGuard: HydrationConsoleGuard;

test.describe("UI Improvement Validation @smoke", () => {
  test.describe.configure({ mode: "serial" });

  test.beforeEach(async ({ page }) => {
    hydrationGuard = createHydrationConsoleGuard(page);

    await page.addInitScript(() => {
      const fixedNow = 1_730_000_000_000;
      Date.now = () => fixedNow;
      Math.random = () => 0.123456789;

      document.addEventListener("DOMContentLoaded", () => {
        const style = document.createElement("style");
        style.setAttribute("data-ui-improvement-deterministic", "1");
        style.textContent = [
          "*{animation:none !important;transition:none !important;}",
          "*::before,*::after{animation:none !important;transition:none !important;}",
          "html{scroll-behavior:auto !important;}"
        ].join("");
        document.head.appendChild(style);
      });
    });
  });

  test.afterEach(async ({ page }, testInfo) => {
    try {
      await hydrationGuard.assertDebugOverlayGating({
        markerSelector: "[data-pitch-debug-overlay='1']",
        requirePresentWhenEnabled: false
      });

      await hydrationGuard.assertNoHydrationWarningsOrErrors(testInfo);
    } finally {
      await hydrationGuard.logFailureDiagnostics(testInfo);
      hydrationGuard.dispose();
    }
  });

  for (const scene of SCENES) {
    test(`scene:${scene.id} @smoke`, async ({ page }) => {
      await page.goto(scene.route, { waitUntil: "networkidle" });
      await expect(page.locator("[data-pitch-shell='1']")).toBeVisible();

      await page.waitForTimeout(120);
      const firstCapture = await page.screenshot({
        fullPage: true,
        animations: "disabled"
      });

      await page.waitForTimeout(120);
      const secondCapture = await page.screenshot({
        fullPage: true,
        animations: "disabled"
      });

      expect(hashBuffer(secondCapture), `Snapshot drift detected for route ${scene.route}.`).toBe(
        hashBuffer(firstCapture)
      );
    });
  }
});
