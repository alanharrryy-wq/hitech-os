import type { ReactNode } from "react";
import { getPcRouteContract, getPrimaryRouteActions, buildEvidenceDrawerItems, getPcSubnavItems } from "@/uiux/decision-model";

export function PcRouteContractProvider({
  currentPath,
  children
}: {
  currentPath: string;
  children: (value: ReturnType<typeof getPcRouteContract> & {
    actions: ReturnType<typeof getPrimaryRouteActions>;
    evidence: ReturnType<typeof buildEvidenceDrawerItems>;
    subnav: ReturnType<typeof getPcSubnavItems>;
  }) => ReactNode;
}) {
  const contract = getPcRouteContract(currentPath);
  return (
    <>
      {children({
        ...contract,
        actions: getPrimaryRouteActions(currentPath),
        evidence: buildEvidenceDrawerItems(currentPath),
        subnav: getPcSubnavItems(currentPath)
      })}
    </>
  );
}
