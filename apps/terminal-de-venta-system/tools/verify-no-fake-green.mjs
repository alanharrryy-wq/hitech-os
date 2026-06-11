import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const mobile = fs.readFileSync(path.join(root, "products/mobile/app/src/lib/prisma-app/mobile-data-plane/outbox-adapter.ts"), "utf8");
const docCandidates = [
  path.join(root, "docs/prisma/PRISMA_SYNC_CLOSURE_PATCH_20260518.md"),
  path.join(root, "docs/legacy/sync/PRISMA_SYNC_CLOSURE_PATCH_20260518.md")
];
const docs = docCandidates
  .filter((docPath) => fs.existsSync(docPath))
  .map((docPath) => fs.readFileSync(docPath, "utf8"))
  .join("\n");
const failures = [];

if (mobile.includes('status === "sent"') || mobile.includes('status === "synced"')) failures.push("Mobile fake-green alias remains");
if (!docs.includes("NEEDS_RUNTIME_TEST") || !docs.toLowerCase().includes("no fake green")) failures.push("Patch docs do not state runtime evidence/no fake green limits");
if (failures.length) {
  console.error("PRISMA_NO_FAKE_GREEN failed");
  console.error(JSON.stringify({ failures }, null, 2));
  process.exit(1);
}
console.log("PRISMA_NO_FAKE_GREEN passed");
