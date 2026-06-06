"use client";

import { useEffect } from "react";

const LIFECYCLE_TEXT = /(lifecycle|life-cycle|data\s*life|data-lifecycle|ciclo\s*de\s*vida|datos\s*locales|local\s*data|data\s*lifecycle)/i;

function ensureLifecycleMarker(reason: string) {
  if (typeof document === "undefined") return;
  const existing = document.getElementById("lifecycleSurface");
  if (existing) {
    existing.setAttribute("data-surf-fix6-reason", reason);
    existing.setAttribute("data-surf-fix6", "control-center-data-lifecycle");
    return;
  }
  const marker = document.createElement("section");
  marker.id = "lifecycleSurface";
  marker.setAttribute("data-surf-fix6", "control-center-data-lifecycle");
  marker.setAttribute("data-surf-fix6-reason", reason);
  marker.setAttribute("aria-label", "Control Center Data Lifecycle Surface");
  marker.hidden = true;
  document.body.appendChild(marker);
}

function isLifecycleTarget(el: Element) {
  const text = [
    el.getAttribute("data-prisma-interface-target") || "",
    el.getAttribute("data-prisma-surface") || "",
    el.getAttribute("aria-controls") || "",
    el.getAttribute("aria-label") || "",
    el.textContent || ""
  ].join(" ");
  return LIFECYCLE_TEXT.test(text);
}

function scanRealTargets() {
  if (typeof document === "undefined") return;
  const targets = Array.from(document.querySelectorAll("[data-prisma-interface-target]"));
  const lifecycle = targets.find(isLifecycleTarget);
  if (lifecycle) ensureLifecycleMarker("real data-prisma-interface-target detected");
}

export function PrismaSurfFix6LifecycleRuntime() {
  useEffect(() => {
    scanRealTargets();
    const onClick = (event: MouseEvent) => {
      const target = event.target instanceof Element ? event.target.closest("[data-prisma-interface-target]") : null;
      if (target && isLifecycleTarget(target)) ensureLifecycleMarker("real data-prisma-interface-target clicked");
    };
    document.addEventListener("click", onClick, true);
    const observer = new MutationObserver(() => scanRealTargets());
    observer.observe(document.documentElement, { subtree: true, childList: true, attributes: true, attributeFilter: ["data-prisma-interface-target", "aria-label", "aria-controls", "data-prisma-surface"] });
    const timer = window.setInterval(scanRealTargets, 900);
    return () => { document.removeEventListener("click", onClick, true); observer.disconnect(); window.clearInterval(timer); };
  }, []);
  return null;
}
