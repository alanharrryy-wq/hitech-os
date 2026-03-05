export const WINDOW_LAYOUT_VERSION = 1 as const;

export type BuiltInLayoutPreset = "debug" | "presentation" | "minimal";

export interface ViewportBounds {
  readonly width: number;
  readonly height: number;
}

export interface WindowGeometry {
  readonly x: number;
  readonly y: number;
  readonly w: number;
  readonly h: number;
}

export interface WindowLayoutEntry extends WindowGeometry {
  readonly z: number;
  readonly visible: boolean;
  readonly collapsed: boolean;
}

export interface WindowLayout {
  readonly version: typeof WINDOW_LAYOUT_VERSION;
  readonly preset: string;
  readonly windows: Record<string, WindowLayoutEntry>;
}

export interface WindowPreset {
  readonly id: string;
  readonly label: string;
  readonly windows: Record<string, Partial<WindowLayoutEntry>>;
}

export interface WindowRegistration {
  readonly id: string;
  readonly title: string;
  readonly defaultState?: Partial<WindowLayoutEntry>;
  readonly minWidth?: number;
  readonly minHeight?: number;
  readonly singleInstance?: boolean;
}

export interface SnapTarget {
  readonly x: number;
  readonly y: number;
  readonly w: number;
  readonly h: number;
  readonly kind: "edge" | "grid";
  readonly label: string;
}

export interface SnapCandidate extends SnapTarget {
  readonly score: number;
}

export interface LayoutImportResult {
  readonly ok: boolean;
  readonly error?: string;
}

export interface WindowManagerState {
  readonly activePreset: string;
  readonly windows: Record<string, WindowLayoutEntry>;
  readonly registrations: Record<string, WindowRegistration>;
  readonly mountCounts: Record<string, number>;
  readonly snapPreview: SnapCandidate | null;
  readonly customPresets: Record<string, WindowLayout>;
  readonly viewport: ViewportBounds;
}

export interface WindowManagerContextValue {
  readonly state: WindowManagerState;
  readonly builtinPresets: readonly WindowPreset[];
  readonly registerWindow: (registration: WindowRegistration) => void;
  readonly unregisterWindow: (id: string) => void;
  readonly bringToFront: (id: string) => void;
  readonly setWindowState: (id: string, patch: Partial<WindowLayoutEntry>) => void;
  readonly commitWindowState: (id: string, patch: Partial<WindowLayoutEntry>) => void;
  readonly toggleWindow: (id: string) => void;
  readonly setWindowVisible: (id: string, visible: boolean) => void;
  readonly setWindowCollapsed: (id: string, collapsed: boolean) => void;
  readonly setSnapPreview: (candidate: SnapCandidate | null) => void;
  readonly clearSnapPreview: () => void;
  readonly applyPreset: (presetId: string) => void;
  readonly saveCurrentAsPreset: (presetId: string) => { readonly ok: boolean; readonly error?: string };
  readonly removeCustomPreset: (presetId: string) => void;
  readonly exportLayoutJson: () => string;
  readonly importLayoutJson: (raw: string) => LayoutImportResult;
  readonly resetLayout: (presetId?: string) => void;
  readonly panicReset: () => void;
  readonly duplicateWindowIds: readonly string[];
}
