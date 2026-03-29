export type SceneItem = {
  id: string;          // slug (ej. "01-double-engine")
  title: string;       // label bonito
  path: string;        // ruta (ej. "/pitch/01-double-engine")
};

export type SceneGroup = {
  title: string;
  items: SceneItem[];
};

/**
 * EDITA AQUÍ tu catálogo de escenas.
 * Tip: mantiene ids estables para que el search/favs no se rompan.
 */
export const SCENE_GROUPS: SceneGroup[] = [
  {
    title: "Studio",
    items: [
      { id: "scene-studio", title: "Scene Studio", path: "/dev/scene-studio" },
    ],
  },
  {
    title: "Pitch",
    items: [
      { id: "01-double-engine", title: "01 · Double Engine", path: "/pitch/01-double-engine" },
      // agrega más:
      // { id: "02-problem", title: "02 · Problem", path: "/pitch/02-problem" },
      // { id: "03-solution", title: "03 · Solution", path: "/pitch/03-solution" },
    ],
  },
];

export function allScenesFlat(): SceneItem[] {
  return SCENE_GROUPS.flatMap(g => g.items);
}