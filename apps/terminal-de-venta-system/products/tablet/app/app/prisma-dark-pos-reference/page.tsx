import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { PrismaSoftCard, PrismaStatusChip, TabletGenericSurfaceV2 } from "@components/tablet-visual-v2";

export const metadata = {
  title: "PRISMA Dark POS Reference - Tablet",
  description: "Referencia visual PRISMA Dark POS para tablet"
};

export default function PrismaDarkPosReferencePage() {
  return (
    <PrismaTabletShellUnified
      currentPath="/prisma-dark-pos-reference"
      title="Referencia POS"
      subtitle="Referencia visual aislada del POS para comparar estados sin tocar venta."
      kicker="Referencia Tablet"
    >
      <TabletGenericSurfaceV2 routeId="/prisma-dark-pos-reference" title="Referencia POS" description="Referencia visual aislada del POS para comparar estados sin tocar venta." statusLabel="Referencia">
        <PrismaSoftCard as="article" data-prisma-role="status-surface">
          <PrismaStatusChip tone="warning">Referencia histórica aislada</PrismaStatusChip>
          <h2>Shell oscuro retirado de la composición activa</h2>
          <p>Esta ruta conserva la referencia documental sin montar un segundo shell completo dentro de Tablet.</p>
        </PrismaSoftCard>
      </TabletGenericSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
