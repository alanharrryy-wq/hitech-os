"use client";

import { useMemo, useState } from "react";

import { resolveIconFamilyByTheme } from "@/lib/ui/shell-system/client/client.theme";
import type { IconFamily } from "@/lib/ui/shell-system/types";
import type { UiThemeId } from "@/lib/ui/theme-system";
import { cn } from "@/lib/utils";

const FALLBACK_ICON_PATH = "/icons/round-ui/set_01_nebula_midnight/sparkle.svg";

function buildIconPath(family: IconFamily, name: string, themeId?: UiThemeId): string {
  const resolvedFamily = family === "system" ? resolveIconFamilyByTheme(themeId ?? "solstice") : family;
  return `/icons/round-ui/${resolvedFamily}/${name}.svg`;
}

export function RoundSvgIcon({
  name,
  family,
  themeId,
  size = 16,
  className,
  alt,
  decorative = true
}: {
  name: string;
  family?: IconFamily;
  themeId?: UiThemeId;
  size?: number;
  className?: string;
  alt?: string;
  decorative?: boolean;
}) {
  const [failed, setFailed] = useState(false);
  const resolvedFamily = family ?? (themeId ? resolveIconFamilyByTheme(themeId) : "set_02_pearl_mist");

  const src = useMemo(
    () => (failed ? FALLBACK_ICON_PATH : buildIconPath(resolvedFamily, name, themeId)),
    [failed, resolvedFamily, name, themeId]
  );

  return (
    <img
      src={src}
      width={size}
      height={size}
      className={cn("shrink-0 object-contain", className)}
      alt={decorative ? "" : alt ?? name}
      aria-hidden={decorative}
      draggable={false}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  );
}
