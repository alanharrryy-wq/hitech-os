import { Badge } from "@components/ui/badge";

type Tone = "ok" | "warn" | "danger";

export function StatusBadge({ value }: { value: string }) {
  const normalized = value.toLowerCase();
  let tone: Tone = "ok";
  if (["failed", "fallido", "conflict", "crítico", "critico", "rejected"].some((item) => normalized.includes(item))) tone = "danger";
  if (["pending", "pendiente", "riesgo", "partial", "parcial", "warning"].some((item) => normalized.includes(item))) tone = "warn";
  return <Badge tone={tone}>{value}</Badge>;
}
