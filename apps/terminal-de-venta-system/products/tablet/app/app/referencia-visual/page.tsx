import { PrismaDarkSelector } from "@components/ui/prisma-dark-selector";
import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletGenericSurfaceV2 } from "@components/tablet-visual-v2";
import { tabletMessages } from "@/lib/i18n/messages/es";

export const metadata = {
  title: "Referencia Visual - Tablet",
  description: "Visual reference for the Prisma dark selector"
};

export default function ReferenciaVisualPage() {
  return (
    <PrismaTabletShellUnified
      currentPath="/referencia-visual"
      title="Referencia visual"
      subtitle={tabletMessages.metadata.description}
      kicker="Referencia Tablet"
    >
      <TabletGenericSurfaceV2 routeId="/referencia-visual" title="Referencia visual" description={tabletMessages.metadata.description} statusLabel="Referencia">
        <div className="referencia-visual-container">
          <div className="referencia-visual-canvas">
            <div className="referencia-visual-demo">
              <h2 className="referencia-visual-label">Selector oscuro — referencia</h2>
              <PrismaDarkSelector />
            </div>
          </div>
        </div>
      </TabletGenericSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
