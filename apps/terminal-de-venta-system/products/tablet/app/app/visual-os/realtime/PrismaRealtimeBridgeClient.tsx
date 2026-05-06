"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "../prisma-studio-pro-qa.module.css";
import {
  PRISMA_REALTIME_DEFAULT_URL,
  applyPrismaRealtimePayload,
  connectPrismaRealtime,
  createPrismaRealtimeClientId,
  type PrismaRealtimeStatus,
  type PrismaVisualRealtimePayload
} from "../../../src/visual-os/realtime/prisma-realtime-client";

export default function PrismaRealtimeBridgeClient() {
  const [serverUrl, setServerUrl] = useState(PRISMA_REALTIME_DEFAULT_URL);
  const [status, setStatus] = useState<PrismaRealtimeStatus>("idle");
  const [lastPayload, setLastPayload] = useState<PrismaVisualRealtimePayload | null>(null);
  const clientId = useMemo(() => createPrismaRealtimeClientId("studio-pro-bridge"), []);

  useEffect(() => {
    const disconnect = connectPrismaRealtime({
      serverUrl,
      clientId,
      onStatus: setStatus,
      onPayload: (payload) => {
        setLastPayload(payload);
        applyPrismaRealtimePayload(payload);
      }
    });
    return disconnect;
  }, [clientId, serverUrl]);

  return (
    <section className={styles.bridgeCard} data-prisma-layer="surface">
      <p className={styles.eyebrow}>00R/00S · Realtime Bridge</p>
      <h1>Bridge conectado</h1>
      <p>
        Esta pantalla escucha el broadcast SSE y aplica variables visuales en vivo. Si no cambia cuando mueves sliders, el canal está dormido, no iluminado por angelitos técnicos.
      </p>
      <label>
        Server URL
        <input value={serverUrl} onChange={(event) => setServerUrl(event.target.value)} />
      </label>
      <div className={styles.statusGrid}>
        <article data-status={status}><strong>{status}</strong><span>Estado</span></article>
        <article><strong>{lastPayload?.surface ?? "sin payload"}</strong><span>Superficie</span></article>
        <article><strong>{lastPayload?.recipeName ?? "sin receta"}</strong><span>Receta</span></article>
        <article><strong>{lastPayload?.score?.overall ?? "—"}</strong><span>Score</span></article>
      </div>
      <pre>{lastPayload ? JSON.stringify(lastPayload, null, 2) : "Esperando eventos SSE..."}</pre>
    </section>
  );
}
