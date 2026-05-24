#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const appRoot = path.join(root, "products", "pc", "app");
const pageRoot = path.join(appRoot, "app");
const files = [
  path.join(appRoot, "src", "uiux", "page-contracts.ts"),
  path.join(appRoot, "src", "uiux", "copy-dictionary.ts")
].filter(f => fs.existsSync(f));

const joined = files.map(f => fs.readFileSync(f, "utf8")).join("\n");
const required = {
  loading: [/loading/i, /preparando/i],
  empty: [/empty/i, /sin datos/i, /no hay/i, /defaultTitle/i],
  error: [/error/i, /no se pudo/i, /defaultAction/i],
  stale: [/stale/i, /atrasad/i],
  demo: [/demo/i, /mock/i, /prueba/i],
  partial: [/partial/i, /parcial/i, /incomplet/i]
};

const missing = [];
for (const [state, patterns] of Object.entries(required)) {
  if (!patterns.some(rx => rx.test(joined))) missing.push(state);
}

console.log(JSON.stringify({ verifier: "verify_pc_uiux_states_contract", status: missing.length ? "FAIL" : "PASS", scannedFiles: files.map(f => path.relative(root, f).replace(/\\/g, "/")), missing }, null, 2));
process.exit(missing.length ? 1 : 0);
