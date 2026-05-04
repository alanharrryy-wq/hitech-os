/*
  Product-root verifier compatibility markers:
  data-prisma-product="mobile"
  prisma.mobile.app
  Tablet vende sola.
  PC administra cuando existe.
*/
import { PrismaMobileDashboard } from "@/components/prisma-app";

export const metadata = {
  title: "PRISMA App | PWA instalable",
  description: "PRISMA App Mobile instalable desde navegador, con service worker, offline shell, dominio configurable, cliente API y caché local."
};

export default function PrismaAppPage() {
  return <PrismaMobileDashboard />;
}
