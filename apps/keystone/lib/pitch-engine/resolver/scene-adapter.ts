import type { SceneRecord } from "../contracts/program-types.js";

export interface SceneRuntimeConfig {
  readonly scene: SceneRecord;
  readonly camera: Readonly<Record<string, unknown>>;
  readonly overlay: Readonly<Record<string, unknown>>;
  readonly motion: Readonly<Record<string, unknown>>;
  readonly layers: Readonly<Record<string, unknown>>;
}

export interface SceneAdapter {
  readonly getSceneById: (sceneId: string) => SceneRecord | null;
  readonly canonicalizeScene: (scene: SceneRecord) => SceneRecord;
}

export class InMemorySceneAdapter implements SceneAdapter {
  private readonly table: Readonly<Record<string, SceneRecord>>;

  public constructor(scenes: Readonly<Record<string, SceneRecord>>) {
    this.table = scenes;
  }

  public getSceneById(sceneId: string): SceneRecord | null {
    return this.table[sceneId] ?? null;
  }

  public canonicalizeScene(scene: SceneRecord): SceneRecord {
    return {
      sceneId: scene.sceneId,
      route: scene.route,
      query: Object.fromEntries(
        Object.entries(scene.query).sort(([left], [right]) => left.localeCompare(right))
      ),
      viewport: {
        width: scene.viewport.width,
        height: scene.viewport.height,
        deviceScaleFactor: scene.viewport.deviceScaleFactor
      },
      profile: scene.profile,
      layers: [...scene.layers].sort((left, right) => left.localeCompare(right)),
      motion: {
        enabled: scene.motion.enabled,
        intensity: scene.motion.intensity,
        reducedMotionPolicy: scene.motion.reducedMotionPolicy
      }
    };
  }
}
