"use client";

import { RoundSvgIcon } from "@components/ui/round-svg-icon";
import type { WidgetSlotPayload } from "@/lib/ui/shell-system";
import type { UiThemeId } from "@/lib/ui/theme-system";

export function ContextPanel({
  themeId,
  slot,
  t
}: {
  themeId: UiThemeId;
  slot?: WidgetSlotPayload;
  t: (key: string) => string;
}) {
  if (!slot || slot.widgets.length === 0) return null;

  return (
    <aside className="context-panel" aria-label={t("shell.contextPanel")}>
      <p className="context-panel-title">{t("shell.contextPanel")}</p>
      <div className="grid gap-2">
        {slot.widgets.map((widget) => (
          <section key={widget.id} className="context-widget-card">
            <div className="context-widget-head">
              {widget.icon ? (
                <RoundSvgIcon
                  name={widget.icon.name}
                  family={widget.icon.family}
                  themeId={themeId}
                  size={14}
                />
              ) : null}
              <span>{t(widget.titleKey)}</span>
            </div>
            {widget.summaryKey ? <p className="context-widget-summary">{t(widget.summaryKey)}</p> : null}
          </section>
        ))}
      </div>
    </aside>
  );
}

