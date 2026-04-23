import Link from "next/link";
import { ArrowUpRight, RotateCcw } from "lucide-react";

import { Button } from "@components/ui/button";
import { RoundSvgIcon } from "@components/ui/round-svg-icon";

export function FlowSummaryStrip({
  schemaId,
  schemaTitle,
  schemaSummary,
  accessModeLabel,
  stepCount,
  allowDrafts,
  t
}: {
  schemaId: string;
  schemaTitle: string;
  schemaSummary: string;
  accessModeLabel: string;
  stepCount: number;
  allowDrafts: boolean;
  t: (key: string, values?: Record<string, string | number>) => string;
}) {
  return (
    <header className="flow-summary-strip surface-shell">
      <div className="flow-summary-strip-head">
        <div className="flow-summary-strip-kicker">
          <span className="flow-summary-strip-kicker-icon">
            <RoundSvgIcon name="workflow" family="system" size={15} />
          </span>
          <span className="eyebrow">{t("flow.page.eyebrow")}</span>
        </div>
        <h1 className="flow-summary-strip-title">{schemaTitle}</h1>
        <p className="flow-summary-strip-description">{schemaSummary}</p>
        <div className="flow-summary-strip-chips">
          <span className="shell-chip">{t("flow.page.accessChip", { value: accessModeLabel })}</span>
          <span className="shell-chip">{t("flow.page.stepsChip", { count: stepCount })}</span>
          <span className="shell-chip">
            {t(allowDrafts ? "flow.page.draftsChipEnabled" : "flow.page.draftsChipDisabled")}
          </span>
        </div>
      </div>

      <div className="flow-summary-strip-actions">
        <Link href={`/flow/${schemaId}`}>
          <Button variant="ghost" size="sm">
            <RotateCcw className="h-4 w-4" />
            {t("flow.page.newSession")}
          </Button>
        </Link>
        <Link href="/inbox">
          <Button variant="secondary" size="sm">
            <ArrowUpRight className="h-4 w-4" />
            {t("flow.page.openInbox")}
          </Button>
        </Link>
      </div>
    </header>
  );
}
