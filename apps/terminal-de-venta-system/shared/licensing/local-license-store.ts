import fs from "node:fs";
import path from "node:path";
import { resolveLocalLicensePath } from "./license-paths";
import { defaultRefreshState, type LicenseRefreshState } from "./license-refresh-state";

function ensureParent(file: string): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
}

function nowStamp(): string {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

export function getCurrentLicenseFilePath(): string {
  return resolveLocalLicensePath().path;
}

export function getRefreshStatePath(): string {
  return path.join(path.dirname(getCurrentLicenseFilePath()), "license-refresh-state.json");
}

export function readLicenseRefreshState(enabled = false): LicenseRefreshState {
  const file = getRefreshStatePath();
  if (!fs.existsSync(file)) return defaultRefreshState(enabled);
  try {
    return { ...defaultRefreshState(enabled), ...JSON.parse(fs.readFileSync(file, "utf8")), enabled } as LicenseRefreshState;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { ...defaultRefreshState(enabled), state: "refresh_failed", lastError: `LICENSE_REFRESH_STATE_INVALID: ${message}` };
  }
}

export function writeLicenseRefreshState(state: LicenseRefreshState): void {
  const file = getRefreshStatePath();
  ensureParent(file);
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(state, null, 2) + "\n", "utf8");
  fs.renameSync(tmp, file);
}

export function writeLicenseAtomically(serializedLicense: string): { path: string; backupPath: string | null } {
  const file = getCurrentLicenseFilePath();
  ensureParent(file);
  let backupPath: string | null = null;
  if (fs.existsSync(file)) {
    backupPath = `${file}.${nowStamp()}.bak`;
    fs.copyFileSync(file, backupPath);
  }
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, serializedLicense.endsWith("\n") ? serializedLicense : serializedLicense + "\n", "utf8");
  fs.renameSync(tmp, file);
  return { path: file, backupPath };
}
