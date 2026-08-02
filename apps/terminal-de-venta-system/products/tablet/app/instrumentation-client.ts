const PRISMA_CHUNK_SESSION_KEY = "prisma.zero-idle.chunk-recovery.v1";

type PrismaChunkSignal = "ChunkLoadError" | "Failed to load chunk" | "_next/static/chunks";
type PrismaChunkSource = "window.error" | "unhandledrejection";

let emittedInThisDocument = false;

function classifyChunkFailure(value: unknown): PrismaChunkSignal | null {
  const text =
    value instanceof Error
      ? `${value.name} ${value.message} ${value.stack ?? ""}`
      : typeof value === "string"
        ? value
        : String(value ?? "");

  if (text.includes("ChunkLoadError")) return "ChunkLoadError";
  if (text.includes("Failed to load chunk")) return "Failed to load chunk";
  if (text.includes("_next/static/chunks")) return "_next/static/chunks";
  return null;
}

function reportChunkFailure(signal: PrismaChunkSignal, source: PrismaChunkSource) {
  if (emittedInThisDocument) return;
  try {
    if (sessionStorage.getItem(PRISMA_CHUNK_SESSION_KEY) === "reported") return;
    sessionStorage.setItem(PRISMA_CHUNK_SESSION_KEY, "reported");
  } catch {
    // The module-level gate still prevents a loop when storage is unavailable.
  }
  emittedInThisDocument = true;

  void fetch("/api/runtime-evidence/chunk-load", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      schemaVersion: "prisma-passive-chunk-beacon/v1",
      signal,
      source
    }),
    cache: "no-store",
    keepalive: true,
    credentials: "same-origin"
  })
    .catch(() => undefined)
    .finally(() => {
      window.location.reload();
    });
}

window.addEventListener("error", (event) => {
  const signal = classifyChunkFailure(
    `${event.message ?? ""} ${event.filename ?? ""} ${String(event.error ?? "")}`
  );
  if (signal) reportChunkFailure(signal, "window.error");
});

window.addEventListener("unhandledrejection", (event) => {
  const signal = classifyChunkFailure(event.reason);
  if (signal) reportChunkFailure(signal, "unhandledrejection");
});
