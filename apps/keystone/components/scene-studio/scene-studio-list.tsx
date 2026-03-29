"use client";

import { useEffect, useMemo, useRef, type RefObject } from "react";
import { buildSceneTagIndex, searchScenes, type SceneRecord } from "../../lib/scene-studio";
import styles from "./scene-studio.module.css";

const cls = (name: string): string => styles[name] ?? "";

export interface SceneStudioListProps {
  readonly scenes: readonly SceneRecord[];
  readonly selectedId: string | undefined;
  readonly searchTerm: string;
  readonly selectedTags: readonly string[];
  readonly onSearchTermChange: (value: string) => void;
  readonly onTagToggle: (tag: string) => void;
  readonly onSelect: (id: string) => void;
  readonly searchInputRef: RefObject<HTMLInputElement | null>;
}

export function SceneStudioList({
  scenes,
  selectedId,
  searchTerm,
  selectedTags,
  onSearchTermChange,
  onTagToggle,
  onSelect,
  searchInputRef
}: SceneStudioListProps) {
  const listRef = useRef<HTMLUListElement | null>(null);

  const visibleScenes = useMemo(
    () => searchScenes(scenes, { term: searchTerm, tags: selectedTags }),
    [scenes, searchTerm, selectedTags]
  );

  const tagIndex = useMemo(() => buildSceneTagIndex(scenes), [scenes]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (!listRef.current) {
        return;
      }

      if (event.key !== "ArrowDown" && event.key !== "ArrowUp") {
        return;
      }

      const items = visibleScenes;
      if (items.length === 0) {
        return;
      }

      event.preventDefault();
      const currentIndex = items.findIndex((scene) => scene.id === selectedId);
      const direction = event.key === "ArrowDown" ? 1 : -1;
      const nextIndex =
        currentIndex < 0
          ? 0
          : (currentIndex + direction + items.length) % items.length;

      const next = items[nextIndex];
      if (next) {
        onSelect(next.id);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onSelect, selectedId, visibleScenes]);

  return (
    <>
      <div className={cls("searchRow")}>
        <input
          ref={searchInputRef}
          aria-label="Search scenes"
          className={cls("input")}
          placeholder="Search scenes, routes, tags"
          value={searchTerm}
          onChange={(event) => onSearchTermChange(event.currentTarget.value)}
        />
        <button type="button" className={cls("button")} onClick={() => onSearchTermChange("")}>
          Clear
        </button>
      </div>

      <div className={cls("tagCloud")} aria-label="Scene tags filter">
        {tagIndex.map((tag) => {
          const selected = selectedTags.includes(tag.tag);
          return (
            <button
              key={tag.tag}
              type="button"
              className={cls("tagPill")}
              data-selected={selected ? "1" : "0"}
              onClick={() => onTagToggle(tag.tag)}
              aria-pressed={selected}
            >
              {tag.tag} ({tag.count})
            </button>
          );
        })}
      </div>

      <ul ref={listRef} className={cls("sceneList")} aria-label="Scene list">
        {visibleScenes.map((scene) => (
          <li key={scene.id}>
            <button
              type="button"
              className={cls("sceneItem")}
              data-active={scene.id === selectedId ? "1" : "0"}
              onClick={() => onSelect(scene.id)}
              aria-label={`Select scene ${scene.title}`}
            >
              <p className={cls("sceneItemTitle")}>{scene.title}</p>
              <p className={cls("sceneItemMeta")}>{scene.id}</p>
              <p className={cls("sceneItemMeta")}>{scene.route}</p>
            </button>
          </li>
        ))}
      </ul>
    </>
  );
}




