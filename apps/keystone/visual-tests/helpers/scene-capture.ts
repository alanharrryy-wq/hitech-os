import { mkdir } from "node:fs/promises";
import path from "node:path";
import type { Browser } from "@playwright/test";
import {
  createDeterministicContextOptions,
  prepareDeterministicPage,
  waitForDeterministicReady
} from "./deterministic.js";
import { buildScenePath, type VisualSceneDefinition } from "./scene-manifest.js";

export interface CaptureSceneInput {
  readonly browser: Browser;
  readonly scene: VisualSceneDefinition;
  readonly baseUrl: string;
  readonly outputPath: string;
}

export interface CapturedConsoleMessage {
  readonly type: string;
  readonly text: string;
}

export interface CapturedNetworkRequest {
  readonly method: string;
  readonly url: string;
  readonly status?: number;
}

export interface CaptureSceneOutput {
  readonly sceneUrl: string;
  readonly browserVersion: string;
  readonly consoleMessages: readonly CapturedConsoleMessage[];
  readonly networkRequests: readonly CapturedNetworkRequest[];
}

function buildAbsoluteSceneUrl(baseUrl: string, scenePath: string): string {
  const normalizedBase = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
  return `${normalizedBase}${scenePath}`;
}

export async function captureScene(input: CaptureSceneInput): Promise<CaptureSceneOutput> {
  await mkdir(path.dirname(input.outputPath), { recursive: true });

  const context = await input.browser.newContext(
    createDeterministicContextOptions(input.scene)
  );
  const page = await context.newPage();

  await prepareDeterministicPage(page);

  const consoleMessages: CapturedConsoleMessage[] = [];
  const networkRequests: CapturedNetworkRequest[] = [];

  page.on("console", (message) => {
    consoleMessages.push({
      type: message.type(),
      text: message.text()
    });
  });

  page.on("response", (response) => {
    networkRequests.push({
      method: response.request().method(),
      url: response.url(),
      status: response.status()
    });
  });

  const scenePath = buildScenePath(input.scene);
  const sceneUrl = buildAbsoluteSceneUrl(input.baseUrl, scenePath);

  await page.goto(sceneUrl, { waitUntil: "networkidle" });
  await waitForDeterministicReady(page);

  await page.screenshot({
    path: input.outputPath,
    fullPage: true,
    animations: "disabled"
  });

  const browserVersion = input.browser.version();
  await context.close();

  return {
    sceneUrl,
    browserVersion,
    consoleMessages,
    networkRequests
  };
}
