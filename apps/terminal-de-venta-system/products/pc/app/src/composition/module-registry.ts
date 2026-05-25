import type { TwinModuleManifest } from "@shared-kernel/types/module";
import { sortModules } from "@shared-kernel/runtime/module-registry";
import { CatalogModule } from "@/modules/catalog/module.manifest";
import { StockModule } from "@/modules/stock/module.manifest";
import { CountsModule } from "@/modules/counts/module.manifest";
import { PurchasingModule } from "@/modules/purchasing/module.manifest";
import { ReceivingModule } from "@/modules/receiving/module.manifest";
import { ReplenishmentModule } from "@/modules/replenishment/module.manifest";
import { SuppliersModule } from "@/modules/suppliers/module.manifest";
import { AuditModule } from "@/modules/audit/module.manifest";
import { SyncModule } from "@/modules/sync/module.manifest";

const MovementsModule: TwinModuleManifest = {
  key: "movements",
  route: "/movements",
  title: "Movimientos",
  description: "Entradas, salidas, ajustes y trazabilidad de inventario.",
  navGroup: "control"
};

const SalesControlModule: TwinModuleManifest = {
  key: "sales-control",
  route: "/sales-control",
  title: "Ventas / Caja",
  description: "Ventas consolidadas, tickets, KPIs y detalle de auditoria.",
  navGroup: "control"
};

const CashSessionsModule: TwinModuleManifest = {
  key: "cash-sessions",
  route: "/cash-sessions",
  title: "Cortes de caja",
  description: "Sesiones de caja, movimientos, esperado, contado y variaciones.",
  navGroup: "control"
};

const DevicesModule: TwinModuleManifest = {
  key: "devices",
  route: "/devices",
  title: "Dispositivos",
  description: "Fleet de Tablets, heartbeats, frescura, outbox y licencias.",
  navGroup: "control"
};

const LicenseRuntimeModule: TwinModuleManifest = {
  key: "license-runtime",
  route: "/license-runtime",
  title: "Licencias y Runtime",
  description: "Licencia PC, estados Tablet, refresh remoto y readiness.",
  navGroup: "operation"
};

const TabletCommunicationModule: TwinModuleManifest = {
  key: "tablet-communication",
  route: "/tablet-communication",
  title: "Comunicacion Tablet",
  description: "Inbound Tablet-to-PC, gobierno PC-to-Tablet y acks observables.",
  navGroup: "control"
};

const DataQualityModule: TwinModuleManifest = {
  key: "data-quality",
  route: "/data-quality",
  title: "Calidad de datos",
  description: "Integridad canonica, folios, pagos, caja, sync y heartbeat.",
  navGroup: "operation"
};

const SettingsModule: TwinModuleManifest = {
  key: "settings",
  route: "/settings",
  title: "Ajustes",
  description: "Políticas, terminales, permisos y reglas sin conexión.",
  navGroup: "operation"
};

export const pcModuleRegistry: TwinModuleManifest[] = sortModules([
  SalesControlModule,
  CashSessionsModule,
  CatalogModule,
  StockModule,
  MovementsModule,
  CountsModule,
  PurchasingModule,
  ReceivingModule,
  ReplenishmentModule,
  SuppliersModule,
  AuditModule,
  SyncModule,
  DevicesModule,
  TabletCommunicationModule,
  LicenseRuntimeModule,
  DataQualityModule,
  SettingsModule
]);
