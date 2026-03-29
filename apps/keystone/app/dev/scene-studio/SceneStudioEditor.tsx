"use client";

import { ALL_LAYERS, type LayerId } from "@hitech/ui-kit";
import { KNOWN_PITCH_ROUTES, type SceneRecord } from "../../../lib/scene-studio";
import styles from "./scene-studio.module.css";
import { FloatingWindow } from "./FloatingWindow";

const cls = (name: string): string => styles[name] ?? "";

const LAYER_GROUPS: Readonly<Record<string, readonly LayerId[]>> = {
  stage: ALL_LAYERS.filter((id) => id.startsWith("stage.")),
  card: ALL_LAYERS.filter((id) => id.startsWith("card.")),
  inset: ALL_LAYERS.filter((id) => id.startsWith("inset.")),
  motion: ["motion.enabled"]
};

export interface SceneStudioEditorProps {
  readonly scene: SceneRecord | undefined;
  readonly onChange: (scene: SceneRecord) => void;
  readonly onResetToDefaults: () => void;
}

function toTagsInput(tags: readonly string[]): string {
  return tags.join(", ");
}

function fromTagsInput(input: string): readonly string[] {
  return input
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function ensureRoute(route: string): string {
  const trimmed = route.trim();
  if (!trimmed) return "/";
  if (!trimmed.startsWith("/")) return `/${trimmed}`;
  return trimmed;
}

function updateScene(scene: SceneRecord, patch: Partial<SceneRecord>): SceneRecord {
  return { ...scene, ...patch };
}

function ensureLayerList(layers: readonly LayerId[]): readonly LayerId[] {
  return Array.from(new Set(layers));
}

function sortLayers(layers: readonly LayerId[]): readonly LayerId[] {
  return [...layers].sort((a, b) => a.localeCompare(b));
}

function isKnownRoute(route: string): boolean {
  return KNOWN_PITCH_ROUTES.includes(route as (typeof KNOWN_PITCH_ROUTES)[number]);
}

export function SceneStudioEditor({ scene, onChange, onResetToDefaults }: SceneStudioEditorProps) {
  if (!scene) return null;

  const invalidRoute = scene.route.trim().length > 0 && !scene.route.startsWith("/");
  const invalidListMode = scene.mode === "list" && (!scene.layers || scene.layers.length === 0);

  return (
    <FloatingWindow
      id="scene-studio-editor"
      title="Scene Studio · Editor"
      defaultPos={{ x: 18, y: 18 }}
      defaultSize={{ w: 520, h: 720 }}
    >
      <div className={cls("panelBody")}>
        <div className={cls("actionsRow")}>
          <button type="button" className={cls("button")} onClick={onResetToDefaults}>
            Reset Defaults
          </button>
        </div>

        {invalidRoute ? <p className={cls("warning")}>Route must start with '/'.</p> : null}
        {invalidListMode ? (
          <p className={cls("warning")}>List mode requires at least one layer.</p>
        ) : null}

        <div className={cls("fieldset")}>
          <label className={cls("legend")} htmlFor="scene-id-input">
            Scene Id
          </label>
          <input
            id="scene-id-input"
            className={cls("input")}
            value={scene.id}
            onChange={(event) => onChange(updateScene(scene, { id: event.currentTarget.value }))}
          />

          <label className={cls("legend")} htmlFor="scene-title-input">
            Title
          </label>
          <input
            id="scene-title-input"
            className={cls("input")}
            value={scene.title}
            onChange={(event) => onChange(updateScene(scene, { title: event.currentTarget.value }))}
          />

          <label className={cls("legend")} htmlFor="scene-route-input">
            Route
          </label>
          <input
            id="scene-route-input"
            className={cls("input")}
            value={scene.route}
            onChange={(event) =>
              onChange(updateScene(scene, { route: ensureRoute(event.currentTarget.value) }))
            }
          />

          <div className={cls("hintRow")}>
            <span className={cls("hint")}>
              {isKnownRoute(scene.route) ? "Known route" : "Custom route"}
            </span>
          </div>

          <label className={cls("legend")} htmlFor="scene-tags-input">
            Tags
          </label>
          <input
            id="scene-tags-input"
            className={cls("input")}
            value={toTagsInput(scene.tags ?? [])}
            onChange={(event) =>
              onChange(updateScene(scene, { tags: fromTagsInput(event.currentTarget.value) }))
            }
          />
        </div>

        <div className={cls("fieldset")}>
          <label className={cls("legend")} htmlFor="scene-mode-input">
            Mode
          </label>
          <select
            id="scene-mode-input"
            className={cls("select")}
            value={scene.mode}
            onChange={(event) =>
              onChange(
                updateScene(scene, { mode: event.currentTarget.value as SceneRecord["mode"] })
              )
            }
          >
            <option value="single">single</option>
            <option value="list">list</option>
          </select>
        </div>

        <div className={cls("fieldset")}>
          <div className={cls("legend")}>Layers</div>

          {Object.entries(LAYER_GROUPS).map(([group, ids]) => (
            <details key={group} className={cls("details")} open>
              <summary className={cls("summary")}>{group}</summary>

              <div className={cls("layerGrid")}>
                {ids.map((layerId) => {
                  const checked = (scene.layers ?? []).includes(layerId);
                  return (
                    <label key={layerId} className={cls("layerItem")}>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={(event) => {
                          const next = event.currentTarget.checked
                            ? ensureLayerList([...(scene.layers ?? []), layerId])
                            : (scene.layers ?? []).filter((id) => id !== layerId);

                          onChange(updateScene(scene, { layers: sortLayers(next) }));
                        }}
                      />
                      <span className={cls("layerLabel")}>{layerId}</span>
                    </label>
                  );
                })}
              </div>
            </details>
          ))}
        </div>
      </div>
    </FloatingWindow>
  );
}
