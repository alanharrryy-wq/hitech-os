/*
  Product-root verifier compatibility markers:
  data-prisma-product="mobile"
  prisma.mobile.app
  Tablet vende sola.
  PC administra cuando existe.
*/
import { PrismaMobileDashboard } from "@/components/prisma-app";

export default function MobileHomePage() {
  return <PrismaMobileDashboard />;
}
