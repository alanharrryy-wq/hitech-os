"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { AppShell } from "@components/layout/app-shell";

export function AppFrame({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return <AppShell currentPath={pathname}>{children}</AppShell>;
}
