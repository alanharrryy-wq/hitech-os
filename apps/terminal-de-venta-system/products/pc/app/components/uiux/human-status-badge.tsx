import { humanizePcStatus } from "@/uiux/status-translator";

const SEVERITY_CLASS: Record<ReturnType<typeof humanizePcStatus>["severity"], string> = {
  info: "chip",
  attention: "chip chip-warning",
  critical: "chip chip-danger",
  blocking: "chip chip-danger",
  demo: "chip chip-demo",
  technical: "chip chip-technical"
};

export function HumanStatusBadge({ status, label }: { status: string; label?: string }) {
  const human = humanizePcStatus(status);
  return (
    <span className={SEVERITY_CLASS[human.severity] ?? "chip"} data-prisma-component="HumanStatusBadge" data-status-severity={human.severity}>
      {label ? `${label}: ` : null}{human.label}
    </span>
  );
}
