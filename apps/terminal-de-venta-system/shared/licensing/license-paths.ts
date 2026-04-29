import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export type LicensePathResolution = {
  path: string;
  source: "env" | "programdata" | "dev" | "unix";
  exists: boolean;
};

function findSystemRoot(start: string): string {
  let current = path.resolve(start);
  for (let i = 0; i < 12; i += 1) {
    if (fs.existsSync(path.join(current, "products")) || fs.existsSync(path.join(current, "terminal_de_venta.cmd"))) {
      return current;
    }
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return path.resolve(start);
}

export function getSystemRoot(): string {
  return path.resolve(process.env.TV_SYSTEM_ROOT || findSystemRoot(process.cwd()));
}

export function getLicenseCandidatePaths(): LicensePathResolution[] {
  const candidates: LicensePathResolution[] = [];
  if (process.env.PRISMA_LICENSE_PATH) {
    candidates.push({ path: path.resolve(process.env.PRISMA_LICENSE_PATH), source: "env", exists: false });
  }

  if (os.platform() === "win32") {
    const programData = process.env.ProgramData || "C:\\ProgramData";
    candidates.push({ path: path.join(programData, "PRISMA", "license", "license.json"), source: "programdata", exists: false });
  } else {
    candidates.push({ path: "/var/lib/prisma/license/license.json", source: "unix", exists: false });
  }

  candidates.push({ path: path.join(getSystemRoot(), "local-runtime", "license", "license.signed.dev.json"), source: "dev", exists: false });
  candidates.push({ path: path.join(getSystemRoot(), "local-runtime", "license", "license.dev.json"), source: "dev", exists: false });
  return candidates.map((candidate) => ({ ...candidate, exists: fs.existsSync(candidate.path) }));
}

export function resolveLocalLicensePath(): LicensePathResolution {
  const candidates = getLicenseCandidatePaths();
  return candidates.find((candidate) => candidate.exists) ?? candidates[0];
}
