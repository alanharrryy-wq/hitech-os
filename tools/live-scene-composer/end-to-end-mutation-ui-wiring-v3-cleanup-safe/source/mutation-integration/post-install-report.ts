import { type VerificationReport } from "./contracts";

export function summarizeReport(report: VerificationReport): string[] {
  return [
    `package=${report.packageName}`,
    `verification=${report.verificationStatus}`,
    `smoke=${report.smokeStatus}`,
    `guard=${report.guardStatus}`,
    `mirror=${report.mirrorStatus}`,
    `docs=${report.copiedDocsCount}`,
    `staged=${report.stagedFilesCount}`,
    `mirrored=${report.mirroredFilesCount}`
  ];
}
