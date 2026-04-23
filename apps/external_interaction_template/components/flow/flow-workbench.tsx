import type { ReactNode } from "react";

export function FlowWorkbench({
  main,
  context
}: {
  main: ReactNode;
  context: ReactNode;
}) {
  return (
    <section className="flow-workbench">
      <div className="flow-workbench-main">{main}</div>
      <aside className="flow-workbench-context">{context}</aside>
    </section>
  );
}
