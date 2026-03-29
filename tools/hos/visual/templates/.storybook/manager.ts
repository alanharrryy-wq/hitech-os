import { addons } from "@storybook/manager-api";
import { create } from "@storybook/theming/create";

addons.setConfig({
  theme: create({
    base: "light",
    brandTitle: "HITECH UI Lab",
    brandUrl: "https://example.invalid"
  }),
  panelPosition: "right",
  showPanel: true
});

