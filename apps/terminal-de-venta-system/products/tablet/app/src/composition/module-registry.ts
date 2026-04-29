import type { TwinModuleManifest } from "@shared-kernel/types/module";
import { sortModules } from "@shared-kernel/runtime/module-registry";
import { PosModule } from "@/modules/pos/module.manifest";
import { SalesModule } from "@/modules/sales/module.manifest";
import { CheckoutModule } from "@/modules/checkout/module.manifest";
import { ShiftModule } from "@/modules/shift/module.manifest";
import { ReturnsModule } from "@/modules/returns/module.manifest";
import { StockModule } from "@/modules/stock/module.manifest";
import { SyncModule } from "@/modules/sync/module.manifest";

export const tabletModuleRegistry: TwinModuleManifest[] = sortModules([
  PosModule,
  SalesModule,
  CheckoutModule,
  ShiftModule,
  ReturnsModule,
  StockModule,
  SyncModule
]);
