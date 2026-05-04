#!/usr/bin/env node
/* PRISMA_TRI_SURFACE_VISUAL_GUARDIAN_00B node wrapper.
 * Delegates to the canonical Python guardian so existing Node-style checker habits still work.
 */
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const guardian = path.join(__dirname, "prisma_tri_surface_visual_guardian_00b.py");
const result = spawnSync("python", [guardian, ...process.argv.slice(2)], { stdio: "inherit" });
if (result.error) {
  console.error(`Failed to launch Python guardian: ${result.error.message}`);
  process.exit(2);
}
process.exit(result.status ?? 2);
