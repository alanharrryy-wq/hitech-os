import { useEffect, useState } from "react";
import { catalogRequest } from "@/lib/catalog/product-form-state";
import styles from "./catalog.module.css";

type Props = {
  value: string;
  productId?: string;
  onChange: (value: string) => void;
};

export function CatalogBarcodeField({ value, productId, onChange }: Props) {
  const [state, setState] = useState<"idle" | "checking" | "available" | "duplicate" | "error">("idle");

  useEffect(() => {
    const code = value.trim();
    if (code.length < 3) {
      setState("idle");
      return;
    }
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setState("checking");
      try {
        const params = new URLSearchParams({ code });
        if (productId) params.set("productId", productId);
        const response = await catalogRequest<{ available: boolean }>(`/api/pos/products/barcodes/validate?${params.toString()}`, { signal: controller.signal });
        setState(response.data.available ? "available" : "duplicate");
      } catch (error) {
        if (!controller.signal.aborted) setState("error");
      }
    }, 350);
    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [value, productId]);

  return (
    <label className={styles.field}>
      <span>Código de barras</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} placeholder="7500000000000" inputMode="numeric" />
      <small>
        {state === "checking" ? "Validando código..." : null}
        {state === "available" ? "Código disponible." : null}
        {state === "duplicate" ? "Ese código ya está ligado a otro producto." : null}
        {state === "error" ? "No se pudo validar ahora; se revisará al guardar." : null}
        {state === "idle" ? "Opcional, pero recomendado para escaneo rápido." : null}
      </small>
    </label>
  );
}
