import { LocalAdapter } from "@/lib/adapters/local-adapter";
import { RestAdapter } from "@/lib/adapters/rest-adapter";
import { type ExternalAdapter } from "@/lib/adapters/types";
import { WebhookAdapter } from "@/lib/adapters/webhook-adapter";

const adapters: ExternalAdapter[] = [new LocalAdapter(), new RestAdapter(), new WebhookAdapter()];

const adapterMap = new Map(adapters.map((adapter) => [adapter.id, adapter]));

export function listAdapters(): ExternalAdapter[] {
  return adapters;
}

export function getAdapter(adapterId: string): ExternalAdapter {
  const adapter = adapterMap.get(adapterId);
  if (!adapter) {
    throw new Error(`Adapter '${adapterId}' is not registered`);
  }
  return adapter;
}
