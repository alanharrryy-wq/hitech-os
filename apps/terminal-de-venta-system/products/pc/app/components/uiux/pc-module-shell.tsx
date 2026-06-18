import type { ReactNode } from "react";
import { getPcRouteContract, PC_GROUP_LABELS } from "@/uiux/decision-model";
import { PcSubnav } from "./pc-subnav";

const PRISMA_PC_ROUTE_PANELS: Record<string, string> = {
  "/catalog": "pc.catalog",
  "/dashboard": "pc.dashboard",
  "/settings": "pc.settings",
  "/stock": "pc.stock"
};

export function PcModuleShell({ currentPath, children }: { currentPath: string; children: ReactNode }) {
  const contract = getPcRouteContract(currentPath);
  const prismaPanelId = PRISMA_PC_ROUTE_PANELS[currentPath] ?? "pc.workspace";

  return (
    <section
      className="card"
      data-prisma-panel={prismaPanelId}
      data-prisma-surface="pc"
      data-prisma-route={currentPath}
      data-prisma-component="PcModuleShell"
      data-pc-module={contract.group}
    >
      <div className="section-head">
        <div>
          <div className="kicker">{PC_GROUP_LABELS[contract.group]}</div>
          <h2 className="section-title">{contract.primaryQuestion}</h2>
          <div className="section-copy">{contract.subtitle}</div>
        </div>
      </div>
      <PcSubnav currentPath={currentPath} />
      <div style={{ marginTop: 16 }}>{children}</div>
    </section>
  );
}
