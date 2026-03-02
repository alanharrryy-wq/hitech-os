"use client";

import type { RunsQueryResponse } from "@hitech/contracts";
import {
  Badge,
  EmptyState,
  InsetPanel,
  ScrollArea,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow
} from "@hitech/ui-kit";
import { useKeystoneUiStore } from "../../lib/store/ui-store";

export interface RunsPanelProps {
  readonly data: RunsQueryResponse | undefined;
  readonly isLoading: boolean;
  readonly isError: boolean;
}

function statusTone(status: string): "neutral" | "accent" | "success" | "warning" | "danger" {
  if (status === "running") {
    return "accent";
  }
  if (status === "succeeded") {
    return "success";
  }
  if (status === "failed") {
    return "danger";
  }
  if (status === "paused") {
    return "warning";
  }
  return "neutral";
}

export function RunsPanel({ data, isLoading, isError }: RunsPanelProps) {
  const selectedRunId = useKeystoneUiStore((state) => state.selectedRunId);
  const setSelectedRunId = useKeystoneUiStore((state) => state.setSelectedRunId);

  if (isError) {
    return (
      <EmptyState
        title="Runs unavailable"
        description="Runs endpoint returned an error. Check contracts or API route."
      />
    );
  }

  if (isLoading) {
    return (
      <InsetPanel title="Runs" description="Loading deterministic run fixtures">
        <p className="m-0 text-sm keystone-muted">Loading run summaries...</p>
      </InsetPanel>
    );
  }

  const items = data?.items ?? [];

  if (items.length === 0) {
    return (
      <EmptyState title="No runs" description="No run data available in current fixture set." />
    );
  }

  return (
    <InsetPanel title="Runs" description="Deterministic list from contract fixtures">
      <ScrollArea className="h-[320px]">
        <div className="overflow-x-auto">
          <Table className="min-w-[34rem] sm:min-w-0">
            <TableHead>
              <TableRow>
                <TableHeaderCell>Run</TableHeaderCell>
                <TableHeaderCell>Status</TableHeaderCell>
                <TableHeaderCell className="hidden sm:table-cell">Priority</TableHeaderCell>
                <TableHeaderCell>Progress</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((run) => {
                const selected = selectedRunId === run.id;
                return (
                  <TableRow
                    key={run.id}
                    className={selected ? "bg-[hsl(var(--ui-accent-soft))]" : ""}
                    onClick={() => {
                      setSelectedRunId(run.id);
                    }}
                  >
                    <TableCell>
                      <div className="min-w-0">
                        <p className="m-0 truncate text-sm font-medium">{run.name}</p>
                        <p className="m-0 max-w-[14rem] truncate text-xs keystone-muted sm:max-w-none">
                          {run.id}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge tone={statusTone(run.status)}>{run.status}</Badge>
                    </TableCell>
                    <TableCell className="hidden sm:table-cell">
                      <span className="text-sm">{run.priority}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{run.progress.percent.toFixed(1)}%</span>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </ScrollArea>
    </InsetPanel>
  );
}
