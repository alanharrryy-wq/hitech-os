import type { PrismaMobileSnapshotPayload } from "../prisma-mobile-snapshot-contract";

export function mapSnapshotToHomeViewModel(snapshot: PrismaMobileSnapshotPayload) {
  return {
    meta: snapshot.meta,
    today: snapshot.today,
    heroChart: snapshot.chartViewModels.find((chart) => chart.chartKey === "operational-health-gauge") ?? null,
    primaryAction: snapshot.actionInbox.primaryAction,
    sourceStatus: snapshot.dataQuality.sources,
    recentTimeline: snapshot.timeline.slice(0, 3)
  };
}

export function mapSnapshotToAlertsViewModel(snapshot: PrismaMobileSnapshotPayload) {
  return {
    alertCenter: snapshot.alertCenter,
    severityChart: snapshot.chartViewModels.find((chart) => chart.chartKey === "alert-severity-donut") ?? null,
    primaryAction: snapshot.actionInbox.primaryAction
  };
}

export function mapSnapshotToOperationViewModel(snapshot: PrismaMobileSnapshotPayload) {
  return {
    sales: snapshot.sales,
    money: snapshot.money,
    inventory: snapshot.inventory,
    sync: snapshot.sync,
    charts: snapshot.chartViewModels.filter((chart) => [
      "sales-rhythm-hourly",
      "revenue-momentum",
      "inventory-risk-ranking",
      "sync-freshness-outbox",
      "cash-variance-bullet",
      "top-products-ranking"
    ].includes(chart.chartKey))
  };
}

export function mapSnapshotToTimelineViewModel(snapshot: PrismaMobileSnapshotPayload) {
  return { events: snapshot.timeline, charts: snapshot.chartViewModels.filter((chart) => chart.chartKey === "timeline-activity-density") };
}

export function mapSnapshotToHealthRadarViewModel(snapshot: PrismaMobileSnapshotPayload) {
  return {
    healthRadar: snapshot.healthRadar,
    dataQuality: snapshot.dataQuality,
    chart: snapshot.chartViewModels.find((chart) => chart.chartKey === "health-radar-dimensions") ?? null
  };
}

