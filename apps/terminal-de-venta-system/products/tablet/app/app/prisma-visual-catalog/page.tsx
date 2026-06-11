import { PrismaActionButton, PrismaMetricCard, PrismaRouteFrame, PrismaStateBanner, PrismaSurfacePanel } from "../../../../shared-ui/prisma/components";

export default function PrismaVisualCatalogPilotPage() {
  return (
    <PrismaRouteFrame surface="tablet" aria-labelledby="prisma-visual-catalog-title">
      <PrismaStateBanner surface="tablet" tone="success" title="Catálogo PRISMA conectado">
        Esta ruta piloto consume componentes reales desde products/shared-ui/prisma sin tocar POS ni checkout.
      </PrismaStateBanner>
      <PrismaSurfacePanel surface="tablet" eyebrow="Homologación" title="PRISMA Visual Catalog" id="prisma-visual-catalog-title">
        <p>Flujo gobernado: adapter, route frame, shell, background contract, components, tokens, recipes y validators.</p>
        <PrismaMetricCard surface="tablet" label="Componentes" value="13" delta="live shared-ui" />
        <PrismaMetricCard surface="tablet" label="Superficies" value="4+" delta="actuales y futuras" />
        <PrismaActionButton surface="tablet" href="/">Volver al inicio</PrismaActionButton>
      </PrismaSurfacePanel>
    </PrismaRouteFrame>
  );
}
