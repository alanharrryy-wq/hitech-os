"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { AppShell } from "@components/layout/app-shell";
import { LanguageProvider } from "@/lib/i18n/provider";
import { useAccessibilitySignals } from "@/lib/ui/use-accessibility-signals";

export function AppFrame({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const accessibility = useAccessibilitySignals();

  return (
    <LanguageProvider>
      <AppShell currentPath={pathname} accessibility={accessibility}>
        {children}
      </AppShell>
    </LanguageProvider>
  );
}
