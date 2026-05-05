export type PrismaScreenTone = "ok" | "warn" | "danger" | "neutral";

export type PrismaScreenDensity = "standard" | "dense" | "executive";

export type PrismaScreenAction = {
  label: string;
  description?: string;
  href?: string;
  tone?: PrismaScreenTone;
  disabled?: boolean;
};

export type PrismaScreenStatus = {
  label: string;
  tone: PrismaScreenTone;
};

export type PrismaScreenMetric = {
  label: string;
  value: string;
  note?: string;
  tone?: PrismaScreenTone;
  emphasis?: "primary" | "secondary";
};

export type PrismaScreenHero = {
  eyebrow: string;
  title: string;
  description: string;
  signal?: PrismaScreenStatus;
};

export type PrismaScreenListItem = {
  title: string;
  description?: string;
  meta?: string;
  value?: string;
  tone?: PrismaScreenTone;
};

export type PrismaScreenTableColumn = {
  key: string;
  label: string;
  align?: "left" | "right" | "center";
};

export type PrismaScreenTableRow = Record<string, string | number | null | undefined> & {
  id?: string;
  tone?: PrismaScreenTone;
};

export type PrismaScreenTable = {
  columns: PrismaScreenTableColumn[];
  rows: PrismaScreenTableRow[];
};

export type PrismaScreenSection = {
  id: string;
  title: string;
  subtitle?: string;
  kind: "table" | "list" | "alerts" | "actions" | "timeline" | "custom";
  tone?: PrismaScreenTone;
  table?: PrismaScreenTable;
  items?: PrismaScreenListItem[];
  emptyTitle?: string;
  emptyDescription?: string;
};

export type PrismaOperationalScreenModel = {
  currentPath: string;
  title: string;
  subtitle: string;
  kicker?: string;
  density?: PrismaScreenDensity;
  status?: PrismaScreenStatus;
  actions?: PrismaScreenAction[];
  hero?: PrismaScreenHero;
  metrics: PrismaScreenMetric[];
  sections: PrismaScreenSection[];
};

export const PRISMA_OPERATIONAL_SCREEN_ORDER = [
  "shell",
  "masthead",
  "status",
  "actions",
  "metrics",
  "primary-section",
  "secondary-sections",
  "empty-error-offline-states"
] as const;
