"use client";

import { useEffect } from "react";

const ISSUE_BADGE_PATTERN = /\b\d+\s+issues?\b|\bissues?\b/i;
const NEXT_DEV_MARK_PATTERN = /^(n|next\.js)$/i;

function isHTMLElement(node: Element): node is HTMLElement {
  return node instanceof HTMLElement;
}

function getVisibleRect(element: HTMLElement) {
  const rect = element.getBoundingClientRect();
  if (!rect || rect.width <= 0 || rect.height <= 0) return null;
  return rect;
}

function isBottomLeftDevIssueCandidate(element: HTMLElement) {
  const text = (element.textContent || "").replace(/\s+/g, " ").trim();
  if (!ISSUE_BADGE_PATTERN.test(text) && !NEXT_DEV_MARK_PATTERN.test(text)) return false;

  const rect = getVisibleRect(element);
  if (!rect) return false;

  const computed = window.getComputedStyle(element);
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;

  const nearLeft = rect.left <= 140;
  const nearBottom = viewportHeight - rect.bottom <= 150;
  const compact = rect.width <= 430 && rect.height <= 180;
  const overlayLike = computed.position === "fixed" || computed.position === "sticky" || computed.zIndex !== "auto";

  return nearLeft && nearBottom && compact && overlayLike;
}

function findHideTarget(element: HTMLElement) {
  let target: HTMLElement = element;
  let current: HTMLElement | null = element.parentElement;

  while (current) {
    const rect = getVisibleRect(current);
    const text = (current.textContent || "").replace(/\s+/g, " ").trim();
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;

    if (
      rect &&
      (ISSUE_BADGE_PATTERN.test(text) || NEXT_DEV_MARK_PATTERN.test(text)) &&
      rect.left <= 140 &&
      viewportHeight - rect.bottom <= 150 &&
      rect.width <= 430 &&
      rect.height <= 180
    ) {
      target = current;
      current = current.parentElement;
      continue;
    }

    break;
  }

  return target;
}

function scanRoot(root: ParentNode) {
  const elements = Array.from(root.querySelectorAll("*"));

  for (const element of elements) {
    const anyElement = element as Element & { shadowRoot?: ShadowRoot };
    if (anyElement.shadowRoot) {
      scanRoot(anyElement.shadowRoot);
    }

    if (!isHTMLElement(element)) continue;
    if (!isBottomLeftDevIssueCandidate(element)) continue;

    const target = findHideTarget(element);
    target.dataset.prismaHiddenDevIssueBadge = "true";
    target.setAttribute("aria-hidden", "true");
    target.style.setProperty("display", "none", "important");
    target.style.setProperty("visibility", "hidden", "important");
    target.style.setProperty("pointer-events", "none", "important");
  }
}

export function PrismaDevIssueBadgeCleaner() {
  useEffect(() => {
    let raf = 0;

    const clean = () => {
      cancelAnimationFrame(raf);
      raf = window.requestAnimationFrame(() => {
        scanRoot(document);
      });
    };

    clean();

    const observer = new MutationObserver(clean);
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["style", "class", "data-nextjs-dialog-overlay", "data-nextjs-toast"],
    });

    const interval = window.setInterval(clean, 700);

    return () => {
      cancelAnimationFrame(raf);
      window.clearInterval(interval);
      observer.disconnect();
    };
  }, []);

  return null;
}
