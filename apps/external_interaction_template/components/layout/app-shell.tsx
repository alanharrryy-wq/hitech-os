"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";

import { ContextPanel, MainViewport, SidebarRail, TopbarMinimal, UtilityDrawer } from "@components/layout/shell";
import { useLanguage } from "@/lib/i18n/use-language";
import { cn } from "@/lib/utils";
import { createRuntimeUiContext, runtimeContrastClass, runtimeDataAttributes, runtimeMotionClass } from "@/lib/ui/runtime";
import { composeShellModel, createShellPermissionsSet } from "@/lib/ui/shell-system";
import {
  DEFAULT_UI_THEME,
  VISIBLE_UI_THEMES,
  UI_THEME_STORAGE_KEY,
  isUiThemeId,
  resolveUiThemeId,
  type UiThemeId
} from "@/lib/ui/theme-catalog";
import { applyThemeToDocument } from "@/lib/ui/theme-system";

const SIDEBAR_COLLAPSE_STORAGE_KEY = "hitech.external_interaction_template.sidebar_collapsed";

function resolveArea(currentPath: string) {
  if (currentPath.startsWith("/inbox")) return "inbox" as const;
  if (currentPath.startsWith("/record/")) return "record" as const;
  if (currentPath.startsWith("/flow/")) return "flow" as const;
  if (currentPath.startsWith("/sync")) return "sync" as const;
  if (currentPath.startsWith("/playground")) return "system" as const;
  return "launcher" as const;
}

function dispatchBrowserEvent(eventName: string, detail: Record<string, string>) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(eventName, { detail }));
}

function resolveBreakpoint(width: number): "desktop" | "tablet" | "mobile" {
  if (width < 900) return "mobile";
  if (width < 1260) return "tablet";
  return "desktop";
}

export function AppShell({
  children,
  currentPath,
  accessibility
}: {
  children: ReactNode;
  currentPath: string;
  accessibility?: { motion?: "full" | "reduced" | "none"; contrast?: "normal" | "more" | "max" };
}) {
  const { locale, setLocale, supportedLocales, t } = useLanguage();
  const area = resolveArea(currentPath);
  const [themeId, setThemeId] = useState<UiThemeId>(DEFAULT_UI_THEME);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [utilityDrawerOpen, setUtilityDrawerOpen] = useState(false);
  const [breakpoint, setBreakpoint] = useState<"desktop" | "tablet" | "mobile">("desktop");

  useEffect(() => {
    try {
      const storedTheme = window.localStorage.getItem(UI_THEME_STORAGE_KEY);
      if (isUiThemeId(storedTheme)) {
        setThemeId(storedTheme);
      }
      setSidebarCollapsed(window.localStorage.getItem(SIDEBAR_COLLAPSE_STORAGE_KEY) === "1");
    } catch {
      // noop
    }
  }, []);

  const runtime = createRuntimeUiContext({
    area,
    motion: accessibility?.motion,
    contrast: accessibility?.contrast
  });

  useEffect(() => {
    applyThemeToDocument(themeId);
    try {
      window.localStorage.setItem(UI_THEME_STORAGE_KEY, themeId);
    } catch {
      // noop
    }
    dispatchBrowserEvent("ui-theme-change", { themeId });
  }, [themeId]);

  useEffect(() => {
    try {
      window.localStorage.setItem(SIDEBAR_COLLAPSE_STORAGE_KEY, sidebarCollapsed ? "1" : "0");
    } catch {
      // noop
    }
  }, [sidebarCollapsed]);

  useEffect(() => {
    const sync = () => setBreakpoint(resolveBreakpoint(window.innerWidth));
    sync();
    window.addEventListener("resize", sync, { passive: true });
    return () => window.removeEventListener("resize", sync);
  }, []);

  useEffect(() => {
    if (typeof document === "undefined") return;

    const root = document.documentElement;
    root.dataset.uiMotion = runtime.motion;
    root.dataset.uiContrast = runtime.contrast;
    dispatchBrowserEvent("ui-motion-change", { motion: runtime.motion });
  }, [runtime.motion, runtime.contrast]);

  const themeOptions = VISIBLE_UI_THEMES;
  const selectorThemeId = themeOptions.some((entry) => entry.id === themeId) ? themeId : DEFAULT_UI_THEME;

  const permissionSet = useMemo(() => createShellPermissionsSet(), []);
  const shellModel = useMemo(
    () =>
      composeShellModel({
        area,
        currentPath,
        locale,
        themeId,
        breakpoint,
        collapsedSidebar: sidebarCollapsed,
        permissions: permissionSet
      }),
    [area, breakpoint, currentPath, locale, permissionSet, sidebarCollapsed, themeId]
  );
  const hasContextPanel = Boolean(shellModel.contextualPanelSlot?.widgets?.length);

  return (
    <div
      {...runtimeDataAttributes(runtime)}
      data-ui-theme={themeId}
      className={cn(
        "relative mx-auto flex min-h-screen w-full max-w-[1600px] flex-col px-3 pb-8 pt-3 sm:px-5 lg:px-6",
        runtimeContrastClass(runtime),
        runtimeMotionClass(runtime)
      )}
    >
      <div className={cn("app-shell-grid", !hasContextPanel && "app-shell-grid-no-context")}>
        <SidebarRail
          themeId={themeId}
          currentPath={currentPath}
          collapsed={sidebarCollapsed}
          onToggleCollapsed={() => setSidebarCollapsed((value) => !value)}
          brandSlot={shellModel.brandSlot}
          workspaceSlot={shellModel.workspaceSlot}
          primaryNavSlot={shellModel.primaryNavSlot}
          secondaryNavSlot={shellModel.secondaryNavSlot}
          quickActionSlot={shellModel.quickActionSlot}
          utilitySlot={shellModel.utilitySlot}
          footerSlot={shellModel.footerSlot}
          t={t}
        />

        <section className="app-shell-main">
          <TopbarMinimal
            locale={locale}
            locales={supportedLocales}
            onLocaleChange={setLocale}
            themeId={selectorThemeId}
            onThemeChange={(nextTheme) => setThemeId(resolveUiThemeId(nextTheme))}
            themes={themeOptions}
            contextActions={shellModel.contextActionSlot}
            onToggleUtilityDrawer={() => setUtilityDrawerOpen((value) => !value)}
            t={t}
          />

          <MainViewport themeId={themeId} quickFiltersSlot={shellModel.quickFiltersSlot} t={t}>
            {children}
          </MainViewport>
        </section>

        {hasContextPanel ? <ContextPanel themeId={themeId} slot={shellModel.contextualPanelSlot} t={t} /> : null}
      </div>

      <UtilityDrawer
        open={utilityDrawerOpen}
        onClose={() => setUtilityDrawerOpen(false)}
        themeId={themeId}
        utilitySlot={shellModel.utilitySlot}
        pluginSlot={shellModel.pluginTraySlot}
        t={t}
      />
    </div>
  );
}
