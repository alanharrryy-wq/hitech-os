import type { ComponentProps } from "react";
import { Panel } from "./layout/Panel.js";

export type CardProps = ComponentProps<typeof Panel>;

export function Card(props: CardProps) {
  return <Panel {...props} />;
}
