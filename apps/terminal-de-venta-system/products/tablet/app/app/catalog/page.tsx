import { CatalogStockSellingAssistScreen } from "@components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen";

export const metadata = {
  title: "Catálogo que sí vende - PRISMA Tablet",
  description: "Búsqueda operativa de productos con detalle, existencias y envío al carrito local de venta."
};

export default function CatalogPage() {
  return <CatalogStockSellingAssistScreen mode="catalog" />;
}
