// PRISMA_CHART_LAB_GUIDED_TOUR_V3
export type ChartLabGuidedTourAction = "highlight" | "showTip" | "downplay" | "hideTip" | "dataZoom" | "restore";
export type ChartLabGuidedTourStep = {
  id: string;
  label: string;
  action: ChartLabGuidedTourAction;
  delayMs: number;
  payload: Record<string, unknown>;
  fallback?: ChartLabGuidedTourAction;
};

export type ChartLabGuidedTour = {
  id: string;
  label: string;
  description: string;
  reducedMotionSafe: boolean;
  steps: ChartLabGuidedTourStep[];
};

export const CHART_LAB_GUIDED_TOURS: Record<string, ChartLabGuidedTour> = {
  "hotspot-narrative": {
    id: "hotspot-narrative",
    label: "Hotspot Narrative",
    description: "Walks the operator through top pressure zones with highlight and tooltip actions.",
    reducedMotionSafe: true,
    steps: [
      { id: "clear", label: "Clear old state", action: "downplay", delayMs: 0, payload: {} },
      { id: "first-hotspot", label: "First hotspot", action: "highlight", delayMs: 240, payload: { seriesIndex: 0, dataIndex: 0 }, fallback: "showTip" },
      { id: "first-tooltip", label: "Show evidence", action: "showTip", delayMs: 520, payload: { seriesIndex: 0, dataIndex: 0 } },
      { id: "second-hotspot", label: "Second hotspot", action: "highlight", delayMs: 980, payload: { seriesIndex: 0, dataIndex: 1 }, fallback: "showTip" },
      { id: "reset", label: "Return to overview", action: "hideTip", delayMs: 1400, payload: {} }
    ]
  },
  "forensic-scan": {
    id: "forensic-scan",
    label: "Forensic Scan",
    description: "Slow evidence scan intended for review and audit demos.",
    reducedMotionSafe: false,
    steps: [
      { id: "restore", label: "Restore overview", action: "restore", delayMs: 0, payload: {} },
      { id: "zoom", label: "Zoom to incident range", action: "dataZoom", delayMs: 400, payload: { start: 25, end: 75 } },
      { id: "tip", label: "Show incident tip", action: "showTip", delayMs: 900, payload: { seriesIndex: 0, dataIndex: 2 } }
    ]
  }
};

export function getChartLabGuidedTour(id: string): ChartLabGuidedTour {
  return CHART_LAB_GUIDED_TOURS[id] ?? CHART_LAB_GUIDED_TOURS["hotspot-narrative"];
}

export function createDispatchActionPlan(tourId: string, reducedMotion: boolean): ChartLabGuidedTourStep[] {
  const tour = getChartLabGuidedTour(tourId);
  if (reducedMotion && !tour.reducedMotionSafe) return CHART_LAB_GUIDED_TOURS["hotspot-narrative"].steps;
  return tour.steps;
}

export function validateGuidedTourContracts(): string[] {
  const errors: string[] = [];
  for (const [id, tour] of Object.entries(CHART_LAB_GUIDED_TOURS)) {
    if (!tour.steps.length) errors.push(`${id}: missing steps`);
    for (const step of tour.steps) {
      if (!step.id) errors.push(`${id}: step missing id`);
      if (step.delayMs < 0) errors.push(`${id}.${step.id}: negative delay`);
      if (!["highlight", "showTip", "downplay", "hideTip", "dataZoom", "restore"].includes(step.action)) errors.push(`${id}.${step.id}: invalid action`);
    }
  }
  return errors;
}
