import type { Meta, StoryObj } from "@storybook/react";
import { useState } from "react";
import { {{COMPONENT_NAME}} } from "./{{COMPONENT_NAME}}";

const meta: Meta<typeof {{COMPONENT_NAME}}> = {
  title: "Generated/Controls/{{COMPONENT_NAME}}",
  component: {{COMPONENT_NAME}},
  args: {
    label: "{{COMPONENT_NAME}}",
    hint: "Generated {{CONTROL_KIND}} control",
    min: 0,
    max: 100,
    step: 1,
    value: 42
  }
};

export default meta;
type Story = StoryObj<typeof {{COMPONENT_NAME}}>;

export const Default: Story = {
  render: (args) => {
    const [value, setValue] = useState(Number(args.value));
    return <{{COMPONENT_NAME}} {...args} value={value} onChange={setValue} />;
  }
};

