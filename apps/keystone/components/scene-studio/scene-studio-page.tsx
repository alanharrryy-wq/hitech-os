"use client";

import { useMemo, useRef, useState } from "react";
import {
  buildCanonicalSceneUrl,
  buildCanonicalSceneQuery,
  createDefaultSceneLibrary,
  parseSceneQueryToObject,
  type SceneImportMode,
  type SceneRecord
} from "../../lib/scene-studio";
import { SceneStudioDiagnostics } from "./scene-studio-diagnostics";
import { SceneStudioEditor } from "./scene-studio-editor";
import { SceneStudioHelpPanel } from "./scene-studio-help-panel";
import { SceneStudioList } from "./scene-studio-list";
import styles from "./scene-studio.module.css";
import { SceneStudioPreview } from "./scene-studio-preview";
import { useSceneStudioHotkeys } from "./use-scene-studio-hotkeys";
import { useSceneStudioState } from "./use-scene-studio-state";
import type { SceneDiagnosticsPayload } from "../../lib/scene-studio";

const cls = (name: string): string => styles[name] ?? "";

function syncSceneQuery(scene: SceneRecord): SceneRecord {
  const query = buildCanonicalSceneQuery({
    route: scene.route,
    query: scene.query,
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

async function copyTextToClipboard(text: string): Promise<boolean> {
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

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.append(textarea);
  textarea.select();

  const copied = document.execCommand("copy");
  textarea.remove();
  return copied;
}

function downloadText(fileName: string, content: string): void {
  const blob = new Blob([content], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  anchor.click();
  URL.revokeObjectURL(url);
}

const SORT_OPTIONS: ReadonlyArray<{ value: "updated" | "title" | "route"; label: string }> = [
  { value: "updated", label: "Updated" },
  { value: "title", label: "Title" },
  { value: "route", label: "Route" }
];

export function SceneStudioPage() {
  const {
    scenes,
    selectedScene,
    draftScene,
    dirty,
    sortMode,
    setSortMode,
    selectScene,
    updateDraft,
    saveDraft,
    discardDraft,
    createScene,
    duplicateSelectedScene,
    deleteSelectedScene,
    resetSelectedSceneToDefaults,
    exportAllScenes,
    exportSelectedScene,
    importScenesFromJson
  } = useSceneStudioState();

  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTags, setSelectedTags] = useState<readonly string[]>([]);
  const [diagnostics, setDiagnostics] = useState<SceneDiagnosticsPayload | null>(null);
  const [compareSceneId, setCompareSceneId] = useState<string>("");
  const [statusLine, setStatusLine] = useState<string>("ready");

  const normalizedDraft = useMemo(() => (draftScene ? syncSceneQuery(draftScene) : undefined), [draftScene]);

  const canonicalUrl = useMemo(() => {
    if (!normalizedDraft) {
      return "";
    }

    return buildCanonicalSceneUrl({
      route: normalizedDraft.route,
      query: normalizedDraft.query,
      layerProfile: normalizedDraft.layerProfile,
      layersMode: normalizedDraft.layers.mode,
      layerIds: normalizedDraft.layers.layerIds,
      motion: normalizedDraft.motion,
      debug: true
    });
  }, [normalizedDraft]);

  const compareScene = useMemo(() => scenes.find((scene) => scene.id === compareSceneId), [compareSceneId, scenes]);

  const compareCanonicalUrl = useMemo(() => {
    if (!compareScene) {
      return undefined;
    }

    return buildCanonicalSceneUrl({
      route: compareScene.route,
      query: compareScene.query,
      layerProfile: compareScene.layerProfile,
      layersMode: compareScene.layers.mode,
      layerIds: compareScene.layers.layerIds,
      motion: compareScene.motion,
      debug: true
    });
  }, [compareScene]);

  useSceneStudioHotkeys({
    onFocusSearch: () => searchInputRef.current?.focus(),
    onNewScene: () => {
      createScene();
      setStatusLine("new scene created");
    },
    onSaveScene: () => {
      const saved = saveDraft();
      setStatusLine(saved ? `saved ${saved.id}` : "nothing to save");
    },
    onCopyUrl: () => {
      if (!canonicalUrl) {
        setStatusLine("no scene selected");
        return;
      }

      void copyTextToClipboard(canonicalUrl).then((ok) => {
        setStatusLine(ok ? "canonical URL copied" : "copy failed");
      });
    },
    onRunVisual: () => {
      void runVisualForSelection();
    }
  });

  const toggleTag = (tag: string) => {
    setSelectedTags((previous) => {
      if (previous.includes(tag)) {
        return previous.filter((entry) => entry !== tag);
      }

      return [...previous, tag].sort((left, right) => left.localeCompare(right));
    });
  };

  const runVisualForSelection = async () => {
    if (!normalizedDraft) {
      return;
    }

    setStatusLine(`running visual test for ${normalizedDraft.id}...`);

    try {
      const response = await fetch("/api/scene-studio/run?debug=1", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          sceneIds: [normalizedDraft.id],
          mode: "smoke"
        })
      });

      if (!response.ok) {
        const details = await response.text();
        setStatusLine(`visual run failed: ${details.slice(0, 140)}`);
        return;
      }

      const payload = (await response.json()) as {
        command: string;
        exitCode: number;
        artifactRoot?: string;
      };

      if (payload.exitCode === 0) {
        setStatusLine(`visual run complete: ${payload.artifactRoot ?? "artifacts generated"}`);
      } else {
        setStatusLine(`visual run exited with code ${payload.exitCode}`);
      }
    } catch (error) {
      setStatusLine(error instanceof Error ? error.message : "visual run request failed");
    }
  };

  const importFromFile = async (file: File, mode: SceneImportMode) => {
    const raw = await file.text();

    try {
      const result = importScenesFromJson(raw, mode);
      setStatusLine(
        `imported=${result.imported} migrated=${result.migrated} errors=${result.errors.length}`
      );
    } catch (error) {
      setStatusLine(error instanceof Error ? error.message : "scene import failed");
    }
  };

  const runManifestBootstrap = () => {
    const defaults = createDefaultSceneLibrary();
    const payload = {
      schemaVersion: 2,
      exportedAt: new Date().toISOString(),
      scenes: defaults
    };
    const result = importScenesFromJson(JSON.stringify(payload), "replace");
    setStatusLine(
      `manifest loaded. imported=${result.imported} migrated=${result.migrated} errors=${result.errors.length}`
    );
  };

  return (
    <section className={cls("root")}>
      <header className={cls("panelHeader")}>
        <h1 className={cls("panelTitle")}>Keystone Scene Studio</h1>
        <p className={cls("devBanner")}>
          Dev-only workspace for reproducible scenes, share URLs, diagnostics and visual proof.
        </p>
      </header>

      <div className={cls("shell")}>
        <aside className={cls("panel")} aria-label="Scene catalog">
          <header className={cls("panelHeader")}>
            <h2 className={cls("panelTitle")}>Scenes</h2>
            <div className={cls("actionsRow")}>
              <button type="button" className={cls("button")} onClick={() => {
                createScene();
                setStatusLine("new scene created");
              }}>
                New
              </button>
              <button
                type="button"
                className={cls("button")}
                onClick={() => {
                  const clone = duplicateSelectedScene();
                  setStatusLine(clone ? `duplicated ${clone.id}` : "no scene selected");
                }}
                disabled={!selectedScene}
              >
                Duplicate
              </button>
            </div>
          </header>

          <div className={cls("panelBody")}>
            <div className={cls("searchRow")}>
              <label className={cls("legend")} htmlFor="scene-sort-mode">
                Sort
              </label>
              <select
                id="scene-sort-mode"
                className={cls("select")}
                value={sortMode}
                onChange={(event) => setSortMode(event.currentTarget.value as "updated" | "title" | "route")}
              >
                {SORT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <SceneStudioList
              scenes={scenes}
              selectedId={selectedScene?.id}
              searchTerm={searchTerm}
              selectedTags={selectedTags}
              onSearchTermChange={setSearchTerm}
              onTagToggle={toggleTag}
              onSelect={(id) => {
                const selected = selectScene(id);
                setStatusLine(selected ? `selected ${id}` : "selection cancelled");
              }}
              searchInputRef={searchInputRef}
            />

            <div className={cls("actionsRow")}>
              <button
                type="button"
                className={cls("button")}
                onClick={() => {
                  const payload = exportAllScenes();
                  downloadText("keystone-scenes-export.json", payload);
                  setStatusLine("all scenes exported");
                }}
              >
                Export All
              </button>

              <button
                type="button"
                className={cls("button")}
                onClick={() => {
                  const payload = exportSelectedScene();
                  if (!payload || !selectedScene) {
                    setStatusLine("no scene selected");
                    return;
                  }
                  downloadText(`${selectedScene.id}.json`, payload);
                  setStatusLine(`exported ${selectedScene.id}`);
                }}
                disabled={!selectedScene}
              >
                Export Scene
              </button>

              <label className={cls("button")}>
                Import Merge
                <input
                  type="file"
                  hidden
                  accept="application/json"
                  onChange={async (event) => {
                    const file = event.currentTarget.files?.[0];
                    if (!file) {
                      return;
                    }

                    await importFromFile(file, "merge");
                    event.currentTarget.value = "";
                  }}
                />
              </label>

              <label className={cls("button")}>
                Import Replace
                <input
                  type="file"
                  hidden
                  accept="application/json"
                  onChange={async (event) => {
                    const file = event.currentTarget.files?.[0];
                    if (!file) {
                      return;
                    }

                    await importFromFile(file, "replace");
                    event.currentTarget.value = "";
                  }}
                />
              </label>

              <button type="button" className={cls("button")} onClick={runManifestBootstrap}>
                Reset Library
              </button>
            </div>
          </div>
        </aside>

        <section className={cls("panel")} aria-label="Preview and compare">
          <header className={cls("panelHeader")}>
            <h2 className={cls("panelTitle")}>Preview</h2>
            <div className={cls("actionsRow")}>
              <select
                className={cls("select")}
                value={compareSceneId}
                onChange={(event) => setCompareSceneId(event.currentTarget.value)}
                aria-label="Compare scene selector"
              >
                <option value="">Compare scene...</option>
                {scenes
                  .filter((scene) => scene.id !== normalizedDraft?.id)
                  .map((scene) => (
                    <option key={scene.id} value={scene.id}>
                      {scene.title}
                    </option>
                  ))}
              </select>
            </div>
          </header>
          <div className={cls("panelBody")}>
            <SceneStudioPreview
              scene={normalizedDraft}
              compareScene={compareScene}
              canonicalUrl={canonicalUrl}
              compareCanonicalUrl={compareCanonicalUrl}
              onCopyCanonicalUrl={() => copyTextToClipboard(canonicalUrl)}
              onDiagnostics={setDiagnostics}
              onRunVisual={runVisualForSelection}
            />
          </div>
        </section>

        <aside className={cls("panel")} aria-label="Inspector and diagnostics">
          <header className={cls("panelHeader")}>
            <h2 className={cls("panelTitle")}>Inspector</h2>
            <div className={cls("actionsRow")}>
              <button
                type="button"
                className={cls("button")}
                onClick={() => {
                  const saved = saveDraft();
                  setStatusLine(saved ? `saved ${saved.id}` : "nothing to save");
                }}
                disabled={!dirty}
              >
                Save
              </button>
              <button
                type="button"
                className={cls("button")}
                onClick={() => {
                  discardDraft();
                  setStatusLine("changes discarded");
                }}
                disabled={!dirty}
              >
                Discard
              </button>
              <button
                type="button"
                className={cls("button")}
                onClick={() => {
                  deleteSelectedScene();
                  setStatusLine("scene deleted");
                }}
                disabled={!selectedScene}
              >
                Delete
              </button>
            </div>
          </header>

          <div className={cls("panelBody")}>
            <p className={cls("subtle")}>
              status={statusLine} dirty={dirty ? "1" : "0"}
            </p>

            <SceneStudioEditor
              scene={normalizedDraft}
              onChange={(next) => {
                const queryObject = parseSceneQueryToObject(next.query);
                const refreshed = syncSceneQuery({
                  ...next,
                  query: buildCanonicalSceneQuery({
                    route: next.route,
                    query: queryObject,
                    layerProfile: next.layerProfile,
                    layersMode: next.layers.mode,
                    layerIds: next.layers.layerIds,
                    motion: next.motion,
                    debug: true
                  })
                });
                updateDraft(refreshed);
              }}
              onResetToDefaults={resetSelectedSceneToDefaults}
            />

            <section className={cls("panel")} aria-label="Diagnostics">
              <header className={cls("panelHeader")}>
                <h3 className={cls("panelTitle")}>Diagnostics</h3>
              </header>
              <SceneStudioDiagnostics scene={normalizedDraft} diagnostics={diagnostics} />
            </section>

            <section className={cls("panel")} aria-label="Help">
              <header className={cls("panelHeader")}>
                <h3 className={cls("panelTitle")}>Help</h3>
              </header>
              <SceneStudioHelpPanel />
            </section>
          </div>
        </aside>
      </div>
    </section>
  );
}




