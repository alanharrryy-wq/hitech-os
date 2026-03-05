"use client";

import { useMemo, useState, type CSSProperties } from "react";
import { useWindowManager } from "./window-manager/useWindowManager";

const ROOT_STYLE: CSSProperties = {
  display: "grid",
  gap: "0.65rem"
};

const ROW_STYLE: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: "0.45rem",
  alignItems: "center"
};

const INPUT_STYLE: CSSProperties = {
  width: "100%",
  border: "1px solid hsl(var(--ui-border-2))",
  borderRadius: "8px",
  padding: "0.42rem 0.55rem",
  background: "hsl(var(--ui-surface-1))",
  color: "hsl(var(--ui-text-1))",
  fontSize: "0.76rem"
};

const BUTTON_STYLE: CSSProperties = {
  border: "1px solid hsl(var(--ui-border-2))",
  borderRadius: "8px",
  padding: "0.35rem 0.6rem",
  fontSize: "0.72rem",
  fontWeight: 650,
  textTransform: "uppercase",
  letterSpacing: "0.04em",
  background: "hsl(var(--ui-surface-2))",
  cursor: "pointer"
};

const STATUS_STYLE: CSSProperties = {
  margin: 0,
  fontSize: "0.72rem",
  color: "hsl(var(--ui-text-3))"
};

async function copyToClipboard(text: string): Promise<boolean> {
  if (typeof navigator !== "undefined" && navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  }

  if (typeof document === "undefined") {
    return false;
  }

  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.opacity = "0";
  document.body.append(textArea);
  textArea.select();
  const copied = document.execCommand("copy");
  textArea.remove();
  return copied;
}

export function ControlRoomToolbar() {
  const {
    state,
    builtinPresets,
    applyPreset,
    saveCurrentAsPreset,
    removeCustomPreset,
    exportLayoutJson,
    importLayoutJson,
    resetLayout,
    toggleWindow
  } = useWindowManager();

  const [customName, setCustomName] = useState("");
  const [importText, setImportText] = useState("");
  const [status, setStatus] = useState("ready");

  const customPresetIds = useMemo(
    () => Object.keys(state.customPresets).sort((left, right) => left.localeCompare(right)),
    [state.customPresets]
  );

  const presetOptions = useMemo(
    () => [
      ...builtinPresets.map((preset) => ({ id: preset.id, label: preset.label })),
      ...customPresetIds.map((id) => ({ id, label: `Custom: ${id}` }))
    ],
    [builtinPresets, customPresetIds]
  );

  const handleExport = async () => {
    const payload = exportLayoutJson();
    const copied = await copyToClipboard(payload);
    setStatus(copied ? "layout copied" : "clipboard unavailable");
  };

  return (
    <div style={ROOT_STYLE}>
      <div style={ROW_STYLE}>
        <label style={{ fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.05em" }} htmlFor="control-room-preset">
          Preset
        </label>
        <select
          id="control-room-preset"
          value={state.activePreset}
          style={INPUT_STYLE}
          onChange={(event) => {
            applyPreset(event.currentTarget.value);
            setStatus(`preset ${event.currentTarget.value} applied`);
          }}
        >
          {presetOptions.map((preset) => (
            <option key={preset.id} value={preset.id}>
              {preset.label}
            </option>
          ))}
        </select>
      </div>

      <div style={ROW_STYLE}>
        <input
          value={customName}
          style={{ ...INPUT_STYLE, width: "180px" }}
          onChange={(event) => setCustomName(event.currentTarget.value)}
          placeholder="custom preset name"
          aria-label="Custom preset name"
        />
        <button
          type="button"
          style={BUTTON_STYLE}
          onClick={() => {
            const result = saveCurrentAsPreset(customName);
            if (!result.ok) {
              setStatus(result.error ?? "could not save preset");
              return;
            }

            setStatus(`preset ${customName} saved`);
            setCustomName("");
          }}
        >
          Save Custom
        </button>

        {customPresetIds.includes(state.activePreset) ? (
          <button
            type="button"
            style={BUTTON_STYLE}
            onClick={() => {
              removeCustomPreset(state.activePreset);
              setStatus(`custom preset ${state.activePreset} removed`);
            }}
          >
            Delete Custom
          </button>
        ) : null}
      </div>

      <div style={ROW_STYLE}>
        <button type="button" style={BUTTON_STYLE} onClick={handleExport}>
          Export JSON
        </button>
        <button
          type="button"
          style={BUTTON_STYLE}
          onClick={() => {
            const result = importLayoutJson(importText);
            setStatus(result.ok ? "layout imported" : result.error ?? "import failed");
          }}
        >
          Import JSON
        </button>
        <button
          type="button"
          style={BUTTON_STYLE}
          onClick={() => {
            resetLayout("debug");
            setStatus("layout reset (debug)");
          }}
        >
          Panic Reset
        </button>
      </div>

      <textarea
        value={importText}
        onChange={(event) => setImportText(event.currentTarget.value)}
        placeholder='Paste layout JSON (e.g. {"version":1,...})'
        style={{ ...INPUT_STYLE, minHeight: "88px", resize: "vertical" }}
      />

      <div style={ROW_STYLE}>
        <button type="button" style={BUTTON_STYLE} onClick={() => toggleWindow("scene-editor")}>Toggle Editor (E)</button>
        <button type="button" style={BUTTON_STYLE} onClick={() => toggleWindow("layer-debug")}>Toggle Layers (L)</button>
        <button type="button" style={BUTTON_STYLE} onClick={() => toggleWindow("scene-graph")}>Toggle Graph (G)</button>
      </div>

      <p style={STATUS_STYLE}>{status}</p>
    </div>
  );
}
