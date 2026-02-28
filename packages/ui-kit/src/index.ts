export { Button } from "./components/Button.js";
export type { ButtonProps } from "./components/Button.js";

export { Card } from "./components/Card.js";
export type { CardProps } from "./components/Card.js";

export { Section } from "./components/Section.js";
export type { SectionProps } from "./components/Section.js";

export { Text } from "./components/Text.js";
export type { TextProps } from "./components/Text.js";

export const UI_KIT_REQUIRED_COMPONENT_EXPORTS = Object.freeze(["Button", "Card", "Section", "Text"]);

export const UI_KIT_LAYERS_MODULE_PATH = "./layers/index.js";
export const UI_KIT_LAYERS_IDS_MODULE_PATH = "./layers/layerIds.js";
export const UI_KIT_LAYERS_CSS_PATH = "./layers.css";

export interface UiKitLayersWiring {
  readonly modulePath: string;
  readonly idsModulePath: string;
  readonly cssPath: string;
  loadModule(): Promise<unknown>;
  loadIdsModule(): Promise<unknown>;
}

export const layers: UiKitLayersWiring = Object.freeze({
  modulePath: UI_KIT_LAYERS_MODULE_PATH,
  idsModulePath: UI_KIT_LAYERS_IDS_MODULE_PATH,
  cssPath: UI_KIT_LAYERS_CSS_PATH,
  loadModule: () => import(UI_KIT_LAYERS_MODULE_PATH),
  loadIdsModule: () => import(UI_KIT_LAYERS_IDS_MODULE_PATH)
});
