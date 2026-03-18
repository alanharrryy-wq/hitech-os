export interface EvidenceArtifact {
  readonly path: string;
  readonly kind: "txt" | "json" | "stdout" | "stderr" | "csv" | "jsonl";
  readonly purpose: string;
}

export interface EvidenceBundleIndex {
  readonly installSummary: readonly EvidenceArtifact[];
  readonly verification: readonly EvidenceArtifact[];
  readonly smoke: readonly EvidenceArtifact[];
}
