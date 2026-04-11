"use client";

import Link from "next/link";
import { Languages, Layers3, ListChecks, Orbit, RefreshCw, Sparkles } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "@components/ui/button";
import { useLanguage } from "@/lib/i18n/use-language";
import { cn } from "@/lib/utils";
import { createRuntimeUiContext, runtimeContrastClass, runtimeDataAttributes, runtimeMotionClass } from "@/lib/ui/runtime";

const links = [
  { href: "/", labelKey: "shell.nav.launcher", icon: Sparkles },
  { href: "/inbox", labelKey: "shell.nav.inbox", icon: ListChecks },
  { href: "/sync", labelKey: "shell.nav.sync", icon: RefreshCw },
  { href: "/playground", labelKey: "shell.nav.schemas", icon: Layers3 }
] as const;

function resolveArea(currentPath: string) {
  if (currentPath.startsWith("/inbox")) return "inbox" as const;
  if (currentPath.startsWith("/record/")) return "record" as const;
  if (currentPath.startsWith("/flow/")) return "flow" as const;
  if (currentPath.startsWith("/sync")) return "sync" as const;
  if (currentPath.startsWith("/playground")) return "system" as const;
  return "launcher" as const;
}

function areaDescription(area: ReturnType<typeof resolveArea>) {
  switch (area) {
    case "inbox":
      return "shell.areaDescription.inbox";
    case "record":
      return "shell.areaDescription.record";
    case "flow":
      return "shell.areaDescription.flow";
    case "sync":
      return "shell.areaDescription.sync";
    case "system":
      return "shell.areaDescription.system";
    default:
      return "shell.areaDescription.launcher";
  }
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
  const { locale, setLocale, supportedLocales, t } = useLanguage();  const area = resolveArea(currentPath);
  const runtime = createRuntimeUiContext({
    area,
    motion: accessibility?.motion,
    contrast: accessibility?.contrast
  });

  const chips = [
    { label: t("shell.chips.role"), value: t(`runtime.role.${runtime.role}`) },
    { label: t("shell.chips.density"), value: t(`runtime.density.${runtime.density}`) },
    { label: t("shell.chips.preset"), value: t(`runtime.preset.${runtime.preset}`) },
    { label: t("shell.chips.motion"), value: t(`runtime.motion.${runtime.motion}`) },
    { label: t("shell.chips.contrast"), value: t(`runtime.contrast.${runtime.contrast}`) }
  ];

  return (
    <div
      {...runtimeDataAttributes(runtime)}
      className={cn(
        "mx-auto flex min-h-screen w-full max-w-[1440px] flex-col px-3 pb-10 pt-4 sm:px-5 lg:px-8",
        runtimeContrastClass(runtime),
        runtimeMotionClass(runtime)
      )}
    >
      <header className="sticky top-4 z-30 mb-6">
        <div className={cn("surface-shell px-3 py-2.5 sm:px-4 sm:py-3", runtime.brandProfile.surfaceClass, runtime.brandProfile.glowClass)}>
          <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
            <div className="min-w-0 space-y-3">
              <div className="flex min-w-0 items-start gap-4">
                <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-[18px] border border-accent/20 bg-accent/10 shadow-soft", runtime.brandProfile.accentClass)}>
                  <Orbit className="h-5 w-5" />
                </div>
                <div className="min-w-0 space-y-1">
                  <div className="eyebrow">{t("shell.eyebrow")}</div>
                  <div className="truncate text-base font-semibold tracking-[-0.03em] text-heading sm:text-lg">
                    {t("shell.title")}
                  </div>
                  <p className="max-w-3xl text-sm leading-5 text-muted">
                    {t(areaDescription(area))}
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <span className="shell-chip">{t("shell.chips.area")} {t(`shell.area.${area}`)}</span>
                <span className="shell-chip">{t("shell.chips.brand")} {runtime.brandProfile.label}</span>
                <span className="shell-chip">{t("shell.chips.preset")} {t(`runtime.preset.${runtime.preset}`)}</span>
              </div>
            </div>

            <div className="grid gap-2 xl:justify-items-end">
              <div className="flex flex-wrap items-center justify-end gap-2">
                <div className="flex items-center gap-2 rounded-[18px] border border-border/70 bg-surface/78 px-2 py-1 shadow-inset">
                  <Languages className="h-4 w-4 text-muted" />
                  <span className="text-xs font-medium uppercase tracking-[0.14em] text-subtle">{t("shell.language")}</span>
                  <div className="flex items-center gap-1">
                    {supportedLocales.map((entry) => (
                      <button
                        key={entry}
                        type="button"
                        onClick={() => setLocale(entry)}
                        className={cn(
                          "rounded-full px-2 py-1 text-[11px] font-semibold uppercase transition",
                          locale === entry ? "bg-accent/18 text-accent" : "text-muted hover:bg-white/8 hover:text-heading"
                        )}
                        aria-pressed={locale === entry}
                      >
                        {entry}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <nav className="flex flex-wrap items-center gap-1 rounded-[18px] border border-border/70 bg-surface/78 p-1 shadow-inset">
                {links.map((entry) => {
                  const Icon = entry.icon;
                  const active = currentPath === entry.href || (entry.href !== "/" && currentPath.startsWith(entry.href));
                  return (
                    <Link
                      key={entry.href}
                      href={entry.href}
                      className={cn(
                        "inline-flex h-9 items-center gap-2 rounded-[14px] border px-3 text-[13px] font-medium transition",
                        active
                          ? "border-strong/80 bg-elevated text-heading shadow-soft"
                          : "border-transparent text-muted hover:border-border/70 hover:bg-white/5 hover:text-heading"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {t(entry.labelKey)}
                    </Link>
                  );
                })}
              </nav>

              <div className="flex flex-wrap items-center gap-2">
                <Link href="/playground">
                  <Button variant="ghost" size="sm">
                    {t("shell.actions.playground")}
                  </Button>
                </Link>
                <Link href="/flow/service_request">
                  <Button variant="primary" size="sm">
                    {t("shell.actions.startFlow")}
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          <div className="mt-3 grid gap-2 lg:grid-cols-[1.15fr_minmax(0,0.85fr)]">
            <div className="surface-muted p-3">
              <div className="eyebrow">{t("shell.currentSurface")}</div>
              <div className="mt-1 text-base font-semibold tracking-[-0.03em] text-heading">{t(`shell.area.${area}`)}</div>
              <p className="mt-1 text-sm leading-5 text-muted">
                {t("shell.surfaceSummary", {
                  role: t(`runtime.role.${runtime.role}`),
                  density: t(`runtime.density.${runtime.density}`),
                  preset: t(`runtime.preset.${runtime.preset}`)
                })}
              </p>
            </div>

            <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
              {chips.map((chip) => (
                <div key={chip.label} className="surface-muted px-3 py-2.5">
                  <div className="metric-label">{chip.label}</div>
                  <div className="mt-1 text-sm font-medium text-heading">{chip.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
