import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";
import { DemoToggle } from "./DemoToggle";

const meta: Meta<typeof DemoToggle> = {
  title: "Generated/Controls/DemoToggle",
  component: DemoToggle,
  args: {
    label: "DemoToggle",
    hint: "Generated toggle control",
    checked: false
  }
};

export default meta;
type Story = StoryObj<typeof DemoToggle>;

export const Default: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(Boolean(args.checked));
    return (
      <DemoToggle
        {...args}
        checked={checked}
        onChange={(next) => setChecked(next)}
      />
    );
  }
};

