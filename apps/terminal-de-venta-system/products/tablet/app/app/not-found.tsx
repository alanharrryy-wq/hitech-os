import { AppShell } from "@components/layout/app-shell";
import { EmptyState } from "@components/ui/empty-state";
import { SectionCard } from "@components/ui/section-card";

export default function NotFound() {
  return (
    <AppShell currentPath="/">
      <EmptyState
        title="Esa ruta ya se nos fue al monte"
        description="La vista que buscaste no existe o cambió de lugar. Mejor vuelve al tablero y entra por navegación normal para no pisar un hoyo invisible."
      />
      <SectionCard title="Rutas que sí deben seguir vivas" subtitle="Chequeo corto para que la navegación no se vuelva lotería.">
        <div className="pill-row">
          <span className="signal-pill">/</span>
          <span className="signal-pill">/sales</span>
          <span className="signal-pill">/checkout</span>
          <span className="signal-pill">/shift</span>
          <span className="signal-pill">/returns</span>
          <span className="signal-pill">/sync</span>
          <span className="signal-pill">/stock</span>
        </div>
      </SectionCard>
    </AppShell>
  );
}
