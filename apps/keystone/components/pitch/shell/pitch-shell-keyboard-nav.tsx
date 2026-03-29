"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import type { PitchNavigationLink } from "@hitech/contracts";

export interface PitchShellKeyboardNavProps {
  readonly links: readonly PitchNavigationLink[];
  readonly disabled?: boolean;
}

function nextRoute(
  links: readonly PitchNavigationLink[],
  pathname: string,
  direction: "left" | "right"
): string | null {
  const index = links.findIndex((link) => pathname.startsWith(link.href));
  if (index < 0) {
    return null;
  }

  if (direction === "left") {
    if (index === 0) {
      return null;
    }
    return links[index - 1]?.href ?? null;
  }

  if (index >= links.length - 1) {
    return null;
  }

  return links[index + 1]?.href ?? null;
}

export function PitchShellKeyboardNav({ links, disabled = false }: PitchShellKeyboardNavProps) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (disabled || !pathname) {
      return;
    }

    const handler = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) {
        return;
      }

      if (event.key === "ArrowLeft") {
        const previous = nextRoute(links, pathname, "left");
        if (previous) {
          event.preventDefault();
          router.push(previous);
        }
      }

      if (event.key === "ArrowRight") {
        const next = nextRoute(links, pathname, "right");
        if (next) {
          event.preventDefault();
          router.push(next);
        }
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [disabled, links, pathname, router]);

  return null;
}
