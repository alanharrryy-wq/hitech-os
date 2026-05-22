"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { CommandAction } from "@/server/services/pc-command-center.service";

type ActionState = {
  busyKey: string | null;
  ok: string | null;
  error: string | null;
};

function isPost(action: CommandAction) {
  return (action.method ?? "GET").toUpperCase() === "POST";
}

async function runPostAction(action: CommandAction) {
  const response = await fetch(action.href, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(action.body ?? {})
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok || payload?.ok === false) {
    const message = typeof payload?.message === "string" ? payload.message : typeof payload?.error === "string" ? payload.error : `HTTP ${response.status}`;
    throw new Error(message);
  }
  return payload;
}

export function PcCommandActions({ actions }: { actions: CommandAction[] }) {
  const router = useRouter();
  const [state, setState] = useState<ActionState>({ busyKey: null, ok: null, error: null });

  async function run(action: CommandAction) {
    const key = `${action.label}:${action.href}`;
    setState({ busyKey: key, ok: null, error: null });
    try {
      await runPostAction(action);
      setState({ busyKey: null, ok: action.successMessage ?? `${action.label} completado.`, error: null });
      router.refresh();
    } catch (error) {
      setState({ busyKey: null, ok: null, error: error instanceof Error ? error.message : "Accion no completada." });
    }
  }

  return (
    <>
      <div className="dashboard-actions">
        {actions.map((action) => {
          const key = `${action.label}:${action.href}`;
          if (action.disabledReason) {
            return <span key={key} className="footer-chip" title={action.disabledReason}>{action.label}: {action.disabledReason}</span>;
          }
          if (!isPost(action)) {
            return <a key={key} className="footer-chip" href={action.href}>{action.label}</a>;
          }
          return (
            <button
              key={key}
              className="footer-chip"
              type="button"
              onClick={() => void run(action)}
              disabled={Boolean(state.busyKey)}
              aria-busy={state.busyKey === key}
            >
              {state.busyKey === key ? "Ejecutando" : action.label}
            </button>
          );
        })}
      </div>
      {state.ok ? <div className="alert-strip" role="status"><strong>Accion aplicada</strong><span className="subtle">{state.ok}</span></div> : null}
      {state.error ? <div className="alert-strip" role="alert"><strong>No se completo</strong><span className="subtle">{state.error}</span></div> : null}
    </>
  );
}
