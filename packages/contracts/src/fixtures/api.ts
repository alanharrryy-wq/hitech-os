import {
  ActivityQueryResponse,
  ActivityQueryResponseSchema,
  RunsQueryResponse,
  RunsQueryResponseSchema,
  WidgetsQueryResponse,
  WidgetsQueryResponseSchema
} from "../mission-control/api.js";
import { parseOrThrow } from "../parsing.js";
import { ACTIVITY_FIXTURES } from "./activity.js";
import { LAYOUT_FIXTURE } from "./layout.js";
import { RUN_FIXTURES } from "./runs.js";
import { WIDGET_FIXTURES } from "./widgets.js";

const META = {
  requestId: "req_0000000001",
  generatedAt: "2026-02-16T05:00:00.000Z",
  contractVersion: "2.0.0"
} as const;

export const RUNS_RESPONSE_FIXTURE: RunsQueryResponse = {
  meta: {
    ...META,
    requestId: "req_runs-000001"
  },
  items: [...RUN_FIXTURES],
  total: RUN_FIXTURES.length,
  page: 1,
  pageSize: 25
};

export const ACTIVITY_RESPONSE_FIXTURE: ActivityQueryResponse = {
  meta: {
    ...META,
    requestId: "req_activity-000001"
  },
  items: [...ACTIVITY_FIXTURES],
  cursor: "activity-cursor-1",
  hasMore: false
};

export const WIDGETS_RESPONSE_FIXTURE: WidgetsQueryResponse = {
  meta: {
    ...META,
    requestId: "req_widgets-000001"
  },
  widgets: [...WIDGET_FIXTURES],
  layout: LAYOUT_FIXTURE
};

export function parseRunsResponseFixture(): RunsQueryResponse {
  return parseOrThrow(RunsQueryResponseSchema, RUNS_RESPONSE_FIXTURE, {
    resource: "api.runs",
    operation: "fixture-parse"
  });
}

export function parseActivityResponseFixture(): ActivityQueryResponse {
  return parseOrThrow(ActivityQueryResponseSchema, ACTIVITY_RESPONSE_FIXTURE, {
    resource: "api.activity",
    operation: "fixture-parse"
  });
}

export function parseWidgetsResponseFixture(): WidgetsQueryResponse {
  return parseOrThrow(WidgetsQueryResponseSchema, WIDGETS_RESPONSE_FIXTURE, {
    resource: "api.widgets",
    operation: "fixture-parse"
  });
}
