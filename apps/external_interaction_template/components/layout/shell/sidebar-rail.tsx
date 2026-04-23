"use client";

import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@components/ui/button";
import { RoundSvgIcon } from "@components/ui/round-svg-icon";
import type {
  ActionSlotPayload,
  BrandSlotPayload,
  FooterSlotPayload,
  NavItemDescriptor,
  NavSlotPayload,
  WorkspaceSlotPayload
} from "@/lib/ui/shell-system";
import type { UiThemeId } from "@/lib/ui/theme-system";
import { cn } from "@/lib/utils";

function renderNavItem({
  item,
  collapsed,
  currentPath,
  themeId,
  t,
  nested = false
}: {
  item: NavItemDescriptor;
  collapsed: boolean;
  currentPath: string;
  themeId: UiThemeId;
  t: (key: string) => string;
  nested?: boolean;
}) {
  const active = currentPath === item.route || (item.route !== "/" && currentPath.startsWith(item.route));
  const hasChildren = Array.isArray(item.children) && item.children.length > 0;

  return (
    <div key={item.id} className={cn("grid gap-1", nested && "pl-2")}>
      <Link
        href={item.route}
        className={cn("sidebar-link", active && "sidebar-link-active", nested && "sidebar-link-nested")}
        title={collapsed ? t(item.tooltip ?? item.labelKey) : undefined}
      >
        <span className="sidebar-link-icon">
          <RoundSvgIcon name={item.iconName} family={item.iconFamily} themeId={themeId} size={16} />
        </span>
        {!collapsed || item.collapsedLabelPolicy === "always" ? (
          <span className="truncate text-[12px] font-medium">{t(item.labelKey)}</span>
        ) : null}
      </Link>
      {hasChildren && !collapsed ? (
        <div className="grid gap-1">
          {item.children!.map((child) =>
            renderNavItem({
              item: child,
              collapsed,
              currentPath,
              themeId,
              t,
              nested: true
            })
          )}
        </div>
      ) : null}
    </div>
  );
}

function renderActionGroup({
  payload,
  t,
  collapsed,
  themeId
}: {
  payload: ActionSlotPayload | undefined;
  t: (key: string) => string;
  collapsed: boolean;
  themeId: UiThemeId;
}) {
  if (!payload || payload.items.length === 0) return null;

  return (
    <div className="sidebar-action-stack">
      {payload.items.map((action) => (
        <Link
          key={action.id}
          href={action.href ?? "#"}
          className={cn("sidebar-action", action.variant === "primary" && "sidebar-action-primary")}
          title={collapsed ? t(action.labelKey) : undefined}
        >
          {action.iconName ? (
            <RoundSvgIcon
              name={action.iconName}
              family={action.iconFamily ?? "system"}
              themeId={themeId}
              size={14}
            />
          ) : null}
          {!collapsed ? <span>{t(action.labelKey)}</span> : null}
        </Link>
      ))}
    </div>
  );
}

export function SidebarRail({
  themeId,
  currentPath,
  collapsed,
  onToggleCollapsed,
  brandSlot,
  workspaceSlot,
  primaryNavSlot,
  secondaryNavSlot,
  quickActionSlot,
  utilitySlot,
  footerSlot,
  t
}: {
  themeId: UiThemeId;
  currentPath: string;
  collapsed: boolean;
  onToggleCollapsed: () => void;
  brandSlot?: BrandSlotPayload;
  workspaceSlot?: WorkspaceSlotPayload;
  primaryNavSlot?: NavSlotPayload;
  secondaryNavSlot?: NavSlotPayload;
  quickActionSlot?: ActionSlotPayload;
  utilitySlot?: ActionSlotPayload;
  footerSlot?: FooterSlotPayload;
  t: (key: string) => string;
}) {
  const brandHref = brandSlot?.href ?? "/";

  return (
    <aside className={cn("sidebar-rail", collapsed && "sidebar-rail-collapsed")}>
      <div className="sidebar-sheen" />

      <div className="sidebar-head">
        {brandSlot ? (
          <Link href={brandHref} className="sidebar-brand" title={collapsed ? brandSlot.label : undefined}>
            <span className="sidebar-brand-badge">
              <RoundSvgIcon
                name={brandSlot.logo?.name ?? "sparkle"}
                family={brandSlot.logo?.family ?? "system"}
                themeId={themeId}
                size={18}
              />
            </span>
            {!collapsed ? (
              <span className="min-w-0">
                <span className="sidebar-brand-title">{brandSlot.label}</span>
                {brandSlot.subtitle ? <span className="sidebar-brand-subtitle">{brandSlot.subtitle}</span> : null}
              </span>
            ) : null}
          </Link>
        ) : null}

        <Button variant="ghost" size="icon" className="sidebar-collapse-btn" onClick={onToggleCollapsed}>
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {workspaceSlot ? (
        <section className="sidebar-workspace">
          {workspaceSlot.icon ? (
            <RoundSvgIcon name={workspaceSlot.icon.name} family={workspaceSlot.icon.family} themeId={themeId} size={16} />
          ) : null}
          {!collapsed ? (
            <div className="min-w-0">
              <p className="sidebar-section-label">{workspaceSlot.title}</p>
              {workspaceSlot.description ? <p className="sidebar-workspace-description">{workspaceSlot.description}</p> : null}
            </div>
          ) : null}
        </section>
      ) : null}

      {primaryNavSlot && primaryNavSlot.items.length > 0 ? (
        <section className="sidebar-section">
          {!collapsed ? <p className="sidebar-section-label">{t("shell.nav.primary")}</p> : null}
          <div className="grid gap-1">
            {primaryNavSlot.items.map((item) =>
              renderNavItem({
                item,
                collapsed,
                currentPath,
                themeId,
                t
              })
            )}
          </div>
        </section>
      ) : null}

      {secondaryNavSlot && secondaryNavSlot.items.length > 0 ? (
        <section className="sidebar-section">
          {!collapsed ? <p className="sidebar-section-label">{t("shell.nav.secondary")}</p> : null}
          <div className="grid gap-1">
            {secondaryNavSlot.items.map((item) =>
              renderNavItem({
                item,
                collapsed,
                currentPath,
                themeId,
                t
              })
            )}
          </div>
        </section>
      ) : null}

      {renderActionGroup({ payload: quickActionSlot, t, collapsed, themeId })}

      <div className="sidebar-spacer" />

      {renderActionGroup({ payload: utilitySlot, t, collapsed, themeId })}

      {footerSlot && !collapsed ? (
        <footer className="sidebar-footer">
          <p>{footerSlot.text}</p>
          {footerSlot.links?.length ? (
            <div className="sidebar-footer-links">
              {footerSlot.links.map((entry) => (
                <Link key={entry.href} href={entry.href}>
                  {entry.label}
                </Link>
              ))}
            </div>
          ) : null}
        </footer>
      ) : null}
    </aside>
  );
}
