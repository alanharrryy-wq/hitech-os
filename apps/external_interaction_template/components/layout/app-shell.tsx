import Link from "next/link";
import { Layers3, ListChecks, Orbit, RefreshCw, Sparkles } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "@components/ui/button";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Launcher", icon: Sparkles },
  { href: "/inbox", label: "Review", icon: ListChecks },
  { href: "/sync", label: "Sync", icon: RefreshCw },
  { href: "/playground", label: "Playground", icon: Layers3 }
];

export function AppShell({
  children,
  currentPath
}: {
  children: ReactNode;
  currentPath: string;
}) {
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-3 pb-8 pt-4 sm:px-5 lg:px-8">
      <header className="sticky top-3 z-20 mb-4 rounded-2xl border border-white/10 bg-surface/55 p-2 backdrop-blur-xl shadow-glass">
        <div className="flex flex-wrap items-center gap-2">
          <div className="mr-1 flex items-center gap-2 rounded-xl bg-canvas/55 px-3 py-2">
            <Orbit className="h-4 w-4 text-accent" />
            <div className="text-[11px] uppercase tracking-[0.14em] text-muted">External Interaction Template</div>
          </div>
          <nav className="flex flex-wrap items-center gap-1.5">
            {links.map((entry) => {
              const Icon = entry.icon;
              const active = currentPath === entry.href || (entry.href !== "/" && currentPath.startsWith(entry.href));
              return (
                <Link
                  key={entry.href}
                  href={entry.href}
                  className={cn(
                    "inline-flex h-9 items-center gap-2 rounded-lg border px-3 text-sm transition",
                    active
                      ? "border-accent/30 bg-accent/14 text-accent"
                      : "border-transparent bg-transparent text-muted hover:border-white/10 hover:bg-surface/60 hover:text-text"
                  )}
                >
                  <Icon className="h-3.5 w-3.5" />
                  {entry.label}
                </Link>
              );
            })}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <Link href="/playground">
              <Button variant="ghost" className="h-8 px-2.5 text-xs">
                Schemas
              </Button>
            </Link>
            <Link href="/flow/service_request">
              <Button variant="primary" className="h-8 px-3 text-xs">
                Start Flow
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">{children}</main>
    </div>
  );
}
