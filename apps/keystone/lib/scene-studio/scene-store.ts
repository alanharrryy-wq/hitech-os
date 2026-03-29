import {
  SCENE_STUDIO_SCHEMA_VERSION,
  SCENE_STUDIO_STORAGE_KEY
} from "./scene-constants";
import { migrateScene, migrateScenes } from "./scene-migrations";
import {
  SCENE_EXPORT_ENVELOPE_SCHEMA,
  SCENE_SCHEMA_V2,
  normalizeSceneInput,
  type SceneRecord
} from "./scene-schema";

export type SceneImportMode = "replace" | "merge";

export interface SceneImportError {
  readonly index: number;
  readonly error: string;
}

export interface SceneImportResult {
  readonly imported: number;
  readonly migrated: number;
  readonly errors: readonly SceneImportError[];
}

export interface SceneExportEnvelope {
  readonly schemaVersion: number;
  readonly exportedAt: string;
  readonly scenes: readonly SceneRecord[];
}

export interface SceneStore {
  list(): readonly SceneRecord[];
  get(id: string): SceneRecord | undefined;
  upsert(scene: SceneRecord): SceneRecord;
  remove(id: string): void;
  replaceAll(scenes: readonly SceneRecord[]): void;
  importScenes(payload: unknown, mode: SceneImportMode): SceneImportResult;
  exportScenes(): SceneExportEnvelope;
  clear(): void;
}

function sortScenes(scenes: readonly SceneRecord[]): SceneRecord[] {
  return [...scenes].sort((left, right) => {
    if (left.updatedAt === right.updatedAt) {
      return left.id.localeCompare(right.id);
    }

    return right.updatedAt.localeCompare(left.updatedAt);
  });
}

function mergeSceneCollections(existing: readonly SceneRecord[], incoming: readonly SceneRecord[]): SceneRecord[] {
  const map = new Map<string, SceneRecord>();

  for (const scene of existing) {
    map.set(scene.id, scene);
  }

  for (const scene of incoming) {
    map.set(scene.id, scene);
  }

  return sortScenes([...map.values()]);
}

function normalizeForStore(scene: SceneRecord): SceneRecord {
  return SCENE_SCHEMA_V2.parse(
    normalizeSceneInput({
      ...scene,
      updatedAt: scene.updatedAt || new Date().toISOString()
    })
  );
}

function parseImportPayload(payload: unknown): unknown[] {
  const envelope = SCENE_EXPORT_ENVELOPE_SCHEMA.safeParse(payload);
  if (envelope.success) {
    return envelope.data.scenes;
  }

  if (Array.isArray(payload)) {
    return payload;
  }

  if (payload && typeof payload === "object") {
    return Object.values(payload as Record<string, unknown>);
  }

  throw new Error("Unsupported scene import payload. Expected envelope, array, or keyed object.");
}

export class InMemorySceneStore implements SceneStore {
  private scenes = new Map<string, SceneRecord>();

  constructor(initialScenes: readonly SceneRecord[] = []) {
    for (const scene of initialScenes) {
      this.scenes.set(scene.id, normalizeForStore(scene));
    }
  }

  list(): readonly SceneRecord[] {
    return sortScenes([...this.scenes.values()]);
  }

  get(id: string): SceneRecord | undefined {
    return this.scenes.get(id);
  }

  upsert(scene: SceneRecord): SceneRecord {
    const normalized = normalizeForStore(scene);
    this.scenes.set(normalized.id, normalized);
    return normalized;
  }

  remove(id: string): void {
    this.scenes.delete(id);
  }

  replaceAll(scenes: readonly SceneRecord[]): void {
    this.scenes.clear();
    for (const scene of scenes) {
      this.scenes.set(scene.id, normalizeForStore(scene));
    }
  }

  importScenes(payload: unknown, mode: SceneImportMode): SceneImportResult {
    const rawScenes = parseImportPayload(payload);
    const migrated: SceneRecord[] = [];
    const errors: SceneImportError[] = [];
    let migratedCount = 0;

    rawScenes.forEach((entry, index) => {
      try {
        const migratedScene = migrateScene(entry);
        migrated.push(migratedScene.scene);
        if (migratedScene.migrated) {
          migratedCount += 1;
        }
      } catch (error) {
        errors.push({
          index,
          error: error instanceof Error ? error.message : "Unknown scene import error"
        });
      }
    });

    const nextScenes =
      mode === "replace"
        ? sortScenes(migrated)
        : mergeSceneCollections(this.list(), migrated);

    this.replaceAll(nextScenes);

    return {
      imported: migrated.length,
      migrated: migratedCount,
      errors
    };
  }

  exportScenes(): SceneExportEnvelope {
    return {
      schemaVersion: SCENE_STUDIO_SCHEMA_VERSION,
      exportedAt: new Date().toISOString(),
      scenes: this.list()
    };
  }

  clear(): void {
    this.scenes.clear();
  }
}

function safeParseStoredScenes(raw: string): readonly SceneRecord[] {
  try {
    const parsed = JSON.parse(raw) as unknown;
    const rawEntries = parseImportPayload(parsed);
    return migrateScenes(rawEntries).scenes;
  } catch {
    return [];
  }
}

export class LocalSceneStore extends InMemorySceneStore {
  private readonly storageKey: string;

  constructor(storageKey = SCENE_STUDIO_STORAGE_KEY) {
    super([]);
    this.storageKey = storageKey;
    this.hydrate();
  }

  private canUseStorage(): boolean {
    return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
  }

  private hydrate(): void {
    if (!this.canUseStorage()) {
      return;
    }

    const raw = window.localStorage.getItem(this.storageKey);
    if (!raw) {
      return;
    }

    const scenes = safeParseStoredScenes(raw);
    this.replaceAll(scenes);
  }

  private persist(): void {
    if (!this.canUseStorage()) {
      return;
    }

    window.localStorage.setItem(this.storageKey, JSON.stringify(this.exportScenes()));
  }

  override upsert(scene: SceneRecord): SceneRecord {
    const saved = super.upsert(scene);
    this.persist();
    return saved;
  }

  override remove(id: string): void {
    super.remove(id);
    this.persist();
  }

  override replaceAll(scenes: readonly SceneRecord[]): void {
    super.replaceAll(scenes);
    this.persist();
  }

  override importScenes(payload: unknown, mode: SceneImportMode): SceneImportResult {
    const result = super.importScenes(payload, mode);
    this.persist();
    return result;
  }

  override clear(): void {
    super.clear();
    if (this.canUseStorage()) {
      window.localStorage.removeItem(this.storageKey);
    }
  }
}

export function serializeSceneExport(envelope: SceneExportEnvelope): string {
  const orderedScenes = sortScenes(envelope.scenes);
  return `${JSON.stringify(
    {
      schemaVersion: envelope.schemaVersion,
      exportedAt: envelope.exportedAt,
      scenes: orderedScenes
    },
    null,
    2
  )}\n`;
}

export function parseSceneExport(raw: string): SceneExportEnvelope {
  const parsed = JSON.parse(raw) as unknown;
  const envelope = SCENE_EXPORT_ENVELOPE_SCHEMA.parse(parsed);
  const migrated = migrateScenes(envelope.scenes).scenes;

  return {
    schemaVersion: SCENE_STUDIO_SCHEMA_VERSION,
    exportedAt: envelope.exportedAt,
    scenes: migrated
  };
}
