"use client";

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PropsWithChildren
} from "react";
import {
  clampLayout,
  clampWindowEntry,
  getViewportBounds
} from "./clamp";
import { buildBuiltinPresets, findBuiltinPreset, isBuiltinPreset } from "./presets";
import {
  loadActiveLayout,
  loadCustomPresets,
  loadLastPreset,
  loadLegacyLayoutOnce,
  parseLayoutJson,
  saveActiveLayout,
  saveCustomPresets,
  saveLastPreset,
  stringifyLayout
} from "./storage";
import {
  WINDOW_LAYOUT_VERSION,
  type LayoutImportResult,
  type WindowLayout,
  type WindowLayoutEntry,
  type WindowManagerContextValue,
  type WindowManagerState,
  type WindowPreset,
  type WindowRegistration
} from "./types";

const DEFAULT_PRESET = "debug";

const FALLBACK_WINDOW_STATE: WindowLayoutEntry = {
  x: 24,
  y: 24,
  w: 420,
  h: 300,
  z: 1000,
  visible: true,
  collapsed: false
};

function normalizePresetId(raw: string): string {
  return raw.trim().toLowerCase().replace(/[^a-z0-9-_]+/g, "-").replace(/--+/g, "-").replace(/^-|-$/g, "");
}

function nextZ(windows: Record<string, WindowLayoutEntry>): number {
  const maxZ = Object.values(windows).reduce((highest, entry) => Math.max(highest, entry.z), 1000);
  return maxZ + 1;
}

function buildClampOptions(registration?: Pick<WindowRegistration, "minWidth" | "minHeight">) {
  const options: { minWidth?: number; minHeight?: number } = {};

  if (registration?.minWidth !== undefined) {
    options.minWidth = registration.minWidth;
  }

  if (registration?.minHeight !== undefined) {
    options.minHeight = registration.minHeight;
  }

  return options;
}

function getPresetWindows(
  state: Pick<WindowManagerState, "activePreset" | "viewport" | "customPresets">
): Record<string, Partial<WindowLayoutEntry>> {
  const custom = state.customPresets[state.activePreset];
  if (custom) {
    return custom.windows;
  }

  const builtin = findBuiltinPreset(state.activePreset, state.viewport);
  return builtin?.windows ?? {};
}

function buildInitialState(): WindowManagerState {
  const viewport = getViewportBounds();
  const activeLayout = loadActiveLayout();
  const customPresets = loadCustomPresets();
  const legacyLayout = activeLayout ? null : loadLegacyLayoutOnce();
  const loadedLayout = activeLayout ?? legacyLayout;

  const preferredPreset = loadedLayout?.preset ?? loadLastPreset() ?? DEFAULT_PRESET;
  const activePreset = preferredPreset.trim().length > 0 ? preferredPreset : DEFAULT_PRESET;

  const windows = loadedLayout
    ? clampLayout(loadedLayout, viewport).windows
    : {};

  return {
    activePreset,
    windows,
    registrations: {},
    mountCounts: {},
    snapPreview: null,
    customPresets,
    viewport
  };
}

function resolveWindowState(
  state: WindowManagerState,
  registration: WindowRegistration
): WindowLayoutEntry {
  const existing = state.windows[registration.id];
  if (existing) {
    return clampWindowEntry(existing, state.viewport, buildClampOptions(registration));
  }

  const presetWindows = getPresetWindows(state);
  const presetPatch = presetWindows[registration.id] ?? {};

  const baseOffset = Object.keys(state.windows).length * 22;
  const fallback: WindowLayoutEntry = {
    ...FALLBACK_WINDOW_STATE,
    x: FALLBACK_WINDOW_STATE.x + baseOffset,
    y: FALLBACK_WINDOW_STATE.y + baseOffset,
    z: nextZ(state.windows)
  };

  const seeded: WindowLayoutEntry = {
    ...fallback,
    ...(registration.defaultState ?? {}),
    ...presetPatch
  };

  return clampWindowEntry(seeded, state.viewport, buildClampOptions(registration));
}

function mergeEntry(
  base: WindowLayoutEntry,
  patch: Partial<WindowLayoutEntry>,
  registration: WindowRegistration | undefined,
  viewport: WindowManagerState["viewport"]
): WindowLayoutEntry {
  return clampWindowEntry(
    {
      ...base,
      ...patch
    },
    viewport,
    buildClampOptions(registration)
  );
}

function buildLayoutSnapshot(state: WindowManagerState): WindowLayout {
  return {
    version: WINDOW_LAYOUT_VERSION,
    preset: state.activePreset,
    windows: state.windows
  };
}

function applyPresetToState(state: WindowManagerState, presetId: string): WindowManagerState {
  const normalizedPreset = presetId.trim().length > 0 ? presetId : DEFAULT_PRESET;
  const builtinPresets = buildBuiltinPresets(state.viewport);
  const builtin = builtinPresets.find((preset) => preset.id === normalizedPreset);
  const custom = state.customPresets[normalizedPreset];

  const presetWindows = custom?.windows ?? builtin?.windows ?? {};

  const allWindowIds = new Set<string>([
    ...Object.keys(state.windows),
    ...Object.keys(state.registrations),
    ...Object.keys(presetWindows)
  ]);

  const nextWindows: Record<string, WindowLayoutEntry> = {};

  for (const windowId of allWindowIds) {
    const registration = state.registrations[windowId];
    const base = state.windows[windowId] ??
      resolveWindowState(
        {
          ...state,
          activePreset: normalizedPreset
        },
        {
          id: windowId,
          title: registration?.title ?? windowId,
          ...(registration?.defaultState !== undefined ? { defaultState: registration.defaultState } : {}),
          ...(registration?.minWidth !== undefined ? { minWidth: registration.minWidth } : {}),
          ...(registration?.minHeight !== undefined ? { minHeight: registration.minHeight } : {}),
          ...(registration?.singleInstance !== undefined
            ? { singleInstance: registration.singleInstance }
            : {})
        }
      );

    const patch = presetWindows[windowId] ?? {};

    nextWindows[windowId] = mergeEntry(base, patch, registration, state.viewport);
  }

  return {
    ...state,
    activePreset: normalizedPreset,
    windows: nextWindows,
    snapPreview: null
  };
}

export const WindowManagerContext = createContext<WindowManagerContextValue | null>(null);

export function WindowManagerProvider({ children }: PropsWithChildren) {
  const [state, setState] = useState<WindowManagerState>(() => buildInitialState());
  const isHydratingRef = useRef(true);

  useEffect(() => {
    isHydratingRef.current = false;
  }, []);

  useEffect(() => {
    const onResize = () => {
      setState((previous) => {
        const viewport = getViewportBounds();
        if (viewport.width === previous.viewport.width && viewport.height === previous.viewport.height) {
          return previous;
        }

        const windows = Object.fromEntries(
          Object.entries(previous.windows).map(([id, entry]) => {
            const registration = previous.registrations[id];
            return [
              id,
              clampWindowEntry(entry, viewport, buildClampOptions(registration))
            ];
          })
        );

        return {
          ...previous,
          viewport,
          windows,
          snapPreview: null
        };
      });
    };

    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
    };
  }, []);

  useEffect(() => {
    if (isHydratingRef.current) {
      return;
    }

    saveActiveLayout(buildLayoutSnapshot(state));
    saveLastPreset(state.activePreset);
  }, [state.activePreset, state.windows]);

  useEffect(() => {
    if (isHydratingRef.current) {
      return;
    }

    saveCustomPresets(state.customPresets);
  }, [state.customPresets]);

  const registerWindow = useCallback((registration: WindowRegistration) => {
    setState((previous) => {
      const mountCount = (previous.mountCounts[registration.id] ?? 0) + 1;
      const nextRegistrations: WindowManagerState["registrations"] = {
        ...previous.registrations,
        [registration.id]: registration
      };

      const nextMountCounts: WindowManagerState["mountCounts"] = {
        ...previous.mountCounts,
        [registration.id]: mountCount
      };

      const currentEntry = previous.windows[registration.id];
      if (currentEntry) {
        return {
          ...previous,
          registrations: nextRegistrations,
          mountCounts: nextMountCounts
        };
      }

      return {
        ...previous,
        registrations: nextRegistrations,
        mountCounts: nextMountCounts,
        windows: {
          ...previous.windows,
          [registration.id]: resolveWindowState(previous, registration)
        }
      };
    });
  }, []);

  const unregisterWindow = useCallback((id: string) => {
    setState((previous) => {
      const current = previous.mountCounts[id] ?? 0;
      const nextCount = Math.max(current - 1, 0);

      const nextMountCounts = { ...previous.mountCounts };
      if (nextCount === 0) {
        delete nextMountCounts[id];
      } else {
        nextMountCounts[id] = nextCount;
      }

      const nextRegistrations = { ...previous.registrations };
      if (nextCount === 0) {
        delete nextRegistrations[id];
      }

      return {
        ...previous,
        mountCounts: nextMountCounts,
        registrations: nextRegistrations,
        snapPreview: previous.snapPreview
      };
    });
  }, []);

  const bringToFront = useCallback((id: string) => {
    setState((previous) => {
      const target = previous.windows[id];
      if (!target) {
        return previous;
      }

      const top = nextZ(previous.windows);
      if (target.z === top) {
        return previous;
      }

      return {
        ...previous,
        windows: {
          ...previous.windows,
          [id]: {
            ...target,
            z: top
          }
        }
      };
    });
  }, []);

  const setWindowState = useCallback((id: string, patch: Partial<WindowLayoutEntry>) => {
    setState((previous) => {
      const target = previous.windows[id];
      if (!target) {
        return previous;
      }

      const registration = previous.registrations[id];
      const next = mergeEntry(target, patch, registration, previous.viewport);

      return {
        ...previous,
        windows: {
          ...previous.windows,
          [id]: next
        }
      };
    });
  }, []);

  const commitWindowState = useCallback((id: string, patch: Partial<WindowLayoutEntry>) => {
    setState((previous) => {
      const target = previous.windows[id];
      if (!target) {
        return previous;
      }

      const registration = previous.registrations[id];
      const merged = mergeEntry(target, patch, registration, previous.viewport);

      return {
        ...previous,
        windows: {
          ...previous.windows,
          [id]: merged
        },
        snapPreview: null
      };
    });
  }, []);

  const setWindowVisible = useCallback((id: string, visible: boolean) => {
    setState((previous) => {
      const target = previous.windows[id];
      if (!target || target.visible === visible) {
        return previous;
      }

      const z = visible ? nextZ(previous.windows) : target.z;

      return {
        ...previous,
        windows: {
          ...previous.windows,
          [id]: {
            ...target,
            visible,
            z
          }
        }
      };
    });
  }, []);

  const toggleWindow = useCallback((id: string) => {
    setState((previous) => {
      const target = previous.windows[id];
      if (!target) {
        return previous;
      }

      const nextVisible = !target.visible;
      return {
        ...previous,
        windows: {
          ...previous.windows,
          [id]: {
            ...target,
            visible: nextVisible,
            z: nextVisible ? nextZ(previous.windows) : target.z
          }
        }
      };
    });
  }, []);

  const setWindowCollapsed = useCallback((id: string, collapsed: boolean) => {
    setState((previous) => {
      const target = previous.windows[id];
      if (!target || target.collapsed === collapsed) {
        return previous;
      }

      return {
        ...previous,
        windows: {
          ...previous.windows,
          [id]: {
            ...target,
            collapsed
          }
        }
      };
    });
  }, []);

  const setSnapPreview = useCallback((candidate: WindowManagerState["snapPreview"]) => {
    setState((previous) => {
      if (!candidate && !previous.snapPreview) {
        return previous;
      }

      if (
        candidate &&
        previous.snapPreview &&
        candidate.x === previous.snapPreview.x &&
        candidate.y === previous.snapPreview.y &&
        candidate.w === previous.snapPreview.w &&
        candidate.h === previous.snapPreview.h &&
        candidate.label === previous.snapPreview.label
      ) {
        return previous;
      }

      return {
        ...previous,
        snapPreview: candidate
      };
    });
  }, []);

  const clearSnapPreview = useCallback(() => {
    setState((previous) => {
      if (!previous.snapPreview) {
        return previous;
      }

      return {
        ...previous,
        snapPreview: null
      };
    });
  }, []);

  const applyPreset = useCallback((presetId: string) => {
    setState((previous) => applyPresetToState(previous, presetId));
  }, []);

  const saveCurrentAsPreset = useCallback((presetId: string) => {
    const normalizedId = normalizePresetId(presetId);

    if (normalizedId.length === 0) {
      return {
        ok: false,
        error: "Preset name is required."
      } as const;
    }

    if (isBuiltinPreset(normalizedId)) {
      return {
        ok: false,
        error: "Built-in preset names are reserved."
      } as const;
    }

    setState((previous) => {
      const customPresets = {
        ...previous.customPresets,
        [normalizedId]: {
          version: WINDOW_LAYOUT_VERSION,
          preset: normalizedId,
          windows: previous.windows
        }
      };

      return {
        ...previous,
        activePreset: normalizedId,
        customPresets
      };
    });

    return { ok: true } as const;
  }, []);

  const removeCustomPreset = useCallback((presetId: string) => {
    if (isBuiltinPreset(presetId)) {
      return;
    }

    setState((previous) => {
      if (!previous.customPresets[presetId]) {
        return previous;
      }

      const customPresets = { ...previous.customPresets };
      delete customPresets[presetId];

      const activePreset = previous.activePreset === presetId ? DEFAULT_PRESET : previous.activePreset;

      return {
        ...previous,
        activePreset,
        customPresets
      };
    });
  }, []);

  const exportLayoutJson = useCallback(() => stringifyLayout(buildLayoutSnapshot(state)), [state]);

  const importLayoutJson = useCallback((raw: string): LayoutImportResult => {
    const parsed = parseLayoutJson(raw);
    if (!parsed) {
      return {
        ok: false,
        error: "Invalid layout JSON or unsupported version."
      };
    }

    setState((previous) => {
      const clamped = clampLayout(parsed, previous.viewport);
      return {
        ...previous,
        activePreset: clamped.preset,
        windows: clamped.windows,
        snapPreview: null
      };
    });

    return {
      ok: true
    };
  }, []);

  const resetLayout = useCallback((presetId?: string) => {
    setState((previous) => applyPresetToState(previous, presetId ?? DEFAULT_PRESET));
  }, []);

  const panicReset = useCallback(() => {
    setState((previous) => applyPresetToState(previous, DEFAULT_PRESET));
  }, []);

  const duplicateWindowIds = useMemo(
    () =>
      Object.entries(state.mountCounts)
        .filter(([, count]) => count > 1)
        .map(([id]) => id)
        .sort((left, right) => left.localeCompare(right)),
    [state.mountCounts]
  );

  const builtinPresets = useMemo<readonly WindowPreset[]>(() => buildBuiltinPresets(state.viewport), [state.viewport]);

  const contextValue = useMemo<WindowManagerContextValue>(
    () => ({
      state,
      builtinPresets,
      registerWindow,
      unregisterWindow,
      bringToFront,
      setWindowState,
      commitWindowState,
      toggleWindow,
      setWindowVisible,
      setWindowCollapsed,
      setSnapPreview,
      clearSnapPreview,
      applyPreset,
      saveCurrentAsPreset,
      removeCustomPreset,
      exportLayoutJson,
      importLayoutJson,
      resetLayout,
      panicReset,
      duplicateWindowIds
    }),
    [
      applyPreset,
      bringToFront,
      builtinPresets,
      clearSnapPreview,
      commitWindowState,
      duplicateWindowIds,
      exportLayoutJson,
      importLayoutJson,
      panicReset,
      registerWindow,
      removeCustomPreset,
      resetLayout,
      saveCurrentAsPreset,
      setSnapPreview,
      setWindowCollapsed,
      setWindowState,
      setWindowVisible,
      state,
      toggleWindow,
      unregisterWindow
    ]
  );

  return <WindowManagerContext.Provider value={contextValue}>{children}</WindowManagerContext.Provider>;
}
