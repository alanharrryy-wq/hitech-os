import { listSchemas } from "@/lib/core/schema-registry";
import { getExternalStore } from "@/lib/store";

let bootstrapped = false;

export async function ensureTemplateBootstrap(): Promise<void> {
  if (bootstrapped) return;
  const store = getExternalStore();

  for (const schema of listSchemas()) {
    await store.ensureRecordType(schema.id, schema.title, schema.summary, schema.category, schema);
  }

  bootstrapped = true;
}

export function resetBootstrapFlagForTests() {
  bootstrapped = false;
}
