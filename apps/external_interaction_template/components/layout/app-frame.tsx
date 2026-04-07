"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { AppShell } from "@components/layout/app-shell";
import { useAccessibilitySignals } from "@/lib/ui/use-accessibility-signals";

export function AppFrame({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const accessibility = useAccessibilitySignals();

  return (
    <AppShell currentPath={pathname} accessibility={accessibility}>
      {children}
    </AppShell>
  );
}
