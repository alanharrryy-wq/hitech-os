import {PrismaTabletShellUnified,TabletShellStatusPill} from "@components/tablet-shell/prisma-tablet-shell";
import {TabletOperableReleaseGateScreen} from "@components/release-gate/tablet-operable-release-gate-screen";
import {buildReleaseGateSnapshot} from "@/server/operable-release-gate";
import {buildReleaseGateViewModel} from "@/lib/operable-release-gate/release-gate-view-model";
export default function ReleaseGatePage(){const model=buildReleaseGateViewModel(buildReleaseGateSnapshot());return <PrismaTabletShellUnified currentPath="/release-gate" title="Estado del sistema" subtitle="Cierre operativo de la ola Tablet antes de liberar." kicker="Release gate Tablet" status={<TabletShellStatusPill tone={model.status==="ready"?"ok":model.status==="attention"?"warn":"danger"}>{model.statusLabel}</TabletShellStatusPill>}><TabletOperableReleaseGateScreen model={model}/></PrismaTabletShellUnified>}
