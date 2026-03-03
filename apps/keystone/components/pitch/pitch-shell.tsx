import type { PropsWithChildren, ReactNode } from "react";
import { cn } from "@hitech/ui-kit";
import { buildPitchShellFrameModel } from "./view-model/pitch-shell-model";
import { PitchShell as CorePitchShell, type PitchShellProps as CorePitchShellProps } from "./shell";
import type { PitchNavModel } from "./types";

export interface PitchShellProps extends PropsWithChildren {
  readonly title?: string;
  readonly subtitle?: string;
  readonly nav?: PitchNavModel;
  readonly actions?: ReactNode;
  readonly className?: string;
  readonly model?: CorePitchShellProps["model"];
  readonly showScrollAffordance?: boolean;
  readonly enableKeyboardNav?: boolean;
}

export function PitchShell({
  title,
  subtitle,
  nav,
  actions,
  children,
  className,
  model,
  showScrollAffordance = true,
  enableKeyboardNav = false
}: PitchShellProps) {
  const resolvedModel =
    model ??
    (() => {
      const shellModel = buildPitchShellFrameModel(nav?.activeSlug);
      return {
        ...shellModel,
        hero: {
          ...shellModel.hero,
          title: title ?? shellModel.hero.title,
          subtitle: subtitle ?? shellModel.hero.subtitle
        },
        nav: {
          links: nav?.links ?? shellModel.nav.links,
          ...(nav?.activeSlug ? { activeSlug: nav.activeSlug } : {})
        }
      };
    })();

  return (
    <CorePitchShell
      model={resolvedModel}
      className={cn(className)}
      showScrollAffordance={showScrollAffordance}
      enableKeyboardNav={enableKeyboardNav}
    >
      {actions ? <div className="pitch-glass-card pitch-neon-edge rounded-[var(--pitch-radius-lg)] p-3">{actions}</div> : null}
      {children}
    </CorePitchShell>
  );
}
