import { PrismaDarkSelector } from "@components/ui/prisma-dark-selector";
import { pcMessages } from "@/lib/i18n/messages/es";

export const metadata = {
  title: "Referencia Visual - PC",
  description: "Visual reference for the Prisma dark selector"
};

export default function ReferenciaVisualPage() {
  return (
    <div className="referencia-visual-container">
      <div className="referencia-visual-canvas">
        <div className="referencia-visual-demo">
          <h2 className="referencia-visual-label">Selector oscuro — referencia</h2>
          <PrismaDarkSelector />
        </div>
      </div>
    </div>
  );
}
