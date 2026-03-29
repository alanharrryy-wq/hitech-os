import { expect, test } from "@playwright/test";

const SERVER_MODE = process.env["UI_IMPROVEMENT_SERVER_MODE"] === "dev" ? "dev" : "prod";

test.describe("Layer System Validation", () => {
  test("applies query layers to html root attributes on industrial flow", async ({ page }) => {
    await page.goto(
      "/pitch/02-industrial-flow?layers=stage.haze,stage.vignette&motion=off",
      { waitUntil: "networkidle" }
    );

    await expect
      .poll(async () => {
        return await page.evaluate(() =>
          document.documentElement.getAttribute("data-scene-ready")
        );
      })
      .toBe("1");

    const root = await page.evaluate(() => {
      const html = document.documentElement;
      return {
        haze: html.getAttribute("data-layer-stage-haze"),
        vignette: html.getAttribute("data-layer-stage-vignette"),
        noise: html.getAttribute("data-layer-stage-noise"),
        source: html.getAttribute("data-layer-source"),
        profile: html.getAttribute("data-layer-profile")
      };
    });
    expect(root.haze).toBe("1");
    expect(root.vignette).toBe("1");
    expect(root.noise).toBe(null);
    expect(root.source).toBe("layers");
    expect(root.profile).toBe("neutral");
  });

  test("debug panel shows source/unknown tokens and share URL reproduces state", async ({
    page,
    context
  }) => {
    test.skip(SERVER_MODE !== "dev", "Debug panel is intentionally hidden outside dev server mode.");

    await context.grantPermissions(["clipboard-read", "clipboard-write"], {
      origin: "http://127.0.0.1:3100"
    });

    await page.goto(
      "/pitch/02-industrial-flow?debug=1&layers=stage.haze,stage.vignette,unknown.layer&motion=off",
      { waitUntil: "networkidle" }
    );

    const panel = page.locator('aside[aria-label="Layer Debug Panel"]');
    await expect(panel).toBeVisible();

    await expect(panel).toContainText("source=layers");
    await expect(panel).toContainText("enabled=");
    await expect(panel).toContainText("unknown.layer");

    const hazeToggle = page
      .locator("label", { hasText: "stage.haze" })
      .locator('input[type="checkbox"]');
    if (await hazeToggle.isChecked()) {
      await hazeToggle.uncheck();
    }

    await expect
      .poll(async () => {
        return await page.evaluate(() =>
          document.documentElement.getAttribute("data-layer-stage-haze")
        );
      })
      .toBe(null);

    await page.getByRole("button", { name: "Copy Scene Link" }).click();
    const copiedUrl = await page.evaluate(async () => {
      return await navigator.clipboard.readText();
    });

    expect(copiedUrl).toContain("/pitch/02-industrial-flow");
    expect(copiedUrl).toContain("layers=");
    expect(copiedUrl).not.toContain("unknown.layer");

    const replay = await context.newPage();
    await replay.goto(copiedUrl, { waitUntil: "networkidle" });

    const replayRoot = await replay.evaluate(() => {
      const html = document.documentElement;
      return {
        haze: html.getAttribute("data-layer-stage-haze"),
        vignette: html.getAttribute("data-layer-stage-vignette"),
        noise: html.getAttribute("data-layer-stage-noise"),
        source: html.getAttribute("data-layer-source"),
        profile: html.getAttribute("data-layer-profile")
      };
    });
    expect(replayRoot.haze).toBe(null);
    expect(replayRoot.vignette).toBe("1");
    expect(replayRoot.source).toBe("layers");
    await replay.close();
  });
});
