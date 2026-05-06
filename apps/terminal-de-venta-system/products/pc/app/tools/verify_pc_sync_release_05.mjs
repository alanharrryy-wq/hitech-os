#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const args = process.argv.slice(2);
const idx = args.indexOf("--root");
const root = path.resolve(idx >= 0 && args[idx + 1] ? args[idx + 1] : process.cwd());
const required = [
  "app/sync/page.tsx",
  "app/api/sync/ingest/route.ts",
  "components/sync/sync-release-workspace.tsx",
  "src/modules/sync/types.ts",
  "src/server/validators/sync-event-contract.ts",
  "src/server/services/sync-ingest.service.ts",
  "src/server/services/sync-release.service.ts",
  "docs/release/PC_I05_SYNC_RELEASE.md"
];
function read(rel) { return fs.readFileSync(path.join(root, rel), "utf8"); }
const files = required.map((rel) => {
  const abs = path.join(root, rel);
  return { rel, exists: fs.existsSync(abs), bytes: fs.existsSync(abs) ? fs.statSync(abs).size : 0 };
});
const findings = [];
for (const file of files) {
  if (!file.exists) findings.push({ severity: "BLOCKER", code: "MISSING_FILE", message: file.rel });
  if (file.exists && file.bytes <= 0) findings.push({ severity: "BLOCKER", code: "EMPTY_FILE", message: file.rel });
}
if (findings.length === 0) {
  const route = read("app/api/sync/ingest/route.ts");
  for (const token of ["persistSyncIngestPayload", "classifySyncIngestPayload", "dryRun", "NextResponse.json"]) {
    if (!route.includes(token)) findings.push({ severity: "BLOCKER", code: "ROUTE_TOKEN_MISSING", message: token });
  }
  const validator = read("src/server/validators/sync-event-contract.ts");
  for (const token of ["REQUIRED_SYNC_EVENT_FIELDS", "classifySyncIngestPayload", "duplicate_event", "negative_stock", "terminal_not_registered", "old_local_price"]) {
    if (!validator.includes(token)) findings.push({ severity: "BLOCKER", code: "VALIDATOR_TOKEN_MISSING", message: token });
  }
  const service = read("src/server/services/sync-ingest.service.ts");
  for (const token of ["outboxEvent.create", "outboxEvent.findUnique", "eventId", "conflict", "acked", "failed"]) {
    if (!service.includes(token)) findings.push({ severity: "BLOCKER", code: "SERVICE_TOKEN_MISSING", message: token });
  }
  const ui = read("components/sync/sync-release-workspace.tsx");
  for (const label of ["Sync, dedupe y conflictos", "Campos requeridos", "Catálogo de conflictos", "Payload de prueba dry-run"]) {
    if (!ui.includes(label)) findings.push({ severity: "BLOCKER", code: "UI_LABEL_MISSING", message: label });
  }
}
const ok = findings.every((item) => item.severity !== "BLOCKER");
console.log(JSON.stringify({ verifier: "verify_pc_sync_release_05", iteration: "pc_i05_sync_release", root, ok, state: ok ? "PASS" : "FAIL", files, findings, checkedAt: new Date().toISOString() }, null, 2));
process.exit(ok ? 0 : 1);
