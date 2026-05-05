export function Badge({ tone, children }: { tone: "ok" | "warn" | "danger"; children: any }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
