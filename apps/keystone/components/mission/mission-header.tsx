"use client";

import Link from "next/link";
import { Badge, Button, IconButton, Input, Separator } from "@hitech/ui-kit";
import { useMemo } from "react";
import { useKeystoneUiStore } from "../../lib/store/ui-store";

export interface MissionHeaderProps {
  readonly totalRuns: number;
  readonly runningRuns: number;
}

export function MissionHeader({ totalRuns, runningRuns }: MissionHeaderProps) {
  const sidebarOpen = useKeystoneUiStore((state) => state.sidebarOpen);
  const toggleSidebar = useKeystoneUiStore((state) => state.toggleSidebar);
  const themeMode = useKeystoneUiStore((state) => state.themeMode);
  const setThemeMode = useKeystoneUiStore((state) => state.setThemeMode);

  const modeLabel = useMemo(() => {
    if (themeMode === "system") {
      return "System";
    }

    if (themeMode === "light") {
      return "Light";
    }

    return "Dark";
  }, [themeMode]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="keystone-kicker">Mission Control</p>
          <h1 className="m-0 text-2xl font-semibold tracking-tight text-[hsl(var(--ui-text-1))]">
            Keystone Mission Control
          </h1>
          <p className="m-0 mt-1 text-sm keystone-muted">
            Web-first neutral shell. Contracts validated at runtime.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="accent">{runningRuns} running</Badge>
          <Badge tone="neutral">{totalRuns} total runs</Badge>
          <Link
            href="/pitch"
            className="inline-flex h-9 items-center rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-2))] px-3 text-sm font-medium text-[hsl(var(--ui-text-2))] transition-colors hover:bg-[hsl(var(--ui-surface-2))]"
          >
            Pitch
          </Link>
          <Button variant="outline" onClick={toggleSidebar}>
            {sidebarOpen ? "Hide Sidebar" : "Show Sidebar"}
          </Button>
          <Button
            variant="subtle"
            onClick={() => {
              const next =
                themeMode === "system" ? "light" : themeMode === "light" ? "dark" : "system";
              setThemeMode(next);
            }}
          >
            Theme: {modeLabel}
          </Button>
          <IconButton label="Refresh" onClick={() => window.location.reload()}>
            R
          </IconButton>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <div className="w-full max-w-xs">
          <Input
            placeholder="Search runs, activity or widgets"
            aria-label="Search mission control"
          />
        </div>
        <Separator className="hidden md:block md:w-px md:h-8" orientation="vertical" />
        <p className="m-0 text-xs keystone-muted">
          Progressive enhancement hooks ready. FX overlays remain disabled by default.
        </p>
      </div>
    </div>
  );
}
