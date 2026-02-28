import { QueryFilters, QueryFiltersSchema } from "../mission-control/filters.js";
import { parseOrThrow } from "../parsing.js";

export const FILTER_FIXTURE_DEFAULT: QueryFilters = {
  search: "",
  statuses: [],
  severities: [],
  owners: [],
  tags: [],
  timeRange: null,
  sort: {
    field: "updatedAt",
    direction: "desc"
  },
  pagination: {
    page: 1,
    pageSize: 25
  }
};

export const FILTER_FIXTURE_LAST_24H: QueryFilters = {
  search: "alpha",
  statuses: ["running", "queued"],
  severities: ["warn", "error", "critical"],
  owners: ["usr_ops-0001", "usr_ops-0003"],
  tags: ["build", "nightly"],
  timeRange: {
    type: "relative",
    amount: 24,
    unit: "hours"
  },
  sort: {
    field: "priority",
    direction: "desc"
  },
  pagination: {
    page: 1,
    pageSize: 50
  }
};

export const FILTER_FIXTURE_ABSOLUTE: QueryFilters = {
  search: "queue",
  statuses: ["failed"],
  severities: ["critical"],
  owners: ["usr_queue-0001"],
  tags: ["outage"],
  timeRange: {
    type: "absolute",
    from: "2026-02-11T00:00:00.000Z",
    to: "2026-02-12T00:00:00.000Z"
  },
  sort: {
    field: "createdAt",
    direction: "asc"
  },
  pagination: {
    page: 2,
    pageSize: 10
  }
};

export function parseFilterFixtures(): readonly QueryFilters[] {
  return [FILTER_FIXTURE_DEFAULT, FILTER_FIXTURE_LAST_24H, FILTER_FIXTURE_ABSOLUTE].map((fixture) =>
    parseOrThrow(QueryFiltersSchema, fixture, {
      resource: "filters",
      operation: "fixture-parse"
    })
  );
}
