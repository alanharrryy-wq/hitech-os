#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const verifier = path.join(appRoot, "tools", "verify_tablet_standalone_full_engine_01.mjs");
const result = spawnSync(process.execPath, [verifier], {
  cwd: appRoot,
  stdio: "inherit",
  shell: false
});

process.exit(result.status ?? 1);
