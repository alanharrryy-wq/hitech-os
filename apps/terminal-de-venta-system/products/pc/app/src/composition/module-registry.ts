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
  title: "Ventas",
  description: "Ventas, dinero, tickets y cortes antes de cerrar operación.",
  navGroup: "control"
};

const CashSessionsModule: TwinModuleManifest = {
  key: "cash-sessions",
  route: "/cash-sessions",
  title: "Cortes de caja",
  description: "Cortes, movimientos, esperado, contado y diferencias.",
  navGroup: "control"
};

const DevicesModule: TwinModuleManifest = {
  key: "devices",
  route: "/devices",
  title: "Equipos",
  description: "Equipos conectados, pulso reciente, pendientes y licencias.",
  navGroup: "control"
};

const LicenseRuntimeModule: TwinModuleManifest = {
  key: "license-runtime",
  route: "/license-runtime",
  title: "Licencia",
  description: "Funciones disponibles, licencia activa y estado de equipos.",
  navGroup: "operation"
};

const TabletCommunicationModule: TwinModuleManifest = {
  key: "tablet-communication",
  route: "/tablet-communication",
  title: "Tablet",
  description: "Comunicación entre PC y tablet, cambios pendientes y confirmaciones.",
  navGroup: "control"
};

const DataQualityModule: TwinModuleManifest = {
  key: "data-quality",
  route: "/data-quality",
  title: "Revisión de datos",
  description: "Datos incompletos, códigos repetidos, pagos, caja y sincronización.",
  navGroup: "operation"
};

const SettingsModule: TwinModuleManifest = {
  key: "settings",
  route: "/settings",
  title: "Configuración",
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
