"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "./prisma-skin-selector.module.css";

type PrismaPosSkin = "light" | "dark" | "system";
type ResolvedPrismaPosSkin = "light" | "dark";

const STORAGE_KEY = "prisma.pos.skin";
const FALLBACK_SKIN = "light" as const;
const ALLOWED_SKINS = new Set<PrismaPosSkin>(["light", "dark", "system"]);

function readStoredSkin(): PrismaPosSkin {
  if (typeof window === "undefined") return FALLBACK_SKIN;
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return ALLOWED_SKINS.has(stored as PrismaPosSkin) ? (stored as PrismaPosSkin) : FALLBACK_SKIN;
}

function systemSkin(): ResolvedPrismaPosSkin {
  if (typeof window === "undefined") return FALLBACK_SKIN;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function resolveSkin(skin: PrismaPosSkin): ResolvedPrismaPosSkin {
  if (skin === "system") return systemSkin();
  return skin;
}

function applySkin(resolved: ResolvedPrismaPosSkin) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.dataset.prismaSkin = resolved;
  root.dataset.prismaSurface = "tablet-pos";
  root.dataset.theme = resolved === "dark" ? "prisma-dark" : "prisma-light";
}

export function PrismaSkinSelector() {
  const [selected, setSelected] = useState<PrismaPosSkin>(FALLBACK_SKIN);
  const [resolved, setResolved] = useState<ResolvedPrismaPosSkin>(FALLBACK_SKIN);

  useEffect(() => {
    const stored = readStoredSkin();
    const nextResolved = resolveSkin(stored);
    setSelected(stored);
    setResolved(nextResolved);
    applySkin(nextResolved);
  }, []);

  useEffect(() => {
    if (selected !== "system") return;
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = () => {
      const nextResolved = resolveSkin("system");
      setResolved(nextResolved);
      applySkin(nextResolved);
    };
    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, [selected]);

  const resolvedLabel = useMemo(() => (resolved === "dark" ? "Oscuro" : "Claro"), [resolved]);

  function handleChange(value: PrismaPosSkin) {
    const nextSelected = ALLOWED_SKINS.has(value) ? value : FALLBACK_SKIN;
    const nextResolved = resolveSkin(nextSelected);
    window.localStorage.setItem(STORAGE_KEY, nextSelected);
    setSelected(nextSelected);
    setResolved(nextResolved);
    applySkin(nextResolved);
  }

  return (
    <label className={styles.selector} data-prisma-component="SkinSelector" title={`Skin activa: ${resolvedLabel}`}>
      <span>Apariencia</span>
      <select value={selected} onChange={(event) => handleChange(event.target.value as PrismaPosSkin)} aria-label="Apariencia">
        <option value="light">Claro</option>
        <option value="dark">Oscuro</option>
        <option value="system">Sistema</option>
      </select>
    </label>
  );
}

export function PrismaDarkSelector() {
  return <PrismaSkinSelector />;
}
