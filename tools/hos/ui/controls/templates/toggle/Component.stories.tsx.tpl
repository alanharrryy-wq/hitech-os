import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";
import { {{COMPONENT_NAME}} } from "./{{COMPONENT_NAME}}";

const meta: Meta<typeof {{COMPONENT_NAME}}> = {
  title: "Generated/Controls/{{COMPONENT_NAME}}",
  component: {{COMPONENT_NAME}},
  args: {
    label: "{{COMPONENT_NAME}}",
    hint: "Generated {{CONTROL_KIND}} control",
    checked: false
  }
};

export default meta;
type Story = StoryObj<typeof {{COMPONENT_NAME}}>;

export const Default: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(Boolean(args.checked));
    return (
      <{{COMPONENT_NAME}}
        {...args}
        checked={checked}
        onChange={(next) => setChecked(next)}
      />
    );
  }
};

