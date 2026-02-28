"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState, type PropsWithChildren } from "react";
import { createQueryClient } from "../lib/query-client";
import { useKeystoneUiStore } from "../lib/store/ui-store";

function KeystoneUiBootstrap(): null {
  const themeMode = useKeystoneUiStore((state) => state.themeMode);

  useEffect(() => {
    const root = document.documentElement;
    root.dataset["themeMode"] = themeMode;
  }, [themeMode]);

  return null;
}

export function AppProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(() => createQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <KeystoneUiBootstrap />
      {children}
    </QueryClientProvider>
  );
}
