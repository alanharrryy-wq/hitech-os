export type PrismaAppSectionId =
  | "hoy"
  | "ventas"
  | "caja"
  | "inventario"
  | "alertas"
  | "reportes"
  | "multisucursal";

export type PrismaAppSection = {
  id: PrismaAppSectionId;
  label: string;
  eyebrow: string;
  title: string;
  description: string;
  clientValue: string;
  primaryQuestion: string;
  routeHash: string;
  status: "base" | "pro" | "advanced";
};

export type PrismaAppHealth = "sano" | "revisar" | "urgente" | "offline";
export type PrismaAppSeverity = "critica" | "alta" | "media" | "info";
export type PrismaAppTone = "gold" | "green" | "blue" | "red" | "neutral";

export type PrismaAppKpi = {
  label: string;
  value: string;
  note: string;
  tone: PrismaAppTone;
};

export type PrismaAppAction = {
  title: string;
  detail: string;
  owner: string;
  priority: "alta" | "media" | "baja";
};

export type PrismaAppSalesPoint = {
  hour: string;
  label: string;
  amount: string;
  height: string;
};

export type PrismaAppAlert = {
  id: string;
  severity: PrismaAppSeverity;
  area: string;
  title: string;
  detail: string;
  time: string;
  action: string;
};

export type PrismaAppInventoryItem = {
  sku: string;
  name: string;
  category: string;
  stock: string;
  movement: string;
  state: "critico" | "reponer" | "normal" | "sobrestock";
};

export type PrismaAppReportCard = {
  title: string;
  value: string;
  detail: string;
  footnote: string;
};

export type PrismaAppBranch = {
  name: string;
  status: PrismaAppHealth;
  salesToday: string;
  salesDelta: string;
  cashState: string;
  alerts: number;
  syncLag: string;
  tickets: number;
};
