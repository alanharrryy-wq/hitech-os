import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function InlineAlert({ tone, title, description, note }: { tone: "ok" | "warn" | "danger"; title: ReactNode; description: ReactNode; note?: ReactNode }) {
  return (
    <section className={cn("inline-alert", tone)}>
      <div className="inline-alert-copy">
        <strong>{title}</strong>
        <div className="subtle">{description}</div>
      </div>
      {note ? <div className="inline-alert-note">{note}</div> : null}
    </section>
  );
}
