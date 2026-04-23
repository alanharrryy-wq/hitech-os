import type { TwinModuleManifest } from "@shared-kernel/types/module";
import { sortModules } from "@shared-kernel/runtime/module-registry";
import { CatalogModule } from "@/modules/catalog/module.manifest";
import { StockModule } from "@/modules/stock/module.manifest";
import { CountsModule } from "@/modules/counts/module.manifest";
import { PurchasingModule } from "@/modules/purchasing/module.manifest";
import { ReceivingModule } from "@/modules/receiving/module.manifest";
import { ReplenishmentModule } from "@/modules/replenishment/module.manifest";
import { AuditModule } from "@/modules/audit/module.manifest";
import { SyncModule } from "@/modules/sync/module.manifest";

export const pcModuleRegistry: TwinModuleManifest[] = sortModules([
  CatalogModule,
  StockModule,
  CountsModule,
  PurchasingModule,
  ReceivingModule,
  ReplenishmentModule,
  AuditModule,
  SyncModule
]);
