import { summarizeReport } from "../post-install-report";
import { type VerificationReport } from "../contracts";

const report: VerificationReport = {
  packageName: "demo",
  repoRoot: "F:/repos/hitech-os",
  downloadsRoot: "F:/OneDrive/Descargas",
  docsRoot: "F:/repos/hitech-os/docs/live-scene-composer",
  stagingRoot: "F:/repos/hitech-os/tools/live-scene-composer/demo",
  mirrorStatus: "staged-only",
  verificationStatus: "partial",
  smokeStatus: "passed",
  guardStatus: "skipped",
  copiedDocsCount: 10,
  stagedFilesCount: 20,
  mirroredFilesCount: 0,
  checks: [],
  nextCommands: []
};

console.log(summarizeReport(report));
