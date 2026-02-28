"use client";

import { create } from "zustand";
import type { QueryFilters } from "@hitech/contracts";
import { DEFAULT_QUERY_FILTERS } from "@hitech/contracts";

export type ThemeMode = "system" | "light" | "dark";

export interface KeystoneUiState {
  readonly sidebarOpen: boolean;
  readonly selectedRunId: string | null;
  readonly selectedWidgetId: string | null;
  readonly filters: QueryFilters;
  readonly themeMode: ThemeMode;
  readonly setSidebarOpen: (open: boolean) => void;
  readonly toggleSidebar: () => void;
  readonly setSelectedRunId: (runId: string | null) => void;
  readonly setSelectedWidgetId: (widgetId: string | null) => void;
  readonly setFilters: (filters: QueryFilters) => void;
  readonly patchFilters: (patch: Partial<QueryFilters>) => void;
  readonly resetFilters: () => void;
  readonly setThemeMode: (mode: ThemeMode) => void;
}

export const useKeystoneUiStore = create<KeystoneUiState>((set) => ({
  sidebarOpen: true,
  selectedRunId: null,
  selectedWidgetId: null,
  filters: DEFAULT_QUERY_FILTERS,
  themeMode: "system",
  setSidebarOpen: (open) => {
    set({ sidebarOpen: open });
  },
  toggleSidebar: () => {
    set((state) => ({ sidebarOpen: !state.sidebarOpen }));
  },
  setSelectedRunId: (runId) => {
    set({ selectedRunId: runId });
  },
  setSelectedWidgetId: (widgetId) => {
    set({ selectedWidgetId: widgetId });
  },
  setFilters: (filters) => {
    set({ filters });
  },
  patchFilters: (patch) => {
    set((state) => ({
      filters: {
        ...state.filters,
        ...patch,
        sort: {
          ...state.filters.sort,
          ...(patch.sort ?? {})
        },
        pagination: {
          ...state.filters.pagination,
          ...(patch.pagination ?? {})
        }
      }
    }));
  },
  resetFilters: () => {
    set({ filters: DEFAULT_QUERY_FILTERS });
  },
  setThemeMode: (mode) => {
    set({ themeMode: mode });
  }
}));
