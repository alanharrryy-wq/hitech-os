import type { ReactNode } from "react";

export function FlowContextStack({ children }: { children: ReactNode }) {
  return <div className="flow-context-stack">{children}</div>;
}
