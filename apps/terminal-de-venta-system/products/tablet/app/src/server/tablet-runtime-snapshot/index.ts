import { readRuntimeSnapshotInput } from "./env";
import { readRuntimeSnapshotFromPrisma } from "./queries.prisma";
import { buildTabletRuntimeSnapshot, buildEmptyRuntimeQueryResult } from "./build";
import type { RuntimeSnapshotInput } from "./types";

export async function getTabletRuntimeSnapshot(input: RuntimeSnapshotInput) {
  const queryResult = await readRuntimeSnapshotFromPrisma(input).catch(() => buildEmptyRuntimeQueryResult(input.date));
  return buildTabletRuntimeSnapshot(input, queryResult);
}

export async function getTabletRuntimeSnapshotFromRequest(request: Request) {
  const input = readRuntimeSnapshotInput(new URL(request.url).searchParams);
  return getTabletRuntimeSnapshot(input);
}

export { readRuntimeSnapshotInput } from "./env";
export { buildTabletRuntimeSnapshot, buildEmptyRuntimeQueryResult } from "./build";
export type { RuntimeSnapshotInput, RuntimeSnapshotQueryResult, RuntimeSnapshotBuildResult } from "./types";
