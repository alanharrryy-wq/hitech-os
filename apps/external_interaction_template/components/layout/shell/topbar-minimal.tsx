"use client";

import Link from "next/link";
import { Search } from "lucide-react";

import { Button } from "@components/ui/button";
import { Input } from "@components/ui/input";
import { RoundSvgIcon } from "@components/ui/round-svg-icon";
import { Select } from "@components/ui/select";
import type { ActionSlotPayload } from "@/lib/ui/shell-system";
import type { UiThemeDefinition, UiThemeId } from "@/lib/ui/theme-system";
import { cn } from "@/lib/utils";

export function TopbarMinimal({
  locale,
  locales,
  onLocaleChange,
  themeId,
  onThemeChange,
  themes,
  contextActions,
  onToggleUtilityDrawer,
  t
}: {
  locale: "es" | "en";
  locales: readonly ("es" | "en")[];
  onLocaleChange: (locale: "es" | "en") => void;
  themeId: UiThemeId;
  onThemeChange: (themeId: UiThemeId) => void;
  themes: readonly UiThemeDefinition[];
  contextActions?: ActionSlotPayload;
  onToggleUtilityDrawer: () => void;
  t: (key: string) => string;
}) {
  return (
    <header className="topbar-minimal">
      <div className="topbar-left">
        <form action="/inbox" method="get" className="topbar-search-form">
          <Search className="topbar-search-icon" />
          <Input
            name="q"
            type="search"
            className="topbar-search-input"
            placeholder={t("shell.searchPlaceholder")}
            aria-label={t("shell.searchPlaceholder")}
          />
        </form>

        <div className="topbar-select-cluster">
          <span className="topbar-label">{t("shell.language")}</span>
          <div className="topbar-toggle-line">
            {locales.map((item) => (
              <button
                key={item}
                type="button"
                className={cn("topbar-toggle", item === locale && "topbar-toggle-active")}
                onClick={() => onLocaleChange(item)}
              >
                {item.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="topbar-select-cluster">
          <span className="topbar-label">{t("shell.theme")}</span>
          <Select
            value={themeId}
            onChange={(event) => onThemeChange(event.target.value as UiThemeId)}
            className="h-8 min-w-[156px] px-2.5 text-[10px] font-semibold uppercase tracking-[0.08em]"
          >
            {themes.map((entry) => (
              <option key={entry.id} value={entry.id}>
                {t(entry.labelKey)}
              </option>
            ))}
          </Select>
        </div>
      </div>

      <div className="topbar-right">
        {contextActions?.items?.map((action) => (
          <Link key={action.id} href={action.href ?? "#"} className={cn("topbar-action", action.variant === "primary" && "topbar-action-primary")}>
            {action.iconName ? (
              <RoundSvgIcon
                name={action.iconName}
                family={action.iconFamily ?? "system"}
                themeId={themeId}
                size={14}
              />
            ) : null}
            <span>{t(action.labelKey)}</span>
          </Link>
        ))}
        <Button variant="ghost" size="sm" className="topbar-utility-btn" onClick={onToggleUtilityDrawer}>
          <RoundSvgIcon name="utilities" family="system" themeId={themeId} size={14} />
          <span>{t("shell.actions.utilities")}</span>
        </Button>
      </div>
    </header>
  );
}
