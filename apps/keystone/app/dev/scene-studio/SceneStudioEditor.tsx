"use client";

import {
  createContext,
  useContext,
  useMemo,
  useState,
  type CSSProperties,
  type PropsWithChildren
} from "react";
import {
  buildCanonicalSceneQuery,
  parseSceneQueryToObject,
  type SceneRecord
} from "../../../lib/scene-studio";
import { SceneStudioEditor as SceneStudioEditorFields } from "../../../components/scene-studio/scene-studio-editor";
import {
  useSceneStudioState,
  type SceneStudioState
} from "../../../components/scene-studio/use-scene-studio-state";

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

const INPUT_STYLE: CSSProperties = {
  border: "1px solid hsl(var(--ui-border-2))",
  borderRadius: "8px",
  padding: "0.35rem 0.5rem",
  background: "hsl(var(--ui-surface-1))",
  color: "hsl(var(--ui-text-1))",
  fontSize: "0.78rem"
};

const MUTED_STYLE: CSSProperties = {
  margin: 0,
  fontSize: "0.72rem",
  color: "hsl(var(--ui-text-3))"
};

export interface SceneStudioRuntimeContextValue {
  readonly state: SceneStudioState;
  readonly currentScene: SceneRecord | undefined;
}

const SceneStudioRuntimeContext = createContext<SceneStudioRuntimeContextValue | null>(null);

function syncSceneQuery(scene: SceneRecord): SceneRecord {
  const query = buildCanonicalSceneQuery({
    route: scene.route,
    query: parseSceneQueryToObject(scene.query),
    layerProfile: scene.layerProfile,
    layersMode: scene.layers.mode,
    layerIds: scene.layers.layerIds,
    motion: scene.motion,
    debug: true
  });

  return {
    ...scene,
    query,
    updatedAt: new Date().toISOString()
  };
}

export function SceneStudioRuntimeProvider({ children }: PropsWithChildren) {
  const state = useSceneStudioState();
  const currentScene = state.draftScene ?? state.selectedScene;

  const contextValue = useMemo(
    () => ({
      state,
      currentScene
    }),
    [currentScene, state]
  );

  return <SceneStudioRuntimeContext.Provider value={contextValue}>{children}</SceneStudioRuntimeContext.Provider>;
}

export function useSceneStudioRuntime(): SceneStudioRuntimeContextValue {
  const context = useContext(SceneStudioRuntimeContext);

  if (!context) {
    throw new Error("useSceneStudioRuntime must be used within SceneStudioRuntimeProvider.");
  }

  return context;
}

export function SceneStudioEditorPanel() {
  const { state, currentScene } = useSceneStudioRuntime();
  const [status, setStatus] = useState("ready");

  const save = () => {
    const saved = state.saveDraft();
    setStatus(saved ? `saved ${saved.id}` : "nothing to save");
  };

  return (
    <div style={ROOT_STYLE}>
      <div style={ROW_STYLE}>
        <button type="button" style={BUTTON_STYLE} onClick={() => {
          state.createScene();
          setStatus("new scene created");
        }}>
          New
        </button>
        <button type="button" style={BUTTON_STYLE} onClick={save}>
          Save
        </button>
        <button type="button" style={BUTTON_STYLE} onClick={() => {
          state.discardDraft();
          setStatus("changes discarded");
        }}>
          Discard
        </button>
        <select
          value={state.selectedScene?.id ?? ""}
          style={INPUT_STYLE}
          onChange={(event) => {
            const ok = state.selectScene(event.currentTarget.value);
            setStatus(ok ? `selected ${event.currentTarget.value}` : "selection cancelled");
          }}
          aria-label="Scene selector"
        >
          {state.scenes.map((scene) => (
            <option key={scene.id} value={scene.id}>
              {scene.title}
            </option>
          ))}
        </select>
      </div>

      <p style={MUTED_STYLE}>
        status={status} dirty={state.dirty ? "1" : "0"}
      </p>
      <p style={MUTED_STYLE}>route={currentScene?.route ?? "n/a"}</p>

      <SceneStudioEditorFields
        scene={currentScene}
        onChange={(next) => state.updateDraft(syncSceneQuery(next))}
        onResetToDefaults={state.resetSelectedSceneToDefaults}
      />
    </div>
  );
}
