import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const required = [
  "products/tablet/app/components/pos/pos-live-binding.tsx",
  "products/tablet/app/components/pos/pos-screen.tsx",
  "products/tablet/app/components/pos/pos.module.css",
  "tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs",
  "docs/design/PRISMA_VISUAL_OS_POS_LIVE_BINDING_00T.md"
];

const missing = required.filter((rel) => !fs.existsSync(path.join(root, rel)));
if (missing.length) {
  console.error("[PRISMA 00T] VERIFY FAILED missing files");
  console.error(JSON.stringify(missing, null, 2));
  process.exit(1);
}

const screen = fs.readFileSync(path.join(root, "products/tablet/app/components/pos/pos-screen.tsx"), "utf8");
const binding = fs.readFileSync(path.join(root, "products/tablet/app/components/pos/pos-live-binding.tsx"), "utf8");
const css = fs.readFileSync(path.join(root, "products/tablet/app/components/pos/pos.module.css"), "utf8");

const connectsWithDirectSse =
  binding.includes("new EventSource") &&
  binding.includes("/events") &&
  binding.includes("source.onmessage");

const connectsWithClient =
  binding.includes("connectPrismaRealtime") &&
  binding.includes("applyPrismaRealtimePayload");

const checks = [
  ["PosScreen imports PosLiveBinding", screen.includes('import { PosLiveBinding } from "./pos-live-binding";') || screen.includes('import PosLiveBinding from "./pos-live-binding";')],
  ["PosScreen renders PosLiveBinding", screen.includes("<PosLiveBinding />")],
  ["POS workspace has 00T hook", screen.includes('data-prisma-pos-live="00T"')],
  ["Binding connects SSE", connectsWithDirectSse || connectsWithClient],
  ["Binding filters tablet_pos", binding.includes('payload.surface !== "tablet_pos"')],
  ["Binding applies live variables", binding.includes("setProperty") && binding.includes("--prisma-live-")],
  ["Binding exposes passive badge", binding.includes('data-prisma-pos-live-badge="00T"') && binding.includes('pointerEvents: "none"')],
  ["Binding exports named and default", binding.includes("export function PosLiveBinding") && binding.includes("export default PosLiveBinding")],
  ["CSS has safe no-layout marker", css.includes("PRISMA 00T SAFE NO-LAYOUT LIVE MARKER")],
  ["CSS removed old 00T layout selectors", !css.includes('posWorkspace[data-prisma-pos-live="00T"]') && !css.includes("PRISMA Visual OS 00T - POS Live Binding")],
  ["CSS removed aggressive 00T mappings", !css.includes("PRISMA 00T POS500 SAFE LIVE POS MAPPING") && !css.includes("PRISMA 00T AUTOPILOT HARD GLOBAL POS MAPPING") && !css.includes("PRISMA 00T HARD LIVE POS MAPPING") && !css.includes("FORCE VISIBLE LIVE POS MAPPING")],
  ["CSS module selector stays local", !/^meter\s*\{/m.test(css)]
];

const failed = checks.filter(([, ok]) => !ok).map(([name]) => name);
if (failed.length) {
  console.error("[PRISMA 00T] VERIFY FAILED");
  console.error(JSON.stringify(failed, null, 2));
  process.exit(1);
}

console.log("[PRISMA 00T] VERIFY OK");
console.log(JSON.stringify({ root, required: required.length, checks: checks.length, mode: "safe-no-layout" }, null, 2));
