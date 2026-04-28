export type PrismaIconName =
  | "arrow-left"
  | "arrow-right"
  | "bell"
  | "box"
  | "briefcase"
  | "broom"
  | "cart"
  | "chart"
  | "chevron-down"
  | "credit-card"
  | "dashboard"
  | "grid"
  | "milk"
  | "minus"
  | "more"
  | "package"
  | "plus"
  | "receipt"
  | "save"
  | "scan"
  | "search"
  | "settings"
  | "sparkle"
  | "star"
  | "sun"
  | "tag"
  | "terminal"
  | "trash"
  | "truck"
  | "user"
  | "users"
  | "wallet"
  | "x";

export type ProductVisual = "coke" | "sabritas" | "lala" | "ciel" | "nescafe" | "bimbo" | "ace" | "zucaritas";
export type ProductShape = "bottle" | "bag" | "carton" | "jar" | "bread" | "detergent" | "box";

export type Product = {
  id: string;
  name: string;
  price: string;
  stock: string;
  favorite: boolean;
  visual: ProductVisual;
  shape: ProductShape;
  badge: string;
  detail: string;
  glow: "red" | "gold" | "white" | "blue" | "brown" | "amber" | "orange";
};

export type CartItem = {
  index: number;
  productId: string;
  name: string;
  unitPrice: string;
  quantity: number;
  total: string;
};

export const navItems: Array<{ label: string; icon: PrismaIconName; active?: boolean }> = [
  { label: "Ventas", icon: "cart", active: true },
  { label: "Dashboard", icon: "dashboard" },
  { label: "Inventario", icon: "package" },
  { label: "Clientes", icon: "users" },
  { label: "Productos", icon: "tag" },
  { label: "Compras", icon: "truck" },
  { label: "Caja", icon: "wallet" },
  { label: "Reportes", icon: "chart" },
  { label: "Gastos", icon: "receipt" },
  { label: "Promociones", icon: "sparkle" },
  { label: "Usuarios", icon: "user" },
  { label: "Configuración", icon: "settings" }
];

export const categories: Array<{ label: string; icon: PrismaIconName; active?: boolean }> = [
  { label: "Todos", icon: "grid", active: true },
  { label: "Bebidas", icon: "briefcase" },
  { label: "Snacks", icon: "package" },
  { label: "Lácteos", icon: "milk" },
  { label: "Abarrotes", icon: "box" },
  { label: "Limpieza", icon: "broom" },
  { label: "Personal", icon: "user" }
];

export const products: Product[] = [
  {
    id: "coca-cola-600",
    name: "Coca Cola 600 ml",
    price: "$18.00",
    stock: "Stock: 156",
    favorite: true,
    visual: "coke",
    shape: "bottle",
    badge: "COCA",
    detail: "600 ml",
    glow: "red"
  },
  {
    id: "sabritas-original-45",
    name: "Sabritas Original 45 g",
    price: "$15.00",
    stock: "Stock: 142",
    favorite: false,
    visual: "sabritas",
    shape: "bag",
    badge: "SAB",
    detail: "45 g",
    glow: "gold"
  },
  {
    id: "lala-entera-1",
    name: "Leche Lala Entera 1 L",
    price: "$28.50",
    stock: "Stock: 98",
    favorite: false,
    visual: "lala",
    shape: "carton",
    badge: "LALA",
    detail: "1 L",
    glow: "white"
  },
  {
    id: "agua-ciel-1",
    name: "Agua Ciel 1 L",
    price: "$16.00",
    stock: "Stock: 83",
    favorite: false,
    visual: "ciel",
    shape: "bottle",
    badge: "CIEL",
    detail: "1 L",
    glow: "blue"
  },
  {
    id: "nescafe-clasico-200",
    name: "Nescafé Clásico 200 g",
    price: "$145.00",
    stock: "Stock: 42",
    favorite: false,
    visual: "nescafe",
    shape: "jar",
    badge: "NES",
    detail: "200 g",
    glow: "brown"
  },
  {
    id: "pan-bimbo-blanco",
    name: "Pan Bimbo Blanco Grande",
    price: "$34.00",
    stock: "Stock: 87",
    favorite: true,
    visual: "bimbo",
    shape: "bread",
    badge: "BIMBO",
    detail: "Grande",
    glow: "amber"
  },
  {
    id: "ace-1",
    name: "Ace 1 kg",
    price: "$38.50",
    stock: "Stock: 28",
    favorite: false,
    visual: "ace",
    shape: "detergent",
    badge: "ACE",
    detail: "1 kg",
    glow: "orange"
  },
  {
    id: "zucaritas-730",
    name: "Zucaritas Kellogg's 730 g",
    price: "$67.00",
    stock: "Stock: 31",
    favorite: false,
    visual: "zucaritas",
    shape: "box",
    badge: "ZUC",
    detail: "730 g",
    glow: "blue"
  }
];

export const cartItems: CartItem[] = [
  { index: 1, productId: "coca-cola-600", name: "Coca Cola 600 ml", unitPrice: "$18.00", quantity: 2, total: "$36.00" },
  { index: 2, productId: "sabritas-original-45", name: "Sabritas Original 45 g", unitPrice: "$15.00", quantity: 1, total: "$15.00" },
  { index: 3, productId: "lala-entera-1", name: "Leche Lala Entera 1 L", unitPrice: "$28.50", quantity: 1, total: "$28.50" },
  { index: 4, productId: "pan-bimbo-blanco", name: "Pan Bimbo Blanco Grande", unitPrice: "$34.00", quantity: 1, total: "$34.00" }
];
