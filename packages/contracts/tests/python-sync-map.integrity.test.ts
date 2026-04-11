import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";

describe("python sync map integrity", () => {
  it("references schema files that exist", () => {
    const generatedRoot = path.resolve(process.cwd(), "packages/contracts/schemas/generated");
    const syncMapPath = path.join(generatedRoot, "python-sync-map.json");
    const raw = fs.readFileSync(syncMapPath, "utf8");
    const parsed = JSON.parse(raw) as { schemaFiles?: string[]; pythonModelMap?: Record<string, string> };

    expect(Array.isArray(parsed.schemaFiles)).toBe(true);
    expect(parsed.schemaFiles && parsed.schemaFiles.length).toBeGreaterThan(0);

    for (const item of parsed.schemaFiles ?? []) {
      const schemaPath = path.join(generatedRoot, item);
      expect(fs.existsSync(schemaPath), `missing schema file: ${item}`).toBe(true);
    }

    expect(parsed.pythonModelMap).toBeTruthy();
    expect(Object.keys(parsed.pythonModelMap ?? {}).length).toBeGreaterThan(0);
  });
});
