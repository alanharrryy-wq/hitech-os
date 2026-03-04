import type { BrowserContextOptions, Page, ViewportSize } from "@playwright/test";
import type { VisualSceneDefinition } from "./scene-manifest.js";

export const VIEWPORT_PRESETS: Readonly<Record<"desktop" | "mobile" | "tablet", ViewportSize>> = {
  desktop: { width: 1440, height: 900 },
  mobile: { width: 390, height: 844 },
  tablet: { width: 1024, height: 1366 }
};

const DETERMINISTIC_STYLE = `
*, *::before, *::after {
  animation: none !important;
  transition: none !important;
  caret-color: transparent !important;
  scroll-behavior: auto !important;
}
html {
  text-rendering: geometricPrecision;
  -webkit-font-smoothing: antialiased;
}
`;

function resolveViewport(scene: Pick<VisualSceneDefinition, "viewport" | "viewportWidth" | "viewportHeight">): ViewportSize {
  if (scene.viewport === "custom") {
    return {
      width: scene.viewportWidth ?? 1440,
      height: scene.viewportHeight ?? 900
    };
  }

  if (scene.viewport === "tablet") {
    return VIEWPORT_PRESETS.tablet;
  }

  return scene.viewport === "mobile" ? VIEWPORT_PRESETS.mobile : VIEWPORT_PRESETS.desktop;
}

export function createDeterministicContextOptions(scene: Pick<VisualSceneDefinition, "viewport" | "viewportWidth" | "viewportHeight">): BrowserContextOptions {
  const viewport = resolveViewport(scene);

  return {
    viewport,
    colorScheme: "light",
    locale: "en-US",
    timezoneId: "UTC",
    reducedMotion: "reduce",
    isMobile: scene.viewport === "mobile",
    hasTouch: scene.viewport === "mobile",
    deviceScaleFactor: 1
  };
}

export async function prepareDeterministicPage(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const fixedNow = 1_730_000_000_000;

    Date.now = () => fixedNow;
    Math.random = () => 0.123456789;

    if (typeof performance !== "undefined") {
      const fixedPerformanceNow = () => 42;
      try {
        Object.defineProperty(performance, "now", {
          configurable: true,
          value: fixedPerformanceNow
        });
      } catch {
        // Ignore if runtime does not allow redefining performance.now.
      }
    }
  });
}

export async function waitForDeterministicReady(page: Page): Promise<void> {
  await page.waitForLoadState("networkidle");
  await page.waitForFunction(() => document.readyState === "complete");

  await page.addStyleTag({ content: DETERMINISTIC_STYLE });

  await page.waitForFunction(
    () => document.documentElement.getAttribute("data-scene-ready") === "1",
    undefined,
    { timeout: 15_000 }
  );

  await page.evaluate(async () => {
    const fonts = (document as Document & { fonts?: FontFaceSet }).fonts;
    if (fonts?.ready) {
      await fonts.ready;
    }
  });

  await page.waitForTimeout(80);
}
