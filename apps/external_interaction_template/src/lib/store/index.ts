import { MemoryExternalStore } from "@/lib/store/memory-store";
import { PrismaExternalStore } from "@/lib/store/prisma-store";
import { type ExternalStore } from "@/lib/store/types";

let singleton: ExternalStore | null = null;

export function getExternalStore(): ExternalStore {
  if (singleton) return singleton;

  if (process.env.EXTERNAL_TEMPLATE_STORE === "memory") {
    singleton = new MemoryExternalStore();
    return singleton;
  }

  singleton = new PrismaExternalStore();
  return singleton;
}

export function setExternalStoreForTests(store: ExternalStore | null) {
  singleton = store;
}
