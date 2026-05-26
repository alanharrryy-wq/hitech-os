import type { ReactNode } from "react";
import { getPcRouteContract, PC_GROUP_LABELS } from "@/uiux/decision-model";
import { PcSubnav } from "./pc-subnav";

export function PcModuleShell({ currentPath, children }: { currentPath: string; children: ReactNode }) {
  const contract = getPcRouteContract(currentPath);

  return (
    <section className="card" data-prisma-component="PcModuleShell" data-pc-module={contract.group}>
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
