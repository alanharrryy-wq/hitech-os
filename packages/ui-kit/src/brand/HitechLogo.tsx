import type { HTMLAttributes } from "react";
import { cn } from "../lib/cn.js";
import { brandPresenceConfig } from "./brand-presence.config.js";

export interface HitechLogoProps extends HTMLAttributes<HTMLSpanElement> {
  readonly showWordmark?: boolean;
  readonly imageClassName?: string;
  readonly wordmark?: string;
}

export function HitechLogo({
  className,
  showWordmark = true,
  imageClassName,
  wordmark = "HITECH",
  ...props
}: HitechLogoProps) {
  return (
    <span className={cn("ui-hitech-logo", className)} {...props}>
      <img
        src={brandPresenceConfig.phoenixAssetPath}
        alt="HITECH phoenix"
        width={42}
        height={42}
        decoding="async"
        loading="eager"
        className={cn("ui-hitech-logo__mark", imageClassName)}
      />
      {showWordmark ? <span className="ui-hitech-logo__word">{wordmark}</span> : null}
    </span>
  );
}
