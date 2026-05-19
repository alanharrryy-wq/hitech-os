import runtimeSnapshotJson from "./prisma-chart-runtime.snapshot.json";
import { mockMobileCharts, mockPcCharts, mockTabletCharts } from "../../../../../shared/prisma-charts/prismaChartMocks";
import type {
  PrismaMobileChartsViewModel,
  PrismaPcChartsViewModel,
  PrismaTabletChartsViewModel,
  PrismaTripleAppChartsViewModel
} from "../../../../../shared/prisma-charts/prismaChartContracts";
import type { LabChartDataStatus } from "./chart-lab-types";

type RuntimeSnapshotMeta = {
  runtimeReady?: boolean;
  sourceMode?: string;
  dataStatus?: string;
  generatedAt?: string;
  databasePaths?: Record<string, string | null>;
  warnings?: string[];
  evidence?: string[];
  discovery?: Record<string, unknown>;
};

type RuntimeSnapshot = Partial<PrismaTripleAppChartsViewModel> & {
  meta?: RuntimeSnapshotMeta;
};

const runtimeSnapshot = runtimeSnapshotJson as unknown as RuntimeSnapshot;

function isRuntimeSourceMode(sourceMode: string | undefined) {
  return sourceMode === "sqlite-runtime";
}

function isLabRuntimeDataStatus(value: string | undefined): value is LabChartDataStatus {
  return value === "shared/mock"
    || value === "partial/adapter-ready"
    || value === "runtime"
    || value === "stale"
    || value === "invalid";
}

function hasUsableRuntimeSnapshot(snapshot: RuntimeSnapshot): snapshot is RuntimeSnapshot & {
  pc: Partial<PrismaPcChartsViewModel>;
  tablet: Partial<PrismaTabletChartsViewModel>;
  mobile: Partial<PrismaMobileChartsViewModel>;
} {
  return snapshot.schemaVersion === "1.0" && snapshot.meta?.runtimeReady === true && isRuntimeSourceMode(snapshot.meta?.sourceMode);
}

export const chartRuntimeSnapshotAvailable = hasUsableRuntimeSnapshot(runtimeSnapshot);
const hasRuntimeGovernanceSource = chartRuntimeSnapshotAvailable
  && Boolean(runtimeSnapshot.meta?.databasePaths?.pc || runtimeSnapshot.meta?.databasePaths?.canonical);

export const runtimePcCharts: PrismaPcChartsViewModel = chartRuntimeSnapshotAvailable
  ? ({ ...mockPcCharts, ...(runtimeSnapshot.pc ?? {}) } as PrismaPcChartsViewModel)
  : mockPcCharts;

export const runtimeTabletCharts: PrismaTabletChartsViewModel = chartRuntimeSnapshotAvailable
  ? ({ ...mockTabletCharts, ...(runtimeSnapshot.tablet ?? {}) } as PrismaTabletChartsViewModel)
  : mockTabletCharts;

export const runtimeMobileCharts: PrismaMobileChartsViewModel = chartRuntimeSnapshotAvailable
  ? ({ ...mockMobileCharts, ...(runtimeSnapshot.mobile ?? {}) } as PrismaMobileChartsViewModel)
  : mockMobileCharts;

const snapshotDataStatus = isLabRuntimeDataStatus(runtimeSnapshot.meta?.dataStatus)
  ? runtimeSnapshot.meta?.dataStatus
  : undefined;

export const chartRuntimeDataStatus: LabChartDataStatus = runtimeSnapshot.schemaVersion !== "1.0"
  ? "invalid"
  : chartRuntimeSnapshotAvailable
    ? snapshotDataStatus ?? (hasRuntimeGovernanceSource ? "runtime" : "partial/adapter-ready")
    : runtimeSnapshot.meta?.sourceMode === "mock-fallback"
      ? "shared/mock"
      : "invalid";

export const chartRuntimeFreshnessLabel = chartRuntimeDataStatus === "invalid"
  ? "Invalid Chart Lab runtime snapshot metadata; charts fall back to shared deterministic mocks and no browser DB access is used."
  : chartRuntimeSnapshotAvailable
    ? hasRuntimeGovernanceSource
      ? `SQLite runtime snapshot generated ${runtimeSnapshot.meta?.generatedAt ?? runtimeSnapshot.generatedAt ?? "unknown"} from read-only local DB sources; no browser DB access.`
      : `SQLite runtime snapshot generated ${runtimeSnapshot.meta?.generatedAt ?? runtimeSnapshot.generatedAt ?? "unknown"} from read-only Tablet SQLite; PC/canonical DB are optional and currently unknown, so PC/Mobile charts are partial adapter-ready derivatives; no browser DB access.`
    : "Shared deterministic mock; run tools/prisma/prisma_chart_runtime_snapshot.py --collect-only to refresh a local SQLite runtime snapshot.";
