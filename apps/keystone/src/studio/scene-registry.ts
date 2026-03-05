export type SceneItem = {
  id: string;
  title: string;
  path: string;
};

export type SceneGroup = {
  title: string;
  items: SceneItem[];
};

export const SCENE_GROUPS: SceneGroup[] = [
  {
    title: "Studio",
    items: [{ id: "scene-studio", title: "Scene Studio", path: "/dev/scene-studio" }]
  },
  {
    title: "Pitch",
    items: [
      { id: "pitch-index", title: "Pitch Index", path: "/pitch" },
      { id: "01-double-engine", title: "01 · Double Engine", path: "/pitch/01-double-engine" },
      {
        id: "02-industrial-flow",
        title: "02 · Industrial Flow",
        path: "/pitch/02-industrial-flow"
      },
      { id: "03-hitech-os", title: "03 · HITECH OS", path: "/pitch/03-hitech-os" },
      { id: "04-valuation", title: "04 · Valuation", path: "/pitch/04-valuation" },
      {
        id: "05-inventory-foundation",
        title: "05 · Inventory Foundation",
        path: "/pitch/05-inventory-foundation"
      },
      {
        id: "06-shipments-receiving",
        title: "06 · Shipments Receiving",
        path: "/pitch/06-shipments-receiving"
      }
    ]
  }
];

export function allScenesFlat(): SceneItem[] {
  return SCENE_GROUPS.flatMap((group) => group.items);
}
