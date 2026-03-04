"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  LocalSceneStore,
  createDefaultSceneLibrary,
  createDuplicateSceneId,
  ensureSceneId,
  parseSceneExport,
  serializeSceneExport,
  type SceneImportMode,
  type SceneImportResult,
  type SceneRecord
} from "../../lib/scene-studio";

export type SceneSortMode = "updated" | "title" | "route";

function sortScenes(scenes: readonly SceneRecord[], mode: SceneSortMode): SceneRecord[] {
  const sorted = [...scenes];

  if (mode === "title") {
    return sorted.sort((left, right) => left.title.localeCompare(right.title));
  }

  if (mode === "route") {
    return sorted.sort((left, right) => {
      if (left.route === right.route) {
        return left.title.localeCompare(right.title);
      }
      return left.route.localeCompare(right.route);
    });
  }

  return sorted.sort((left, right) => right.updatedAt.localeCompare(left.updatedAt));
}

function createSceneTemplate(existingIds: ReadonlySet<string>): SceneRecord {
  const timestamp = new Date().toISOString();
  const baseId = ensureSceneId(`scene-${timestamp.slice(0, 10)}`);

  return {
    schemaVersion: 2,
    id: createDuplicateSceneId(baseId, existingIds),
    title: "New Scene",
    route: "/pitch/02-industrial-flow",
    query: "debug=1&layerProfile=neutral&layers=none&motion=off",
    viewport: { preset: "desktop" },
    layerProfile: "neutral",
    layers: {
      mode: "none",
      layerIds: []
    },
    motion: "off",
    tags: ["draft"],
    createdAt: timestamp,
    updatedAt: timestamp
  };
}

function serializeComparableScene(scene: SceneRecord): string {
  return JSON.stringify(scene);
}

export interface SceneStudioState {
  readonly scenes: readonly SceneRecord[];
  readonly selectedScene: SceneRecord | undefined;
  readonly draftScene: SceneRecord | undefined;
  readonly dirty: boolean;
  readonly sortMode: SceneSortMode;
  readonly setSortMode: (mode: SceneSortMode) => void;
  readonly selectScene: (id: string) => boolean;
  readonly updateDraft: (next: SceneRecord) => void;
  readonly saveDraft: () => SceneRecord | undefined;
  readonly discardDraft: () => void;
  readonly createScene: () => SceneRecord;
  readonly duplicateSelectedScene: () => SceneRecord | undefined;
  readonly deleteSelectedScene: () => void;
  readonly resetSelectedSceneToDefaults: () => void;
  readonly exportAllScenes: () => string;
  readonly exportSelectedScene: () => string | null;
  readonly importScenesFromJson: (raw: string, mode: SceneImportMode) => SceneImportResult;
}

export function useSceneStudioState(): SceneStudioState {
  const storeRef = useRef<LocalSceneStore | null>(null);
  const defaultLibraryRef = useRef<readonly SceneRecord[]>(createDefaultSceneLibrary());

  const [scenes, setScenes] = useState<readonly SceneRecord[]>(defaultLibraryRef.current);
  const [selectedId, setSelectedId] = useState<string | undefined>(defaultLibraryRef.current[0]?.id);
  const [draftScene, setDraftScene] = useState<SceneRecord | undefined>(defaultLibraryRef.current[0]);
  const [sortMode, setSortMode] = useState<SceneSortMode>("updated");

  useEffect(() => {
    if (storeRef.current) {
      return;
    }

    const store = new LocalSceneStore();
    if (store.list().length === 0) {
      store.replaceAll(defaultLibraryRef.current);
    }

    const loaded = store.list();
    storeRef.current = store;
    setScenes(loaded);
    const first = loaded[0];
    setSelectedId(first?.id);
    setDraftScene(first);
  }, []);

  const sortedScenes = useMemo(() => sortScenes(scenes, sortMode), [scenes, sortMode]);

  const selectedScene = useMemo(() => {
    if (!selectedId) {
      return undefined;
    }

    return scenes.find((scene) => scene.id === selectedId);
  }, [scenes, selectedId]);

  const dirty = useMemo(() => {
    if (!selectedScene || !draftScene) {
      return false;
    }

    return serializeComparableScene(selectedScene) !== serializeComparableScene(draftScene);
  }, [draftScene, selectedScene]);

  useEffect(() => {
    const onBeforeUnload = (event: BeforeUnloadEvent) => {
      if (!dirty) {
        return;
      }

      event.preventDefault();
      event.returnValue = "";
    };

    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [dirty]);

  const refreshFromStore = useCallback(() => {
    const store = storeRef.current;
    if (!store) {
      return;
    }

    const next = store.list();
    setScenes(next);

    if (!selectedId && next.length > 0) {
      setSelectedId(next[0]?.id);
      setDraftScene(next[0]);
      return;
    }

    if (selectedId) {
      const selected = next.find((scene) => scene.id === selectedId);
      if (!selected) {
        setSelectedId(next[0]?.id);
        setDraftScene(next[0]);
      } else {
        setDraftScene(selected);
      }
    }
  }, [selectedId]);

  const selectScene = useCallback(
    (id: string): boolean => {
      const target = scenes.find((scene) => scene.id === id);
      if (!target) {
        return false;
      }

      if (dirty && !window.confirm("Discard unsaved scene changes?")) {
        return false;
      }

      setSelectedId(id);
      setDraftScene(target);
      return true;
    },
    [dirty, scenes]
  );

  const updateDraft = useCallback((next: SceneRecord) => {
    setDraftScene(next);
  }, []);

  const saveDraft = useCallback((): SceneRecord | undefined => {
    const store = storeRef.current;
    if (!store || !draftScene) {
      return undefined;
    }

    const now = new Date().toISOString();
    const createdAt = selectedScene?.createdAt ?? draftScene.createdAt ?? now;
    const sceneToSave: SceneRecord = {
      ...draftScene,
      createdAt,
      updatedAt: now
    };

    const saved = store.upsert(sceneToSave);
    refreshFromStore();
    setSelectedId(saved.id);
    setDraftScene(saved);
    return saved;
  }, [draftScene, refreshFromStore, selectedScene]);

  const discardDraft = useCallback(() => {
    setDraftScene(selectedScene);
  }, [selectedScene]);

  const createScene = useCallback((): SceneRecord => {
    const store = storeRef.current;
    if (!store) {
      const fallback = createSceneTemplate(new Set(scenes.map((scene) => scene.id)));
      setDraftScene(fallback);
      setSelectedId(fallback.id);
      return fallback;
    }

    const existingIds = new Set(store.list().map((scene) => scene.id));
    const scene = createSceneTemplate(existingIds);
    store.upsert(scene);
    refreshFromStore();
    setSelectedId(scene.id);
    setDraftScene(scene);
    return scene;
  }, [refreshFromStore, scenes]);

  const duplicateSelectedScene = useCallback((): SceneRecord | undefined => {
    const store = storeRef.current;
    if (!store || !selectedScene) {
      return undefined;
    }

    const existingIds = new Set(store.list().map((scene) => scene.id));
    const timestamp = new Date().toISOString();
    const clone: SceneRecord = {
      ...selectedScene,
      id: createDuplicateSceneId(`${selectedScene.id}-copy`, existingIds),
      title: `${selectedScene.title} (Copy)`,
      createdAt: timestamp,
      updatedAt: timestamp
    };

    store.upsert(clone);
    refreshFromStore();
    setSelectedId(clone.id);
    setDraftScene(clone);
    return clone;
  }, [refreshFromStore, selectedScene]);

  const deleteSelectedScene = useCallback(() => {
    const store = storeRef.current;
    if (!store || !selectedId) {
      return;
    }

    store.remove(selectedId);
    const next = store.list();
    setScenes(next);
    setSelectedId(next[0]?.id);
    setDraftScene(next[0]);
  }, [selectedId]);

  const resetSelectedSceneToDefaults = useCallback(() => {
    if (!selectedScene) {
      return;
    }

    const seed = defaultLibraryRef.current.find((scene) => scene.id === selectedScene.id);
    if (!seed) {
      const now = new Date().toISOString();
      setDraftScene({
        ...selectedScene,
        layerProfile: "neutral",
        layers: { mode: "none", layerIds: [] },
        motion: "off",
        query: "debug=1&layerProfile=neutral&layers=none&motion=off",
        updatedAt: now
      });
      return;
    }

    setDraftScene({
      ...seed,
      createdAt: selectedScene.createdAt,
      updatedAt: new Date().toISOString()
    });
  }, [selectedScene]);

  const exportAllScenes = useCallback((): string => {
    const store = storeRef.current;
    if (!store) {
      return "";
    }

    return serializeSceneExport(store.exportScenes());
  }, []);

  const exportSelectedScene = useCallback((): string | null => {
    if (!selectedScene) {
      return null;
    }

    return serializeSceneExport({
      schemaVersion: 2,
      exportedAt: new Date().toISOString(),
      scenes: [selectedScene]
    });
  }, [selectedScene]);

  const importScenesFromJson = useCallback(
    (raw: string, mode: SceneImportMode): SceneImportResult => {
      const store = storeRef.current;
      if (!store) {
        return {
          imported: 0,
          migrated: 0,
          errors: [{ index: -1, error: "Scene store not initialized" }]
        };
      }

      const parsed = parseSceneExport(raw);
      const result = store.importScenes(parsed, mode);
      refreshFromStore();
      return result;
    },
    [refreshFromStore]
  );

  return {
    scenes: sortedScenes,
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
  };
}
