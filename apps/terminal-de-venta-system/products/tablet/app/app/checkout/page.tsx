import { PosScreen } from "@components/pos/pos-screen";

export const metadata = {
  title: "Cobro unificado - PRISMA Tablet",
  description: "El cobro usa el mismo motor del POS para evitar dos flujos de venta."
};

export default function CheckoutPage() {
  return <PosScreen />;
}
