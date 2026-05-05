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

const SettingsModule: TwinModuleManifest = {
  key: "settings",
  route: "/settings",
  title: "Ajustes",
  description: "Políticas, terminales, permisos y reglas sin conexión.",
  navGroup: "operation"
};

export const pcModuleRegistry: TwinModuleManifest[] = sortModules([
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
  SettingsModule
]);
