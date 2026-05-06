import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const marker = "PRISMA_VISUAL_OS_LIVE_STATUS_TRUTH_00ZL";
const files = {
  pos: "products/tablet/app/components/pos/pos-live-binding.tsx",
  studio: "products/tablet/app/app/visual-os/PrismaStudioProQaClient.tsx",
  doc: "tools/prisma-visual-os/docs/VISUAL_OS_LIVE_STATUS_TRUTH_00ZL.md",
  verifier: "tools/prisma-visual-os/verify_prisma_visual_os_live_status_truth_00zl.mjs"
};

function read(rel) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) throw new Error(`missing ${rel}`);
  return fs.readFileSync(abs, "utf8");
}

const pos = read(files.pos);
const studio = read(files.studio);
const doc = read(files.doc);
const verifier = read(files.verifier);

const checks = [
  ["pos listens named controls event", pos.includes('addEventListener("prisma.visual.controls"')],
  ["pos listens status event", pos.includes('addEventListener("prisma.visual.status"')],
  ["pos hydrates state", pos.includes('STATE_URL') && pos.includes('/state') && pos.includes('lastPayload')],
  ["pos preserves compatibility onmessage", pos.includes('source.onmessage = handlePayloadEvent')],
  ["pos has marker", pos.includes(marker)],
  ["studio avoids fake ready label", studio.includes('no confirmado')],
  ["studio explains realtime error", studio.includes('error: revisa 4177')],
  ["studio has package marker", studio.includes('prismaVisualLiveStatusTruth') || studio.includes(marker)],
  ["doc has marker", doc.includes(marker)],
  ["verifier has marker", verifier.includes(marker)]
];

const failed = checks.filter(([, ok]) => !ok).map(([name]) => name);
if (failed.length) {
  console.error(`[${marker}] VERIFY FAILED`);
  console.error(JSON.stringify({ failed }, null, 2));
  process.exit(1);
}

console.log(`[${marker}] VERIFY OK`);
console.log(JSON.stringify({ root, checks: checks.length, files }, null, 2));
