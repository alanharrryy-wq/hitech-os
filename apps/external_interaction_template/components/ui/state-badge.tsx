import { Activity, AlertTriangle, CheckCircle2, Clock3, Rocket } from "lucide-react";
import type { ReactNode } from "react";

import { Badge } from "@components/ui/badge";
import { stateLabel, stateTone } from "@/lib/core/record-view";
import type { RecordState } from "@/lib/core/types";
import { ensureRecordState } from "@/lib/ui/record-contracts";

const stateIcon = {
  draft: <Clock3 className="h-3.5 w-3.5" />,
  submitted: <Activity className="h-3.5 w-3.5" />,
  in_review: <Activity className="h-3.5 w-3.5" />,
  awaiting_update: <AlertTriangle className="h-3.5 w-3.5" />,
  approved: <CheckCircle2 className="h-3.5 w-3.5" />,
  rejected: <AlertTriangle className="h-3.5 w-3.5" />,
  dispatched: <Rocket className="h-3.5 w-3.5" />,
  synced: <CheckCircle2 className="h-3.5 w-3.5" />,
  failed: <AlertTriangle className="h-3.5 w-3.5" />
} satisfies Record<RecordState, ReactNode>;

export interface StateBadgeProps {
  state: RecordState | string;
  className?: string;
  showIcon?: boolean;
}

export function StateBadge({ state, className, showIcon = true }: StateBadgeProps) {
  const safeState = ensureRecordState(state, "draft");

  return (
    <Badge tone={stateTone(safeState)} className={className}>
      {showIcon ? <span className="mr-1 inline-flex shrink-0">{stateIcon[safeState]}</span> : null}
      {stateLabel(safeState)}
    </Badge>
  );
}
