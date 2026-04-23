import { RoundSvgIcon } from "@components/ui/round-svg-icon";
import { Surface } from "@components/ui/surface";

export function SchemaMetaCard({
  categoryLabel,
  accessModeLabel,
  inboundAdapter,
  outboundAdapter,
  tags,
  t
}: {
  categoryLabel: string;
  accessModeLabel: string;
  inboundAdapter: string;
  outboundAdapter: string;
  tags: readonly string[];
  t: (key: string, values?: Record<string, string | number>) => string;
}) {
  return (
    <Surface title={t("flow.route.meta.title")} subtitle={t("flow.route.meta.subtitle")} padding="sm">
      <div className="grid gap-2.5">
        <div className="surface-muted flex items-start gap-2.5 px-3 py-2.5">
          <RoundSvgIcon name="schema" family="system" size={14} className="mt-0.5" />
          <div className="min-w-0">
            <div className="metric-label">{t("flow.route.meta.category")}</div>
            <div className="mt-1 text-[13px] text-heading">{categoryLabel}</div>
          </div>
        </div>

        <div className="surface-muted flex items-start gap-2.5 px-3 py-2.5">
          <RoundSvgIcon name="lock" family="system" size={14} className="mt-0.5" />
          <div className="min-w-0">
            <div className="metric-label">{t("flow.route.meta.access")}</div>
            <div className="mt-1 text-[13px] text-heading">{accessModeLabel}</div>
          </div>
        </div>

        <div className="surface-muted flex items-start gap-2.5 px-3 py-2.5">
          <RoundSvgIcon name="integration" family="system" size={14} className="mt-0.5" />
          <div className="min-w-0">
            <div className="metric-label">{t("flow.route.meta.adapters")}</div>
            <div className="mt-1 grid gap-1 text-[13px] text-heading">
              <span>{t("flow.route.meta.inbound", { value: inboundAdapter })}</span>
              <span>{t("flow.route.meta.outbound", { value: outboundAdapter })}</span>
            </div>
          </div>
        </div>

        <div className="surface-muted flex items-start gap-2.5 px-3 py-2.5">
          <RoundSvgIcon name="layers" family="system" size={14} className="mt-0.5" />
          <div className="min-w-0">
            <div className="metric-label">{t("flow.route.meta.tags")}</div>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {tags.map((tag) => (
                <span key={tag} className="shell-chip">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Surface>
  );
}
