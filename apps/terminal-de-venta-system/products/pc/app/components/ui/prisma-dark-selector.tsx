"use client";

import { useEffect, useMemo, useState } from "react";

type SkinPreference = "light" | "dark" | "system";
type ResolvedSkin = "light" | "dark";

const STORAGE_KEY = "prisma.pc.skin";
const OPTIONS: Array<{ value: SkinPreference; label: string }> = [
  { value: "light", label: "Claro" },
  { value: "dark", label: "Oscuro" },
  { value: "system", label: "Sistema" }
];

function normalizePreference(value: string | null): SkinPreference {
  return value === "light" || value === "dark" || value === "system" ? value : "light";
}

function resolveSkin(preference: SkinPreference): ResolvedSkin {
  if (preference === "light" || preference === "dark") return preference;
  if (typeof window === "undefined") return "light";
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applySkin(preference: SkinPreference) {
  if (typeof document === "undefined") return;
  const resolved = resolveSkin(preference);
  const root = document.documentElement;
  root.dataset.prismaSkin = resolved;
  root.dataset.prismaSurface = "pc-backoffice";
  root.dataset.theme = resolved === "light" ? "prisma-light" : "prisma-dark";
  root.dataset.prismaSkinPreference = preference;
}

export function PrismaDarkSelector() {
  const [preference, setPreference] = useState<SkinPreference>("light");

  useEffect(() => {
    const stored = normalizePreference(window.localStorage.getItem(STORAGE_KEY));
    setPreference(stored);
    applySkin(stored);
  }, []);

  useEffect(() => {
    const query = window.matchMedia?.("(prefers-color-scheme: dark)");
    if (!query) return;
    const listener = () => applySkin(normalizePreference(window.localStorage.getItem(STORAGE_KEY)));
    query.addEventListener?.("change", listener);
    return () => query.removeEventListener?.("change", listener);
  }, []);

  const resolved = useMemo(() => resolveSkin(preference), [preference]);

  function choose(value: SkinPreference) {
    window.localStorage.setItem(STORAGE_KEY, value);
    setPreference(value);
    applySkin(value);
  }

  return (
    <div className="prisma-appearance-selector" role="group" aria-label="Selector de apariencia">
      <span className="prisma-appearance-label">Apariencia</span>
      <span className="prisma-appearance-options" aria-label="Opciones de apariencia">
        {OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            className="prisma-appearance-option"
            data-active={preference === option.value ? "true" : undefined}
            aria-pressed={preference === option.value}
            title={option.value === "system" ? `Sistema: ${resolved}` : option.label}
            onClick={() => choose(option.value)}
          >
            {option.label}
          </button>
        ))}
      </span>
    </div>
  );
}
