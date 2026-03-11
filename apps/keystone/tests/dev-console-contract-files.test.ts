import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

interface PanelContract {
  readonly id: string;
  readonly domain: string;
  readonly file: string;
  readonly requires_scene_look_model: boolean;
}

interface EventContract {
  readonly symbol: string;
  readonly must_have_emitter: boolean;
  readonly must_have_listener: boolean;
}

function readJson(relativePath: string): unknown {
  const currentDir = fileURLToPath(new URL(".", import.meta.url));
  const absolute = resolve(currentDir, "..", "..", "..", relativePath);
  return JSON.parse(readFileSync(absolute, "utf-8"));
}

describe("Dev Console architecture contracts", () => {
  it("declares valid panel contracts", () => {
    const payload = readJson("docs/dev-console/contracts/panels.json") as {
      version: number;
      panels: PanelContract[];
    };

    expect(payload.version).toBe(1);
    expect(payload.panels.length).toBeGreaterThanOrEqual(10);

    const ids = new Set<string>();
    for (const panel of payload.panels) {
      expect(panel.id.length).toBeGreaterThan(0);
      expect(panel.file.endsWith(".tsx")).toBe(true);
      expect(["core", "inspect", "compose"]).toContain(panel.domain);
      expect(ids.has(panel.id)).toBe(false);
      ids.add(panel.id);
    }
  });

  it("declares required event contracts", () => {
    const payload = readJson("docs/dev-console/contracts/events.json") as {
      version: number;
      events: EventContract[];
    };

    expect(payload.version).toBe(1);
    const symbols = new Set(payload.events.map((event) => event.symbol));

    expect(symbols.has("DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT")).toBe(true);
    expect(symbols.has("DEV_CONSOLE_DIAGNOSTICS_EVENT")).toBe(true);
    expect(symbols.has("DEV_CONSOLE_SNAPSHOT_EVENT")).toBe(true);
    expect(symbols.has("DEV_CONSOLE_OPEN_SCENE_EVENT")).toBe(true);
    expect(symbols.has("DEV_CONSOLE_VALIDATE_SCENE_EVENT")).toBe(true);
  });
});
