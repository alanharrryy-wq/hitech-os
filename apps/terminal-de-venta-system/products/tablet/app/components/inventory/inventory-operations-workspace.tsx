"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { formatMoney, requestJson } from "@/lib/pos/cart-state";
import styles from "../catalog-stock-selling-assist/catalog-stock-selling-assist.module.css";

type ProductOption = { id: string; sku: string; name: string; stockOnHand: number };
type PurchaseOrder = { id: string; folio: string; supplierName: string; status: string; lines: Array<{ id: string; productId: string; sku: string; name: string; qtyRemaining: number }> };
type Snapshot = { purchaseOrders: PurchaseOrder[]; recentCounts: Array<{ id: string; variance: number; countedAt: string }> };
type OperationResult = { operationId: string; action: "adjust" | "count" | "receive"; deduplicated: boolean; affectedProducts: Array<{ name: string; beforeQty: number; afterQty: number }>; receipt?: { folio: string; totalCents: number } };

function errorMessage(error: unknown) {
  if (error && typeof error === "object" && "message" in error) return String((error as { message?: unknown }).message ?? "No se pudo operar inventario.");
  return "No se pudo operar inventario.";
}

function requestId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `inventory_${Date.now()}_${Math.random().toString(36).slice(2)}`;
}

export function InventoryOperationsWorkspace({ products, actorId, onCompleted }: { products: ProductOption[]; actorId: string; onCompleted: () => void }) {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<"adjust" | "count" | "receive">("adjust");
  const [snapshot, setSnapshot] = useState<Snapshot>({ purchaseOrders: [], recentCounts: [] });
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState("");
  const [purchaseOrderId, setPurchaseOrderId] = useState("");
  const [purchaseOrderLineId, setPurchaseOrderLineId] = useState("");
  const [state, setState] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const pendingRequestId = useRef<string | null>(null);

  const selectedOrder = snapshot.purchaseOrders.find((order) => order.id === purchaseOrderId) ?? snapshot.purchaseOrders[0] ?? null;
  const selectedLine = selectedOrder?.lines.find((line) => line.id === purchaseOrderLineId) ?? selectedOrder?.lines[0] ?? null;
  const selectedProduct = products.find((product) => product.id === productId) ?? products[0] ?? null;

  async function loadSnapshot() {
    try {
      const response = await requestJson<Snapshot>("/api/pos/inventory/operations");
      setSnapshot(response.data);
    } catch (error) {
      setMessage(errorMessage(error));
      setState("error");
    }
  }

  useEffect(() => {
    if (open) void loadSnapshot();
  }, [open]);

  const canSubmit = useMemo(() => {
    const qty = Number(quantity);
    if (!Number.isInteger(qty) || qty < 0 || !actorId) return false;
    if (mode === "receive") return Boolean(selectedOrder && selectedLine && qty > 0);
    if (!selectedProduct) return false;
    return mode === "count" || reason.trim().length >= 3;
  }, [actorId, mode, quantity, reason, selectedLine, selectedOrder, selectedProduct]);

  async function submit() {
    if (!canSubmit) return;
    const clientRequestId = pendingRequestId.current ?? requestId();
    pendingRequestId.current = clientRequestId;
    const qty = Number(quantity);
    const body = mode === "adjust"
      ? { action: mode, actorId, clientRequestId, productId: selectedProduct!.id, targetQty: qty, reason }
      : mode === "count"
        ? { action: mode, actorId, clientRequestId, lines: [{ productId: selectedProduct!.id, countedQty: qty }], reason: reason || "Conteo físico Tablet" }
        : { action: mode, actorId, clientRequestId, purchaseOrderId: selectedOrder!.id, lines: [{ purchaseOrderLineId: selectedLine!.id, qtyReceived: qty }], reference: reason || null };
    setState("loading");
    setMessage("");
    try {
      const response = await requestJson<{ result: OperationResult }>("/api/pos/inventory/operations", { method: "POST", body: JSON.stringify(body) });
      const result = response.data.result;
      pendingRequestId.current = null;
      setState("success");
      setMessage(result.receipt ? `Recepción ${result.receipt.folio} por ${formatMoney(result.receipt.totalCents)} registrada.` : `${result.affectedProducts[0]?.name ?? "Inventario"}: ${result.affectedProducts[0]?.beforeQty ?? 0} → ${result.affectedProducts[0]?.afterQty ?? 0}.`);
      setQuantity("");
      setReason("");
      await loadSnapshot();
      onCompleted();
    } catch (error) {
      setState("error");
      setMessage(`${errorMessage(error)} Puedes reintentar: se conservará el mismo identificador.`);
    }
  }

  function changeMode(next: "adjust" | "count" | "receive") {
    setMode(next);
    setQuantity("");
    setReason("");
    setMessage("");
    setState("idle");
    pendingRequestId.current = null;
  }

  return <section className={styles.operationsSurface} aria-label="Operaciones de inventario">
    <header className={styles.operationsHeader}><div><span className={styles.detailKicker}>Control de existencias</span><strong>Recibir, contar o ajustar</strong><small>Cada operación conserva responsable, before/after, auditoría e idempotencia.</small></div><button type="button" className={styles.secondaryAction} onClick={() => setOpen((value) => !value)}>{open ? "Cerrar operaciones" : "Abrir operaciones"}</button></header>
    {open ? <div className={styles.operationsGrid}>
      <div className={styles.operationsTabs} role="tablist" aria-label="Tipo de operación">
        {(["adjust", "count", "receive"] as const).map((item) => <button key={item} type="button" role="tab" aria-selected={mode === item} className={mode === item ? styles.primaryAction : styles.ghostAction} onClick={() => changeMode(item)}>{item === "adjust" ? "Ajustar" : item === "count" ? "Contar" : "Recibir"}</button>)}
      </div>
      <div className={styles.operationForm}>
        {mode !== "receive" ? <label className={styles.operationField}><span>Producto</span><select value={selectedProduct?.id ?? ""} onChange={(event) => { setProductId(event.target.value); pendingRequestId.current = null; }}>{products.map((product) => <option value={product.id} key={product.id}>{product.sku} · {product.name} · {product.stockOnHand} disp.</option>)}</select></label> : <>
          <label className={styles.operationField}><span>Orden de compra</span><select value={selectedOrder?.id ?? ""} onChange={(event) => { setPurchaseOrderId(event.target.value); setPurchaseOrderLineId(""); pendingRequestId.current = null; }}>{snapshot.purchaseOrders.map((order) => <option value={order.id} key={order.id}>{order.folio} · {order.supplierName}</option>)}</select></label>
          <label className={styles.operationField}><span>Línea pendiente</span><select value={selectedLine?.id ?? ""} onChange={(event) => { setPurchaseOrderLineId(event.target.value); pendingRequestId.current = null; }}>{selectedOrder?.lines.map((line) => <option value={line.id} key={line.id}>{line.sku} · {line.name} · faltan {line.qtyRemaining}</option>)}</select></label>
        </>}
        <label className={styles.operationField}><span>{mode === "adjust" ? "Existencia final" : mode === "count" ? "Cantidad contada" : "Cantidad recibida"}</span><input inputMode="numeric" value={quantity} onChange={(event) => { setQuantity(event.target.value.replace(/\D/g, "")); pendingRequestId.current = null; }} /></label>
        <label className={styles.operationField}><span>{mode === "receive" ? "Referencia opcional" : mode === "count" ? "Nota de conteo" : "Motivo"}</span><input value={reason} maxLength={180} onChange={(event) => { setReason(event.target.value); pendingRequestId.current = null; }} /></label>
        <button type="button" className={styles.primaryAction} onClick={() => void submit()} disabled={!canSubmit || state === "loading"}>{state === "loading" ? "Registrando..." : mode === "adjust" ? "Confirmar ajuste" : mode === "count" ? "Cerrar conteo" : "Registrar recepción"}</button>
      </div>
      {message ? <div className={styles.operationStatus} data-state={state} role={state === "error" ? "alert" : "status"}>{message}</div> : null}
    </div> : null}
  </section>;
}
