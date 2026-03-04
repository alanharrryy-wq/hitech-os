import { expect, type ConsoleMessage, type Page, type TestInfo } from "@playwright/test";

export const HYDRATION_MISMATCH_PATTERNS: ReadonlyArray<RegExp> = [
  /Hydration failed/i,
  /didn't match the client/i,
  /Text content did not match/i
];

const DEFAULT_OVERLAY_MARKER_SELECTOR = "[data-pitch-debug-overlay='1']";
const DEFAULT_MAX_CONSOLE_MESSAGES = 200;
const DEFAULT_RUN_ID_ENV_VAR_NAMES = ["RUN_ID", "HITECH_RUN_ID", "PITCH_ENGINE_RUN_ID"] as const;

type HydrationSeverity = "warn" | "error";
type GuardSource = "console" | "pageerror";

export interface GuardConsoleMessage {
  index: number;
  source: GuardSource;
  type: string;
  text: string;
  url: string;
}

export interface HydrationEvidence {
  source: GuardSource;
  severity: HydrationSeverity;
  text: string;
  url: string;
}

export interface HydrationGuardOptions {
  overlayMarkerSelector?: string;
  maxConsoleMessages?: number;
  runIdEnvVarNames?: readonly string[];
}

export interface DebugOverlayAssertionOptions {
  markerSelector?: string;
  requirePresentWhenEnabled?: boolean;
}

export interface HydrationConsoleGuard {
  dispose: () => void;
  getConsoleMessages: () => readonly GuardConsoleMessage[];
  getHydrationEvidence: () => readonly HydrationEvidence[];
  assertNoHydrationWarningsOrErrors: (testInfo?: TestInfo) => Promise<void>;
  assertDebugOverlayGating: (options?: DebugOverlayAssertionOptions) => Promise<void>;
  logFailureDiagnostics: (testInfo: TestInfo) => Promise<void>;
}

function normalizeWhitespace(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

function isHydrationText(text: string): boolean {
  return HYDRATION_MISMATCH_PATTERNS.some((pattern) => pattern.test(text));
}

function resolveRunId(runIdEnvVarNames: readonly string[]): string {
  for (const envName of runIdEnvVarNames) {
    const candidate = process.env[envName];
    if (candidate && candidate.trim().length > 0) {
      return candidate.trim();
    }
  }
  return "UNKNOWN_RUN_ID";
}

function formatDiagnosticsReport(
  runId: string,
  route: string,
  hydrationEvidence: readonly HydrationEvidence[],
  consoleMessages: readonly GuardConsoleMessage[]
): string {
  const lines: string[] = [
    "[hydration-guard] failure diagnostics",
    `runId: ${runId}`,
    `route: ${route}`,
    `hydrationSignals: ${hydrationEvidence.length}`,
    "topConsoleMessages:"
  ];

  const topConsoleMessages = consoleMessages.slice(0, 20);
  if (topConsoleMessages.length === 0) {
    lines.push("- (none)");
  } else {
    for (const entry of topConsoleMessages) {
      lines.push(`- #${entry.index} [${entry.source}/${entry.type}] ${entry.url} :: ${entry.text}`);
    }
  }

  if (hydrationEvidence.length > 0) {
    lines.push("hydrationEvidence:");
    for (const evidence of hydrationEvidence) {
      lines.push(
        `- [${evidence.severity}] [${evidence.source}] ${evidence.url} :: ${evidence.text}`
      );
    }
  }

  return lines.join("\n");
}

function extractConsoleUrl(message: ConsoleMessage, fallbackUrl: string): string {
  const location = message.location();
  if (location?.url && location.url.trim().length > 0) {
    return location.url;
  }
  return fallbackUrl;
}

function toHydrationSeverity(consoleType: string): HydrationSeverity {
  return consoleType === "error" ? "error" : "warn";
}

export function createHydrationConsoleGuard(
  page: Page,
  options: HydrationGuardOptions = {}
): HydrationConsoleGuard {
  const overlayMarkerSelector = options.overlayMarkerSelector ?? DEFAULT_OVERLAY_MARKER_SELECTOR;
  const maxConsoleMessages = options.maxConsoleMessages ?? DEFAULT_MAX_CONSOLE_MESSAGES;
  const runIdEnvVarNames = options.runIdEnvVarNames ?? DEFAULT_RUN_ID_ENV_VAR_NAMES;

  const consoleMessages: GuardConsoleMessage[] = [];
  const hydrationEvidence: HydrationEvidence[] = [];
  let eventIndex = 0;

  const pushConsoleMessage = (entry: GuardConsoleMessage): void => {
    if (consoleMessages.length < maxConsoleMessages) {
      consoleMessages.push(entry);
    }
  };

  const onConsole = (message: ConsoleMessage): void => {
    const pageUrl = page.url();
    const text = normalizeWhitespace(message.text());
    const entry: GuardConsoleMessage = {
      index: eventIndex,
      source: "console",
      type: message.type(),
      text,
      url: extractConsoleUrl(message, pageUrl)
    };
    eventIndex += 1;

    pushConsoleMessage(entry);

    if (isHydrationText(text)) {
      hydrationEvidence.push({
        source: "console",
        severity: toHydrationSeverity(entry.type),
        text,
        url: entry.url
      });
    }
  };

  const onPageError = (error: Error): void => {
    const pageUrl = page.url();
    const text = normalizeWhitespace(error.stack ?? error.message ?? String(error));
    const entry: GuardConsoleMessage = {
      index: eventIndex,
      source: "pageerror",
      type: "error",
      text,
      url: pageUrl
    };
    eventIndex += 1;

    pushConsoleMessage(entry);

    if (isHydrationText(text)) {
      hydrationEvidence.push({
        source: "pageerror",
        severity: "error",
        text,
        url: pageUrl
      });
    }
  };

  page.on("console", onConsole);
  page.on("pageerror", onPageError);

  return {
    dispose: () => {
      page.off("console", onConsole);
      page.off("pageerror", onPageError);
    },

    getConsoleMessages: () => [...consoleMessages],

    getHydrationEvidence: () => [...hydrationEvidence],

    assertNoHydrationWarningsOrErrors: async (testInfo?: TestInfo) => {
      if (hydrationEvidence.length === 0) {
        return;
      }

      const runId = resolveRunId(runIdEnvVarNames);
      const report = formatDiagnosticsReport(runId, page.url(), hydrationEvidence, consoleMessages);

      console.error(report);

      if (testInfo) {
        await testInfo.attach("hydration-guard-report", {
          body: report,
          contentType: "text/plain"
        });
      }

      throw new Error(`Hydration warnings/errors detected.\n${report}`);
    },

    assertDebugOverlayGating: async (assertionOptions: DebugOverlayAssertionOptions = {}) => {
      const markerSelector = assertionOptions.markerSelector ?? overlayMarkerSelector;
      const markerCount = await page.locator(markerSelector).count();
      const debugEnabled = process.env["NEXT_PUBLIC_PITCH_DEBUG"] === "1";

      if (!debugEnabled) {
        expect(
          markerCount,
          `Debug overlay marker '${markerSelector}' must be absent when NEXT_PUBLIC_PITCH_DEBUG != '1'.`
        ).toBe(0);
        return;
      }

      if (assertionOptions.requirePresentWhenEnabled === true) {
        expect(
          markerCount,
          `Debug overlay marker '${markerSelector}' is expected when NEXT_PUBLIC_PITCH_DEBUG='1'.`
        ).toBeGreaterThan(0);
      }
    },

    logFailureDiagnostics: async (testInfo: TestInfo) => {
      if (testInfo.status === testInfo.expectedStatus) {
        return;
      }

      const runId = resolveRunId(runIdEnvVarNames);
      const report = formatDiagnosticsReport(runId, page.url(), hydrationEvidence, consoleMessages);

      console.error(report);

      await testInfo.attach("hydration-guard-diagnostics", {
        body: report,
        contentType: "text/plain"
      });
    }
  };
}
