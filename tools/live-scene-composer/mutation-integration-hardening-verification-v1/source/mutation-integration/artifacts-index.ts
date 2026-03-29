import { type EvidenceBundleIndex } from "./evidence-contracts";

export const defaultArtifactsIndex: EvidenceBundleIndex = {
  installSummary: [
    { path: "install_summary.txt", kind: "txt", purpose: "Human install summary" },
    { path: "install_summary.json", kind: "json", purpose: "Machine install summary" }
  ],
  verification: [
    { path: "verification_report.txt", kind: "txt", purpose: "Human verification report" },
    { path: "verification_report.json", kind: "json", purpose: "Machine verification report" }
  ],
  smoke: [
    { path: "smoke_report.txt", kind: "txt", purpose: "Human smoke report" },
    { path: "smoke_report.json", kind: "json", purpose: "Machine smoke report" }
  ]
};
