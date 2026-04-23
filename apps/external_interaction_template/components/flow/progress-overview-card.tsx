import { Sparkles, Workflow } from "lucide-react";

import { StatCard } from "@components/ui/stat-card";
import { StateBadge } from "@components/ui/state-badge";
import { Surface } from "@components/ui/surface";
import { type FlowRunnerContextSnapshot } from "@components/flow/flow-runner";
import { stateDescription } from "@/lib/core/record-view";
import { formatRelativeTime } from "@/lib/utils";

export function ProgressOverviewCard({
  context,
  t
}: {
  context: FlowRunnerContextSnapshot;
  t: (key: string, values?: Record<string, string | number>) => string;
}) {
  return (
    <Surface title={t("flow.route.progress.title")} subtitle={t("flow.route.progress.subtitle")} padding="sm">
      <div className="grid gap-2.5">
        <StatCard
          label={t("flow.runner.sidebar.progress.label")}
          value={`${Math.round(context.progress)}%`}
          meta={t("flow.runner.sidebar.progress.meta", {
            current: context.stepIndex + 1,
            total: context.totalSteps
          })}
          tone="accent"
          icon={<Workflow className="h-5 w-5" />}
        />

        <StatCard
          label={t("flow.runner.sidebar.requiredRemaining.label")}
          value={String(context.remainingRequired)}
          meta={t("flow.runner.sidebar.requiredRemaining.meta")}
          tone={context.remainingRequired === 0 ? "success" : "warning"}
          icon={<Sparkles className="h-5 w-5" />}
        />

        <div className="surface-muted px-3 py-2.5">
          <div className="metric-label">{t("flow.route.progress.activeStep")}</div>
          <div className="mt-1 text-[13px] font-medium text-heading">{context.activeStepTitle}</div>
        </div>

        <div className="surface-muted px-3 py-2.5">
          <div className="metric-label">{t("flow.runner.sidebar.currentState")}</div>
          <div className="mt-2">
            <StateBadge state={context.recordState} />
          </div>
          <div className="mt-1.5 text-sm leading-5 text-muted">{stateDescription(context.recordState)}</div>
        </div>

        <div className="surface-muted px-3 py-2.5">
          <div className="metric-label">{t("flow.runner.sidebar.recordId")}</div>
          <div className="mt-1 break-all text-[13px] text-heading">{context.recordId ?? t("flow.runner.sidebar.recordIdFallback")}</div>
        </div>

        <div className="surface-muted px-3 py-2.5">
          <div className="metric-label">{t("flow.runner.sidebar.resumeToken")}</div>
          <div className="mt-1 break-all text-[13px] text-heading">
            {context.secureToken ?? t("flow.runner.sidebar.resumeTokenFallback")}
          </div>
        </div>

        <div className="surface-muted px-3 py-2.5">
          <div className="metric-label">{t("flow.runner.sidebar.lastSave")}</div>
          <div className="mt-1 text-[13px] text-heading">
            {context.lastSavedAt ? formatRelativeTime(context.lastSavedAt) : t("flow.runner.sidebar.lastSaveFallback")}
          </div>
        </div>
      </div>
    </Surface>
  );
}
