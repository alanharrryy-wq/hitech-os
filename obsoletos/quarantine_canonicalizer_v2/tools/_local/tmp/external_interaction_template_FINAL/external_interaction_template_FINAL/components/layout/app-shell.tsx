import Link from "next/link";
import { Layers3, ListChecks, Orbit, RefreshCw, Sparkles } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "@components/ui/button";
import { cn, formatHumanLabel } from "@/lib/utils";
import { createRuntimeUiContext, runtimeContrastClass, runtimeDataAttributes, runtimeMotionClass } from "@/lib/ui/runtime";

const links = [
  { href: "/", label: "Launcher", icon: Sparkles },
  { href: "/inbox", label: "Inbox", icon: ListChecks },
  { href: "/sync", label: "Sync", icon: RefreshCw },
  { href: "/playground", label: "Schemas", icon: Layers3 }
];

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
      return "Compact triage mode for fast review, filtering, and queue scanning.";
    case "record":
      return "Decision-ready detail surface with stronger context for actions, timeline, and attachments.";
    case "flow":
      return "Guided completion mode tuned for lower-friction external intake and resume tokens.";
    case "sync":
      return "Operational diagnostics for dispatch jobs, retry loops, and sync visibility.";
    case "system":
      return "Schema playground and system validation surface for different workflow shapes.";
    default:
      return "Cross-surface overview for schema-driven external interaction flows.";
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
  const area = resolveArea(currentPath);
  const runtime = createRuntimeUiContext({
    area,
    motion: accessibility?.motion,
    contrast: accessibility?.contrast
  });

  const chips = [
    { label: "Role", value: formatHumanLabel(runtime.role) },
    { label: "Density", value: formatHumanLabel(runtime.density) },
    { label: "Preset", value: formatHumanLabel(runtime.preset) },
    { label: "Motion", value: formatHumanLabel(runtime.motion) },
    { label: "Contrast", value: formatHumanLabel(runtime.contrast) }
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
        <div className={cn("surface-shell px-3 py-3 sm:px-4 sm:py-4", runtime.brandProfile.surfaceClass, runtime.brandProfile.glowClass)}>
          <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
            <div className="min-w-0 space-y-4">
              <div className="flex min-w-0 items-start gap-4">
                <div className={cn("flex h-12 w-12 shrink-0 items-center justify-center rounded-[20px] border border-accent/20 bg-accent/10 shadow-soft", runtime.brandProfile.accentClass)}>
                  <Orbit className="h-5 w-5" />
                </div>
                <div className="min-w-0 space-y-1.5">
                  <div className="eyebrow">External Interaction Template</div>
                  <div className="truncate text-base font-semibold tracking-[-0.03em] text-heading sm:text-lg">
                    Schema-driven workflow control surface
                  </div>
                  <p className="max-w-3xl text-sm leading-6 text-muted">
                    {areaDescription(area)}
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <span className="shell-chip">Area {formatHumanLabel(area)}</span>
                <span className="shell-chip">Brand {runtime.brandProfile.label}</span>
                <span className="shell-chip">Preset {formatHumanLabel(runtime.preset)}</span>
              </div>
            </div>

            <div className="grid gap-3 xl:justify-items-end">
              <nav className="flex flex-wrap items-center gap-1.5 rounded-[18px] border border-border/70 bg-surface/78 p-1.5 shadow-inset">
                {links.map((entry) => {
                  const Icon = entry.icon;
                  const active = currentPath === entry.href || (entry.href !== "/" && currentPath.startsWith(entry.href));
                  return (
                    <Link
                      key={entry.href}
                      href={entry.href}
                      className={cn(
                        "inline-flex h-10 items-center gap-2 rounded-[14px] border px-3.5 text-sm font-medium transition",
                        active
                          ? "border-strong/80 bg-elevated text-heading shadow-soft"
                          : "border-transparent text-muted hover:border-border/70 hover:bg-white/5 hover:text-heading"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {entry.label}
                    </Link>
                  );
                })}
              </nav>

              <div className="flex flex-wrap items-center gap-2">
                <Link href="/playground">
                  <Button variant="ghost" size="sm">
                    Schema Playground
                  </Button>
                </Link>
                <Link href="/flow/service_request">
                  <Button variant="primary" size="sm">
                    Start Flow
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          <div className="mt-4 grid gap-3 lg:grid-cols-[1.2fr_minmax(0,0.8fr)]">
            <div className="surface-muted p-4">
              <div className="eyebrow">Current surface</div>
              <div className="mt-1 text-base font-semibold tracking-[-0.03em] text-heading">{formatHumanLabel(area)}</div>
              <p className="mt-1 text-sm leading-6 text-muted">
                Tuned for a {formatHumanLabel(runtime.role)} lens with {formatHumanLabel(runtime.density)} density and {formatHumanLabel(runtime.preset)} presentation.
              </p>
            </div>

            <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
              {chips.map((chip) => (
                <div key={chip.label} className="surface-muted px-3 py-3">
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
