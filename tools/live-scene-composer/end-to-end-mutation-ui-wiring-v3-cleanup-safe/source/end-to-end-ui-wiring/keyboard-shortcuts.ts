import type { SelectionContext, SurfaceActionEnvelope } from "./contracts";

export interface KeyboardShortcutMatch {
  readonly handled: boolean;
  readonly action?: SurfaceActionEnvelope;
}

function makeAction(context: SelectionContext, type: SurfaceActionEnvelope["type"]): SurfaceActionEnvelope {
  return {
    actionId: `hotkeys-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    surface: "hotkeys",
    type,
    context,
    target: { kind: "draft", sceneId: context.selection.sceneId, draftRevision: context.draftRevision },
    payload: { fromSurface: "hotkeys", keymap: "default" },
    previewPreferred: false,
    commitIntent: type === "hotkey-commit",
    requestedAtUtc: new Date().toISOString(),
    tags: ["hotkeys", type]
  };
}

export function resolveKeyboardShortcut(context: SelectionContext, key: string): KeyboardShortcutMatch {
  switch (key) {
    case "Enter":
      return { handled: true, action: makeAction(context, "hotkey-commit") };
    case "Escape":
      return { handled: true, action: makeAction(context, "hotkey-discard") };
    case "Delete":
    case "Backspace":
      return { handled: true, action: makeAction(context, "hotkey-reset-selected-element") };
    default:
      return { handled: false };
  }
}
