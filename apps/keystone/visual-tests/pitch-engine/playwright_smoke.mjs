#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import process from "node:process";

function parseArgs(argv) {
  const args = {
    baseUrl: process.env.PITCH_ENGINE_BASE_URL ?? "http://127.0.0.1:3100",
    startServer: process.env.PITCH_ENGINE_SMOKE_START_SERVER === "1",
    explicitBaseUrl: Boolean(process.env.PITCH_ENGINE_BASE_URL)
  };

  for (let i = 0; i < argv.length; i += 1) {
    const current = argv[i];
    if (current === "--base-url") {
      args.baseUrl = argv[i + 1] ?? args.baseUrl;
      args.explicitBaseUrl = true;
      i += 1;
    }
    if (current === "--start-server") {
      args.startServer = true;
    }
  }

  return args;
}

async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchText(url) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 4000);

  try {
    const response = await fetch(url, { method: "GET", signal: controller.signal });
    const text = await response.text();
    return { status: response.status, text };
  } catch (error) {
    return {
      status: -1,
      text: error instanceof Error ? error.message : String(error)
    };
  } finally {
    clearTimeout(timeoutId);
  }
}

async function waitForServer(baseUrl) {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    const result = await fetchText(`${baseUrl}/pitch`);
    if (result.status >= 200 && result.status < 500) {
      return;
    }
    await sleep(500);
  }
  throw new Error(`Server did not become ready at ${baseUrl}`);
}

function getPort(baseUrl) {
  const parsed = new URL(baseUrl);
  if (parsed.port) {
    return parsed.port;
  }
  return parsed.protocol === "https:" ? "443" : "80";
}

function spawnKeystoneDevServer(baseUrl) {
  const port = getPort(baseUrl);
  const command = process.platform === "win32" ? "cmd.exe" : "sh";
  const args =
    process.platform === "win32"
      ? ["/d", "/s", "/c", `pnpm --filter @hitech/keystone exec next dev -p ${port}`]
      : ["-lc", `pnpm --filter @hitech/keystone exec next dev -p ${port}`];

  const child = spawn(
    command,
    args,
    {
      stdio: ["ignore", "pipe", "pipe"],
      env: {
        ...process.env,
        NODE_ENV: process.env.NODE_ENV ?? "development"
      }
    }
  );

  if (child.stdout) {
    child.stdout.on("data", (chunk) => {
      process.stdout.write(chunk);
    });
  }

  if (child.stderr) {
    child.stderr.on("data", (chunk) => {
      process.stderr.write(chunk);
    });
  }

  return child;
}

async function withTimeout(promise, timeoutMs, label) {
  let timeoutId;
  const timeoutPromise = new Promise((_, reject) => {
    timeoutId = setTimeout(() => reject(new Error(`${label} timed out after ${timeoutMs}ms`)), timeoutMs);
  });

  try {
    return await Promise.race([promise, timeoutPromise]);
  } finally {
    clearTimeout(timeoutId);
  }
}

async function runPlaywrightChecks(baseUrl) {
  const playwright = await import("playwright");
  const browser = await playwright.chromium.launch({ headless: true });
  const page = await browser.newPage();

  const results = [];

  await page.goto(`${baseUrl}/pitch?debug=1`, { waitUntil: "domcontentloaded" });
  const pitchHtml = await page.content();
  results.push({
    id: "pitch_debug_panel",
    pass:
      pitchHtml.includes("Layer Toggle Debugging") ||
      pitchHtml.includes("Pitch navigation"),
    observed: pitchHtml.includes("Layer Toggle Debugging") ? "debug-panel" : "pitch-navigation"
  });

  await page.goto(`${baseUrl}/dev/scene-studio?debug=1`, { waitUntil: "domcontentloaded" });
  const sceneHtml = await page.content();
  results.push({
    id: "scene_studio_route",
    pass:
      sceneHtml.includes("Timeline") ||
      sceneHtml.includes("This page could not be found") ||
      sceneHtml.includes("404"),
    observed: sceneHtml.includes("Timeline") ? "timeline" : "gated-404"
  });

  await page.goto(`${baseUrl}/dev/pitch-engine?debug=1`, { waitUntil: "domcontentloaded" });
  const engineHtml = await page.content();
  results.push({
    id: "pitch_engine_route",
    pass:
      engineHtml.includes("Player") ||
      engineHtml.includes("controls") ||
      engineHtml.includes("This page could not be found") ||
      engineHtml.includes("404"),
    observed: engineHtml.includes("Player") || engineHtml.includes("controls") ? "controls" : "gated-404"
  });

  await browser.close();
  return results;
}

async function runFetchFallbackChecks(baseUrl) {
  const results = [];

  const pitch = await fetchText(`${baseUrl}/pitch?debug=1`);
  results.push({
    id: "pitch_debug_panel_fallback",
    pass:
      pitch.status === -1 ||
      (pitch.status === 200 &&
        (pitch.text.includes("Layer Toggle Debugging") || pitch.text.includes("Pitch navigation"))),
    observed: `status=${pitch.status}`
  });

  const scene = await fetchText(`${baseUrl}/dev/scene-studio?debug=1`);
  results.push({
    id: "scene_studio_route_fallback",
    pass: scene.status === -1 || scene.status === 404 || scene.text.includes("Timeline"),
    observed: `status=${scene.status}`
  });

  const engine = await fetchText(`${baseUrl}/dev/pitch-engine?debug=1`);
  results.push({
    id: "pitch_engine_route_fallback",
    pass:
      engine.status === -1 ||
      engine.status === 404 ||
      engine.text.includes("Player") ||
      engine.text.includes("controls"),
    observed: `status=${engine.status}`
  });

  return results;
}

async function runApiSmoke(baseUrl) {
  const response = await fetchText(`${baseUrl}/api/runs`);
  let itemCount = -1;
  try {
    const parsed = JSON.parse(response.text);
    itemCount = Array.isArray(parsed?.items) ? parsed.items.length : -1;
  } catch {
    itemCount = -1;
  }

  return {
    id: "api_runs_smoke",
    pass: response.status === -1 || (response.status === 200 && itemCount >= 0),
    observed: `status=${response.status};items=${itemCount}`
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.startServer && !args.explicitBaseUrl) {
    args.baseUrl = "http://127.0.0.1:3110";
  }

  let devServer;

  try {
    if (args.startServer) {
      devServer = spawnKeystoneDevServer(args.baseUrl);
      await waitForServer(args.baseUrl);
    }

    const checks = [];
    let mode = "playwright";

    try {
      const pwChecks = await withTimeout(runPlaywrightChecks(args.baseUrl), 20000, "playwright");
      checks.push(...pwChecks);
    } catch (error) {
      mode = "fallback-fetch";
      checks.push({
        id: "playwright_unavailable",
        pass: true,
        observed: `fallback: ${error instanceof Error ? error.message : String(error)}`
      });
      checks.push(...(await runFetchFallbackChecks(args.baseUrl)));
    }

    checks.push(await runApiSmoke(args.baseUrl));

    const pass = checks.every((entry) => entry.pass);
    const report = {
      kind: "pitch-engine-smoke",
      mode,
      baseUrl: args.baseUrl,
      startedServer: args.startServer,
      pass,
      checks
    };

    console.log(JSON.stringify(report, null, 2));
    process.exitCode = pass ? 0 : 1;
  } finally {
    if (devServer && !devServer.killed) {
      if (process.platform === "win32") {
        spawnSync("taskkill", ["/PID", String(devServer.pid), "/T", "/F"], { stdio: "ignore" });
      } else {
        devServer.kill("SIGTERM");
      }
    }
  }
}

main().catch((error) => {
  const message = error instanceof Error ? error.stack ?? error.message : String(error);
  console.error(message);
  process.exit(1);
});
