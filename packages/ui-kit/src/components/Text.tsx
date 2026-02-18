import type { PropsWithChildren } from "react";

export interface TextProps {
  tone?: "default" | "muted" | "success" | "danger";
  as?: "p" | "span" | "small";
}

export function Text({ children, tone = "default", as = "p" }: PropsWithChildren<TextProps>) {
  const Tag = as;
  return <Tag className={`ui-text ui-text--${tone}`}>{children}</Tag>;
}
