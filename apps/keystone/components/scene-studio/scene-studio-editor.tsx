"use client";

import { ALL_LAYERS, type LayerId } from "@hitech/ui-kit";
import {
  KNOWN_PITCH_ROUTES,
  createDefaultSceneLibrary,
  parseSceneUrlState,
  type SceneRecord
} from "../../lib/scene-studio";
import styles from "./scene-studio.module.css";

const cls = (name: string): string => styles[name] ?? "";

const LAYER_GROUPS: Readonly<Record<string, readonly LayerId[]>> = {
  stage: ALL_LAYERS.filter((id) => id.startsWith("stage.")),
  card: ALL_LAYERS.filter((id) => id.startsWith("card.")),
  inset: ALL_LAYERS.filter((id) => id.startsWith("inset.")),
  motion: ["motion.enabled"]
};

const SCENE_REFERENCE_TIMESTAMP = "2026-01-01T00:00:00.000Z";
const DEFAULT_SCENE_QUERY = "debug=1&layerProfile=neutral&layers=none&motion=off";
const ROUTABLE_PITCH_ROUTES = KNOWN_PITCH_ROUTES.filter((route) => route !== "/pitch");
const SCENE_REFERENCE_LIBRARY = createDefaultSceneLibrary(SCENE_REFERENCE_TIMESTAMP);

export interface SceneStudioEditorProps {
  readonly scene: SceneRecord | undefined;
  readonly onChange: (scene: SceneRecord) => void;
  readonly onResetToDefaults: () => void;
}

function toTagsInput(tags: readonly string[]): string {
  return tags.join(", ");
}

function parseTagsInput(value: string): string[] {
  return Array.from(
    new Set(
      value
        .split(",")
        .map((tag) => tag.trim().toLowerCase().replace(/\s+/g, "-"))
        .filter((tag) => tag.length > 0)
    )
  ).sort((left, right) => left.localeCompare(right));
}

function updateScene(scene: SceneRecord, patch: Partial<SceneRecord>): SceneRecord {
  return {
    ...scene,
    ...patch,
    updatedAt: new Date().toISOString()
  };
}

function toggleLayer(scene: SceneRecord, layerId: LayerId, on: boolean): SceneRecord {
  const nextIds = new Set(scene.layers.layerIds);
  if (on) {
    nextIds.add(layerId);
  } else {
    nextIds.delete(layerId);
  }

  const layerIds = ALL_LAYERS.filter((id) => nextIds.has(id));
  return updateScene(scene, {
    layers: {
      mode: layerIds.length > 0 ? "list" : "none",
      layerIds
    }
  });
}

function applyLayerGroup(scene: SceneRecord, group: keyof typeof LAYER_GROUPS, on: boolean): SceneRecord {
  const nextIds = new Set(scene.layers.layerIds);

  for (const id of LAYER_GROUPS[group] ?? []) {
    if (on) {
      nextIds.add(id);
    } else {
      nextIds.delete(id);
    }
  }

  const layerIds = ALL_LAYERS.filter((id) => nextIds.has(id));

  return updateScene(scene, {
    layers: {
      mode: layerIds.length > 0 ? "list" : "none",
      layerIds
    }
  });
}

function uniqueStrings(values: readonly string[]): string[] {
  return Array.from(new Set(values.filter((value) => value.trim().length > 0)));
}

function toTitleCase(value: string): string {
  return value.replace(/\b\w/g, (char) => char.toUpperCase());
}

function buildRouteReferenceId(route: string): string {
  return route
    .replace(/^\/+/, "")
    .replace(/[^a-z0-9]+/gi, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase()
    .concat("-neutral-desktop");
}

function buildRouteReferenceTitle(route: string): string {
  const normalized = route.replace(/^\/+/, "");
  const segments = normalized
    .split("/")
    .filter(Boolean)
    .map((segment) => segment.replace(/^\d+-/, "").replace(/-/g, " ").trim())
    .filter(Boolean)
    .map(toTitleCase);

  if (segments.length === 0) {
    return "Pitch Runtime Neutral Desktop";
  }

  return `${segments.join(" ")} Neutral Desktop`;
}

function buildRouteCoverageReferenceScene(route: string): SceneRecord {
  const urlState = parseSceneUrlState(route, DEFAULT_SCENE_QUERY);
  return {
    schemaVersion: 2,
    id: buildRouteReferenceId(urlState.route),
    title: buildRouteReferenceTitle(urlState.route),
    route: urlState.route,
    query: urlState.query,
    viewport: { preset: "desktop" },
    layerProfile: urlState.layerProfile,
    layers: {
      mode: urlState.layersMode,
      layerIds: [...urlState.layerIds]
    },
    motion: urlState.motion,
    notes: "Generated scene reference for pitch route coverage in Dev Console.",
    tags: ["pitch", "runtime", "coverage"],
    createdAt: SCENE_REFERENCE_TIMESTAMP,
    updatedAt: SCENE_REFERENCE_TIMESTAMP
  };
}

function buildSceneReferenceLibrary(scene: SceneRecord): readonly SceneRecord[] {
  const byId = new Map<string, SceneRecord>();
  for (const entry of SCENE_REFERENCE_LIBRARY) {
    byId.set(entry.id, entry);
  }
  byId.set(scene.id, scene);

  const coveredRoutes = new Set<string>();
  for (const entry of byId.values()) {
    coveredRoutes.add(parseSceneUrlState(entry.route, entry.query).route);
  }

  for (const route of ROUTABLE_PITCH_ROUTES) {
    if (coveredRoutes.has(route)) {
      continue;
    }
    const fallback = buildRouteCoverageReferenceScene(route);
    byId.set(fallback.id, fallback);
    coveredRoutes.add(route);
  }

  return [...byId.values()].sort((left, right) => left.id.localeCompare(right.id));
}

function findReferenceById(
  library: readonly SceneRecord[],
  id: string
): SceneRecord | undefined {
  return library.find((entry) => entry.id === id);
}

function findUniqueReferenceByTitle(
  library: readonly SceneRecord[],
  title: string
): SceneRecord | undefined {
  const matches = library.filter((entry) => entry.title === title);
  return matches.length === 1 ? matches[0] : undefined;
}

function applyReferenceScene(scene: SceneRecord, reference: SceneRecord): SceneRecord {
  return updateScene(scene, {
    id: reference.id,
    title: reference.title,
    route: reference.route,
    query: reference.query,
    viewport: { ...reference.viewport },
    layerProfile: reference.layerProfile,
    layers: {
      mode: reference.layers.mode,
      layerIds: [...reference.layers.layerIds]
    },
    motion: reference.motion,
    notes: reference.notes,
    tags: [...reference.tags]
  });
}

export function SceneStudioEditor({ scene, onChange, onResetToDefaults }: SceneStudioEditorProps) {
  if (!scene) {
    return <p className={cls("subtle")}>Select a scene to edit.</p>;
  }

  const invalidRoute = !scene.route.startsWith("/");
  const invalidListMode = scene.layers.mode === "list" && scene.layers.layerIds.length === 0;

  const sceneReferenceLibrary = buildSceneReferenceLibrary(scene);
  const sceneIdOptions = sceneReferenceLibrary.map((entry) => entry.id);
  const titleOptions = uniqueStrings(sceneReferenceLibrary.map((entry) => entry.title));
  const routeOptions = uniqueStrings([
    scene.route,
    ...KNOWN_PITCH_ROUTES,
    ...sceneReferenceLibrary.map((entry) => entry.route)
  ]);

  return (
    <div className={cls("panelBody")}>
      <div className={cls("actionsRow")}>
        <button type="button" className={cls("button")} onClick={onResetToDefaults}>
          Reset Defaults
        </button>
      </div>

      {invalidRoute ? <p className={cls("warning")}>Route must start with '/'.</p> : null}
      {invalidListMode ? <p className={cls("warning")}>List mode requires at least one layer.</p> : null}

      <div className={cls("fieldset")}>
        <label className={cls("legend")} htmlFor="scene-id-input">
          Scene Id
        </label>
        <select
          id="scene-id-input"
          className={cls("select")}
          value={scene.id}
          onChange={(event) => {
            const selectedId = event.currentTarget.value;
            const matched = findReferenceById(sceneReferenceLibrary, selectedId);

            if (!matched) {
              onChange(updateScene(scene, { id: selectedId }));
              return;
            }

            onChange(applyReferenceScene(scene, matched));
          }}
        >
          {sceneIdOptions.map((sceneId) => (
            <option key={sceneId} value={sceneId}>
              {sceneId}
            </option>
          ))}
        </select>

        <label className={cls("legend")} htmlFor="scene-title-input">
          Title
        </label>
        <select
          id="scene-title-input"
          className={cls("select")}
          value={scene.title}
          onChange={(event) => {
            const selectedTitle = event.currentTarget.value;
            const matched = findUniqueReferenceByTitle(sceneReferenceLibrary, selectedTitle);

            if (!matched) {
              onChange(updateScene(scene, { title: selectedTitle }));
              return;
            }

            onChange(applyReferenceScene(scene, matched));
          }}
        >
          {titleOptions.map((title) => (
            <option key={title} value={title}>
              {title}
            </option>
          ))}
        </select>

        <label className={cls("legend")} htmlFor="scene-route-input">
          Route
        </label>
        <select
          id="scene-route-input"
          className={cls("select")}
          value={scene.route}
          onChange={(event) => onChange(updateScene(scene, { route: event.currentTarget.value }))}
        >
          {routeOptions.map((route) => (
            <option key={route} value={route}>
              {route}
            </option>
          ))}
        </select>

        <p className={cls("subtle")}>
          Identity fields are constrained to known scene options so the floating console does not drift
          into malformed scene metadata.
        </p>
      </div>

      <div className={cls("fieldset")}>
        <label className={cls("legend")} htmlFor="scene-viewport-input">
          Viewport
        </label>
        <select
          id="scene-viewport-input"
          className={cls("select")}
          value={scene.viewport.preset}
          onChange={(event) => {
            const preset = event.currentTarget.value as SceneRecord["viewport"]["preset"];
            if (preset === "custom") {
              onChange(
                updateScene(scene, {
                  viewport: {
                    preset,
                    width: scene.viewport.width ?? 1440,
                    height: scene.viewport.height ?? 900
                  }
                })
              );
              return;
            }

            onChange(
              updateScene(scene, {
                viewport: {
                  preset
                }
              })
            );
          }}
        >
          <option value="desktop">desktop</option>
          <option value="mobile">mobile</option>
          <option value="tablet">tablet</option>
          <option value="custom">custom</option>
        </select>

        {scene.viewport.preset === "custom" ? (
          <div className={cls("kvGrid")}>
            <label>
              <span className={cls("legend")}>Width</span>
              <input
                className={cls("input")}
                type="number"
                min={320}
                max={3840}
                value={scene.viewport.width ?? 1440}
                onChange={(event) =>
                  onChange(
                    updateScene(scene, {
                      viewport: {
                        ...scene.viewport,
                        width: Number(event.currentTarget.value)
                      }
                    })
                  )
                }
              />
            </label>
            <label>
              <span className={cls("legend")}>Height</span>
              <input
                className={cls("input")}
                type="number"
                min={320}
                max={3840}
                value={scene.viewport.height ?? 900}
                onChange={(event) =>
                  onChange(
                    updateScene(scene, {
                      viewport: {
                        ...scene.viewport,
                        height: Number(event.currentTarget.value)
                      }
                    })
                  )
                }
              />
            </label>
          </div>
        ) : null}
      </div>

      <div className={cls("fieldset")}>
        <label className={cls("legend")} htmlFor="scene-profile-input">
          Layer Profile
        </label>
        <select
          id="scene-profile-input"
          className={cls("select")}
          value={scene.layerProfile}
          onChange={(event) =>
            onChange(
              updateScene(scene, {
                layerProfile: event.currentTarget.value as SceneRecord["layerProfile"]
              })
            )
          }
        >
          <option value="neutral">neutral</option>
          <option value="fx">fx</option>
          <option value="perf">perf</option>
        </select>

        <label className={cls("legend")} htmlFor="scene-layers-mode-input">
          Layers Override Mode
        </label>
        <select
          id="scene-layers-mode-input"
          className={cls("select")}
          value={scene.layers.mode}
          onChange={(event) => {
            const mode = event.currentTarget.value as SceneRecord["layers"]["mode"];
            if (mode !== "list") {
              onChange(
                updateScene(scene, {
                  layers: {
                    mode,
                    layerIds: []
                  }
                })
              );
              return;
            }

            onChange(
              updateScene(scene, {
                layers: {
                  mode,
                  layerIds: scene.layers.layerIds.length > 0 ? scene.layers.layerIds : ["stage.haze"]
                }
              })
            );
          }}
        >
          <option value="none">none</option>
          <option value="all">all</option>
          <option value="list">list</option>
        </select>

        <label className={cls("legend")} htmlFor="scene-motion-input">
          Motion
        </label>
        <select
          id="scene-motion-input"
          className={cls("select")}
          value={scene.motion}
          onChange={(event) => onChange(updateScene(scene, { motion: event.currentTarget.value as "on" | "off" }))}
        >
          <option value="off">off</option>
          <option value="on">on</option>
        </select>
      </div>

      <div className={cls("fieldset")}>
        <p className={cls("legend")}>Quick Layer Groups</p>
        <div className={cls("actionsRow")}>
          {(Object.keys(LAYER_GROUPS) as Array<keyof typeof LAYER_GROUPS>).map((group) => (
            <div key={group} className={cls("actionsRow")}>
              <button
                type="button"
                className={cls("button")}
                data-dev-console-scene-command={`${String(group).toUpperCase()} ON`}
                onClick={() => onChange(applyLayerGroup(scene, group, true))}
              >
                {group} on
              </button>
              <button
                type="button"
                className={cls("button")}
                data-dev-console-scene-command={`${String(group).toUpperCase()} OFF`}
                onClick={() => onChange(applyLayerGroup(scene, group, false))}
              >
                {group} off
              </button>
            </div>
          ))}
        </div>

        <div className={cls("layerGrid")}>
          {ALL_LAYERS.map((layerId) => {
            const enabled = scene.layers.layerIds.includes(layerId);
            const disabled = scene.layers.mode !== "list";
            return (
              <label key={layerId} className={cls("checkRow")}>
                <span>{layerId}</span>
                <input
                  type="checkbox"
                  checked={enabled}
                  disabled={disabled}
                  onChange={(event) => onChange(toggleLayer(scene, layerId, event.currentTarget.checked))}
                />
              </label>
            );
          })}
        </div>
      </div>

      <div className={cls("fieldset")}>
        <label className={cls("legend")} htmlFor="scene-tags-input">
          Tags (comma-separated)
        </label>
        <input
          id="scene-tags-input"
          className={cls("input")}
          value={toTagsInput(scene.tags)}
          onChange={(event) => onChange(updateScene(scene, { tags: parseTagsInput(event.currentTarget.value) }))}
        />

        <label className={cls("legend")} htmlFor="scene-notes-input">
          Notes
        </label>
        <textarea
          id="scene-notes-input"
          className={cls("textarea")}
          value={scene.notes ?? ""}
          onChange={(event) => onChange(updateScene(scene, { notes: event.currentTarget.value || undefined }))}
        />
      </div>
    </div>
  );
}
