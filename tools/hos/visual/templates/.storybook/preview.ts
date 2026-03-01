import type { Preview } from "@storybook/react";

const preview: Preview = {
  parameters: {
    controls: { expanded: true },
    options: { storySort: { method: "alphabetical" } },
    backgrounds: { disable: true },
    layout: "fullscreen"
  },
  decorators: [
    (Story) => {
      return (
        <div data-visual-deterministic="1" style={{ animation: "none", transition: "none" }}>
          <Story />
        </div>
      );
    }
  ]
};

export default preview;

