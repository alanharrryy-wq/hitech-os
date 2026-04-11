import { PlaygroundPageClient } from "@components/playground/playground-page-client";
import { listSchemas } from "@/lib/core/schema-registry";

export default function PlaygroundPage() {
  const schemas = listSchemas();

  return <PlaygroundPageClient schemas={schemas} />;
}
