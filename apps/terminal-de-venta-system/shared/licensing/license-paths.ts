import path from "node:path";
import fs from "node:fs";
import { buildDevPaths, defaultProgramDataRoot, findTerminalSystemRoot, resolveRuntimeContext, type RuntimeContext } from "../runtime";

export type LicensePathResolution = {
  path: string;
  source: "explicit" | "runtime_config" | "programdata" | "legacy_programdata" | "dev";
  exists: boolean;
  runtimeMode: "dev" | "customer" | "test" | "release";
  isDevFallback: boolean;
  warnings: string[];
  blockingIssues: string[];
};

export function getSystemRoot(): string {
  return path.resolve(process.env.TV_SYSTEM_ROOT || findTerminalSystemRoot(process.cwd()));
}

export function getLicenseCandidatePaths(runtimeContext?: RuntimeContext): LicensePathResolution[] {
  const context = runtimeContext ?? resolveRuntimeContext();
  const source = context.provenance.licenseFile?.source;
  const primarySource: LicensePathResolution["source"] =
    source === "explicit" || source === "env" ? "explicit" :
    source === "runtime_config" ? "runtime_config" :
    source === "legacy_programdata" ? "legacy_programdata" :
    source === "dev_fallback" ? "dev" :
    "programdata";
  const candidates: LicensePathResolution[] = [
    {
      path: context.licenseFile,
      source: primarySource,
      exists: fs.existsSync(context.licenseFile),
      runtimeMode: context.runtimeMode,
      isDevFallback: primarySource === "dev",
      warnings: context.warnings.map((issue) => issue.code),
      blockingIssues: context.blockingIssues.map((issue) => issue.code)
    }
  ];

  if (context.runtimeMode === "dev") {
    const devUnsigned = path.join(buildDevPaths(getSystemRoot()).runtimeRoot, "license", "license.dev.json");
    candidates.push({
      path: devUnsigned,
      source: "dev",
      exists: fs.existsSync(devUnsigned),
      runtimeMode: context.runtimeMode,
      isDevFallback: true,
      warnings: context.warnings.map((issue) => issue.code),
      blockingIssues: context.blockingIssues.map((issue) => issue.code)
    });
  }

  const legacy = path.join(defaultProgramDataRoot(), "PRISMA", "config", "license.json");
  if (legacy !== context.licenseFile) {
    candidates.push({
      path: legacy,
      source: "legacy_programdata",
      exists: fs.existsSync(legacy),
      runtimeMode: context.runtimeMode,
      isDevFallback: false,
      warnings: context.warnings.map((issue) => issue.code),
      blockingIssues: context.blockingIssues.map((issue) => issue.code)
    });
  }

  return candidates;
}

export function resolveLocalLicensePath(runtimeContext?: RuntimeContext): LicensePathResolution {
  const candidates = getLicenseCandidatePaths(runtimeContext);
  return candidates.find((candidate) => candidate.exists) ?? candidates[0];
}
