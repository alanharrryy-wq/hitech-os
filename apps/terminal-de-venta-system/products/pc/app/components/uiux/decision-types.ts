import type { ReactNode } from "react";
import type { PcEvidenceRecord } from "@/uiux/page-contracts";

export type SummaryTone = "danger" | "warn" | "ok" | "info";

export type SummaryCard = {
  title: string;
  eyebrow: string;
  tone: SummaryTone;
  lines: string[];
};

export type RecommendedAction = {
  title: string;
  motive: string;
  actions: Array<{ label: string; href: string; primary?: boolean; destructive?: boolean }>;
};

export type EvidenceItem = PcEvidenceRecord;

export type ChartInsight = {
  title: string;
  question: string;
  reading: string;
  action: string;
  bars: Array<{ label: string; value: string; level: "Alto" | "Medio" | "Bajo" }>;
};

export type DecisionScreenChildren = ReactNode;
