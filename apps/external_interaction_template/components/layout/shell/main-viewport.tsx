"use client";

import type { ReactNode } from "react";

import { RoundSvgIcon } from "@components/ui/round-svg-icon";
import type { UiThemeId } from "@/lib/ui/theme-system";
import type { WidgetSlotPayload } from "@/lib/ui/shell-system";

export function MainViewport({
  children,
  themeId,
  quickFiltersSlot,
  t
}: {
  children: ReactNode;
  themeId: UiThemeId;
  quickFiltersSlot?: WidgetSlotPayload;
  t: (key: string) => string;
}) {
  return (
    <div className="main-viewport">
      {quickFiltersSlot && quickFiltersSlot.widgets.length > 0 ? (
        <div className="main-quick-filters" role="region" aria-label="quick filters">
          {quickFiltersSlot.widgets.map((widget) => (
            <span key={widget.id} className="main-quick-filter-chip">
              {widget.icon ? (
                <RoundSvgIcon
                  name={widget.icon.name}
                  family={widget.icon.family}
                  themeId={themeId}
                  size={14}
                />
              ) : null}
              <span>{t(widget.titleKey)}</span>
            </span>
          ))}
        </div>
      ) : null}
      <main className="main-viewport-content">{children}</main>
    </div>
  );
}
