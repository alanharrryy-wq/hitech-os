const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

function sanitizeMessage(value) {
  let text = String(value || "");
  const replacements = [
    [process.env.USERPROFILE, "<USERPROFILE>"],
    [process.env.LOCALAPPDATA, "<LOCALAPPDATA>"],
    [process.env.PROGRAMFILES, "<PROGRAMFILES>"],
    [process.env["PROGRAMFILES(X86)"], "<PROGRAMFILES_X86>"],
    [process.cwd(), "<CWD>"],
  ].filter(([source]) => Boolean(source));

  for (const [source, replacement] of replacements) {
    text = text.split(source).join(replacement);
  }
  return text;
}

function playwrightCandidates() {
  const mamRoot = process.env.MAM_ROOT || "F:\\repos\\hitech-os\\tools\\Plawright Mamastrophic";
  return [
    {
      label: "MAM_RUNTIME_PLAYWRIGHT",
      modulePath: path.join(mamRoot, ".mam-runtime", "node_modules", "playwright"),
      mamRoot,
    },
    {
      label: "MAM_NODE_MODULES_PLAYWRIGHT",
      modulePath: path.join(mamRoot, "node_modules", "playwright"),
      mamRoot,
    },
    {
      label: "NODE_RESOLUTION_PLAYWRIGHT",
      modulePath: "playwright",
      mamRoot: null,
    },
  ];
}

function findPlaywright() {
  const attempts = [];
  for (const candidate of playwrightCandidates()) {
    try {
      return {
        playwright: require(candidate.modulePath),
        source: candidate.label,
        mamRoot: candidate.mamRoot,
        attempts,
      };
    } catch (error) {
      attempts.push({
        source: candidate.label,
        error: sanitizeMessage(error.message),
      });
    }
  }
  return {
    playwright: null,
    source: null,
    mamRoot: null,
    attempts,
  };
}

function existingExecutable(label, executablePath) {
  if (!executablePath) return null;
  try {
    if (fs.existsSync(executablePath) && fs.statSync(executablePath).isFile()) {
      return { label, executablePath };
    }
  } catch (_) {}
  return null;
}

function browserCacheCandidates(mamRoot) {
  if (!mamRoot) return [];
  const roots = [
    path.join(mamRoot, ".mam-runtime", ".ms-playwright"),
    path.join(mamRoot, ".ms-playwright"),
  ];
  const result = [];

  for (const root of roots) {
    if (!fs.existsSync(root)) continue;
    let entries = [];
    try {
      entries = fs.readdirSync(root, { withFileTypes: true });
    } catch (_) {
      continue;
    }

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const base = path.join(root, entry.name);
      const candidates = [
        ["MAM_CHROMIUM_HEADLESS_SHELL", path.join(base, "chrome-headless-shell-win64", "chrome-headless-shell.exe")],
        ["MAM_CHROMIUM", path.join(base, "chrome-win", "chrome.exe")],
        ["MAM_CHROMIUM_NEW", path.join(base, "chrome-win64", "chrome.exe")],
      ];
      for (const [label, executablePath] of candidates) {
        const found = existingExecutable(label, executablePath);
        if (found) result.push(found);
      }
    }
  }

  return result;
}

function systemBrowserCandidates() {
  const values = [
    ["ENV_PLAYWRIGHT_CHROMIUM_EXECUTABLE", process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE],
    ["CHROME_PROGRAM_FILES", process.env.PROGRAMFILES && path.join(process.env.PROGRAMFILES, "Google", "Chrome", "Application", "chrome.exe")],
    ["CHROME_PROGRAM_FILES_X86", process.env["PROGRAMFILES(X86)"] && path.join(process.env["PROGRAMFILES(X86)"], "Google", "Chrome", "Application", "chrome.exe")],
    ["CHROME_LOCALAPPDATA", process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, "Google", "Chrome", "Application", "chrome.exe")],
    ["EDGE_PROGRAM_FILES", process.env.PROGRAMFILES && path.join(process.env.PROGRAMFILES, "Microsoft", "Edge", "Application", "msedge.exe")],
    ["EDGE_PROGRAM_FILES_X86", process.env["PROGRAMFILES(X86)"] && path.join(process.env["PROGRAMFILES(X86)"], "Microsoft", "Edge", "Application", "msedge.exe")],
    ["EDGE_LOCALAPPDATA", process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, "Microsoft", "Edge", "Application", "msedge.exe")],
  ];

  return values
    .map(([label, executablePath]) => existingExecutable(label, executablePath))
    .filter(Boolean);
}

function uniqueCandidates(candidates) {
  const seen = new Set();
  const result = [];
  for (const candidate of candidates) {
    const key = path.normalize(candidate.executablePath).toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(candidate);
  }
  return result;
}

function resolvedPlaywrightExecutable(playwright) {
  if (!playwright?.chromium?.executablePath) return [];
  try {
    const executablePath = playwright.chromium.executablePath();
    const found = existingExecutable("PLAYWRIGHT_RESOLVED", executablePath);
    return found ? [found] : [];
  } catch (_) {
    return [];
  }
}

async function launchAvailableBrowser(playwrightInfo) {
  if (!playwrightInfo.playwright) {
    return {
      browser: null,
      source: null,
      attempts: playwrightInfo.attempts,
      reason: "PLAYWRIGHT_PACKAGE_UNAVAILABLE",
    };
  }

  const candidates = uniqueCandidates([
    ...resolvedPlaywrightExecutable(playwrightInfo.playwright),
    ...browserCacheCandidates(playwrightInfo.mamRoot),
    ...systemBrowserCandidates(),
  ]);
  const attempts = [...playwrightInfo.attempts];

  for (const candidate of candidates) {
    try {
      const browser = await playwrightInfo.playwright.chromium.launch({
        headless: true,
        executablePath: candidate.executablePath,
      });
      return {
        browser,
        source: candidate.label,
        attempts,
        reason: null,
      };
    } catch (error) {
      attempts.push({
        source: candidate.label,
        error: sanitizeMessage(error.message),
      });
    }
  }

  try {
    const browser = await playwrightInfo.playwright.chromium.launch({ headless: true });
    return {
      browser,
      source: "PLAYWRIGHT_DEFAULT",
      attempts,
      reason: null,
    };
  } catch (error) {
    attempts.push({
      source: "PLAYWRIGHT_DEFAULT",
      error: sanitizeMessage(error.message),
    });
  }

  return {
    browser: null,
    source: null,
    attempts,
    reason: "BROWSER_EXECUTABLE_UNAVAILABLE",
  };
}

function writeReport(outputRoot, report) {
  fs.mkdirSync(outputRoot, { recursive: true });
  fs.writeFileSync(
    path.join(outputRoot, "ATLASFIN_VISUAL_GATE.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
}

async function main() {
  const atlasRoot = path.resolve(process.argv[2] || path.join(__dirname, ".."));
  const outputRoot = path.resolve(process.argv[3] || path.join(atlasRoot, "quality", "evidence"));
  fs.mkdirSync(outputRoot, { recursive: true });

  const fixturePath = path.join(atlasRoot, "quality", "atlasfin_state_fixture.html");
  if (!fs.existsSync(fixturePath)) throw new Error(`FIXTURE_MISSING:${fixturePath}`);

  const playwrightInfo = findPlaywright();
  const launched = await launchAvailableBrowser(playwrightInfo);

  if (!launched.browser) {
    const report = {
      schema: "prisma.atlasfin.visual-collision-gate.v1",
      schemaVersion: "1.1.0",
      status: "SKIPPED_BROWSER_UNAVAILABLE",
      fixture: "quality/atlasfin_state_fixture.html",
      viewport: { width: 1440, height: 900 },
      reason: launched.reason,
      browserDiscovery: {
        playwrightSource: playwrightInfo.source,
        attempts: launched.attempts,
        rawPathsIncluded: false,
      },
      checks: {},
      evidence: [],
      runtimeMutationExecuted: false,
      portMutationExecuted: false,
      serverStarted: false,
    };
    writeReport(outputRoot, report);
    console.error("BROWSER_EXECUTABLE_UNAVAILABLE");
    process.exitCode = 3;
    return;
  }

  const browser = launched.browser;
  let page;
  try {
    page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
    const consoleErrors = [];
    page.on("console", message => {
      if (message.type() === "error") consoleErrors.push(message.text());
    });
    page.on("pageerror", error => consoleErrors.push(error.message));

    await page.goto(pathToFileURL(fixturePath).href, { waitUntil: "load" });
    await page.evaluate(() => document.fonts?.ready);
    await page.locator('[data-atlas-evidence-state="focus"]').focus();

    const measurements = await page.evaluate(() => {
      const rect = element => {
        const value = element.getBoundingClientRect();
        return {
          left: value.left,
          top: value.top,
          right: value.right,
          bottom: value.bottom,
          width: value.width,
          height: value.height,
        };
      };
      const intersects = (a, b) =>
        Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left))
        * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));

      const root = document.documentElement;
      const body = document.body;
      const fixture = document.querySelector("[data-atlasfin-evidence-fixture]");
      const cards = [...document.querySelectorAll("[data-atlas-evidence-state]")];
      const labels = [...document.querySelectorAll("[data-evidence-label]")];
      const collisions = [];

      for (let i = 0; i < labels.length; i += 1) {
        for (let j = i + 1; j < labels.length; j += 1) {
          if (labels[i].closest("[data-atlas-evidence-state]") !== labels[j].closest("[data-atlas-evidence-state]")) continue;
          const area = intersects(rect(labels[i]), rect(labels[j]));
          if (area > 1) {
            collisions.push({
              a: labels[i].textContent.trim(),
              b: labels[j].textContent.trim(),
              area,
            });
          }
        }
      }

      const statusRows = cards.map(card => {
        const status = card.querySelector("[data-evidence-status]");
        const style = status ? getComputedStyle(status) : null;
        return {
          state: card.dataset.atlasEvidenceState,
          cardScrollWidth: card.scrollWidth,
          cardClientWidth: card.clientWidth,
          cardScrollHeight: card.scrollHeight,
          cardClientHeight: card.clientHeight,
          statusScrollWidth: status?.scrollWidth || 0,
          statusClientWidth: status?.clientWidth || 0,
          statusHeight: status?.getBoundingClientRect().height || 0,
          statusLineHeight: style ? parseFloat(style.lineHeight) : 0,
        };
      });

      const disabled = document.querySelector('[data-atlas-evidence-state="disabled"] button');
      const enabled = document.querySelector('[data-atlas-evidence-state="enabled"]');
      const focus = document.querySelector('[data-atlas-evidence-state="focus"]');
      const loading = document.querySelector('[data-atlas-evidence-state="loading"]');
      const skipped = document.querySelector('[data-atlas-evidence-state="skipped"]');

      return {
        document: {
          scrollWidth: root.scrollWidth,
          clientWidth: root.clientWidth,
          scrollHeight: root.scrollHeight,
          clientHeight: root.clientHeight,
          bodyScrollWidth: body.scrollWidth,
          bodyClientWidth: body.clientWidth,
          bodyScrollHeight: body.scrollHeight,
          bodyClientHeight: body.clientHeight,
        },
        fixture: {
          scrollWidth: fixture.scrollWidth,
          clientWidth: fixture.clientWidth,
          scrollHeight: fixture.scrollHeight,
          clientHeight: fixture.clientHeight,
        },
        statusRows,
        collisions,
        semantics: {
          disabledLabeledDisabled: Boolean(disabled?.disabled),
          enabledLabeledFixture: enabled?.dataset.atlasEvidenceKind === "fixture",
          focusVisible: document.activeElement === focus,
          loadingLabeledLoading: loading?.getAttribute("aria-busy") === "true",
          skippedNotTested: skipped?.dataset.testStatus === "skipped_not_tested",
        },
        piiText: document.body.innerText,
      };
    });

    const piiMatches = [];
    const email = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/ig;
    const phone = /(?:\+?\d[\s().-]*){10,}/g;
    if (measurements.piiText.match(email)) piiMatches.push("EMAIL");
    if (measurements.piiText.match(phone)) piiMatches.push("PHONE");

    const checks = {
      documentNoHorizontalOverflow: measurements.document.scrollWidth <= measurements.document.clientWidth,
      documentNoVerticalOverflow: measurements.document.scrollHeight <= measurements.document.clientHeight,
      fixtureNoHorizontalOverflow: measurements.fixture.scrollWidth <= measurements.fixture.clientWidth,
      fixtureNoVerticalOverflow: measurements.fixture.scrollHeight <= measurements.fixture.clientHeight,
      cardsNoClipping: measurements.statusRows.every(row =>
        row.cardScrollWidth <= row.cardClientWidth
        && row.cardScrollHeight <= row.cardClientHeight
        && row.statusScrollWidth <= row.statusClientWidth
      ),
      noLabelCollisions: measurements.collisions.length === 0,
      stableWrapping: measurements.statusRows.every(row => row.statusScrollWidth <= row.statusClientWidth),
      disabledLabeledDisabled: measurements.semantics.disabledLabeledDisabled,
      enabledLabeledFixture: measurements.semantics.enabledLabeledFixture,
      focusVisible: measurements.semantics.focusVisible,
      loadingLabeledLoading: measurements.semantics.loadingLabeledLoading,
      skippedNotTested: measurements.semantics.skippedNotTested,
      noConsoleErrors: consoleErrors.length === 0,
      noPii: piiMatches.length === 0,
    };

    await page.screenshot({
      path: path.join(outputRoot, "atlasfin_states_all.png"),
      fullPage: false,
    });
    for (const state of ["disabled", "enabled", "focus", "loading", "skipped"]) {
      await page.locator(`[data-atlas-evidence-state="${state}"]`).screenshot({
        path: path.join(outputRoot, `atlasfin_state_${state}.png`),
      });
    }

    const report = {
      schema: "prisma.atlasfin.visual-collision-gate.v1",
      schemaVersion: "1.1.0",
      status: Object.values(checks).every(Boolean) ? "PASS" : "FAIL",
      fixture: "quality/atlasfin_state_fixture.html",
      viewport: { width: 1440, height: 900 },
      browserSource: launched.source,
      checks,
      measurements: { ...measurements, piiText: undefined },
      consoleErrors,
      piiMatches,
      evidence: [
        "atlasfin_states_all.png",
        "atlasfin_state_disabled.png",
        "atlasfin_state_enabled.png",
        "atlasfin_state_focus.png",
        "atlasfin_state_loading.png",
        "atlasfin_state_skipped.png",
      ],
      runtimeMutationExecuted: false,
      portMutationExecuted: false,
      serverStarted: false,
    };
    writeReport(outputRoot, report);
    console.log(JSON.stringify(report, null, 2));
    process.exitCode = report.status === "PASS" ? 0 : 2;
  } finally {
    await browser.close();
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error(sanitizeMessage(error.stack || error.message));
    process.exitCode = 2;
  });
}

module.exports = {
  sanitizeMessage,
  playwrightCandidates,
  systemBrowserCandidates,
  browserCacheCandidates,
  findPlaywright,
  launchAvailableBrowser,
};
