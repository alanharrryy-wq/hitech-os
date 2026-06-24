import { notFound } from "next/navigation";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletOperableReleaseGateScreen } from "@components/release-gate/tablet-operable-release-gate-screen";
import { buildReleaseGateSnapshot } from "@/server/operable-release-gate";
import { buildReleaseGateViewModel } from "@/lib/operable-release-gate/release-gate-view-model";

export default function ReleaseGatePage() {
  if (process.env.PRISMA_TABLET_INTERNAL_TOOLING !== "1") {
    notFound();
  }

  const model = buildReleaseGateViewModel(buildReleaseGateSnapshot());
  return (
    <PrismaTabletShellUnified
      currentPath="/release-gate"
      title="Release Gate"
      subtitle="Herramienta interna protegida para cierre operativo."
      kicker="Tooling interno Tablet"
      status={<TabletShellStatusPill tone={model.status === "ready" ? "ok" : model.status === "attention" ? "warn" : "danger"}>{model.statusLabel}</TabletShellStatusPill>}
    >
      <TabletOperableReleaseGateScreen model={model} />
    </PrismaTabletShellUnified>
  );
}
