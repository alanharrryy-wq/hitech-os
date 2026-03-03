"use client";

import { useEffect, useRef, type PropsWithChildren } from "react";
import { Badge, cn } from "@hitech/ui-kit";
import { usePitchSectionContext } from "../shell/pitch-shell-context";

export interface PitchSectionProps extends PropsWithChildren {
  readonly id: string;
  readonly title: string;
  readonly description?: string | undefined;
  readonly eyebrow?: string | undefined;
  readonly className?: string | undefined;
  readonly headingClassName?: string | undefined;
  readonly contentClassName?: string | undefined;
  readonly stickyHeading?: boolean | undefined;
  readonly actions?: React.ReactNode | undefined;
}

export function PitchSection({
  id,
  title,
  description,
  eyebrow,
  className,
  headingClassName,
  contentClassName,
  stickyHeading = true,
  actions,
  children
}: PitchSectionProps) {
  const { setActiveSectionId } = usePitchSectionContext();
  const ref = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveSectionId(id);
          }
        }
      },
      {
        rootMargin: "-30% 0px -60% 0px",
        threshold: [0.1, 0.3, 0.5]
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [id, setActiveSectionId]);

  return (
    <section id={id} ref={ref} className={cn("scroll-mt-24", className)} aria-labelledby={`${id}-heading`}>
      <header
        className={cn(
          "pitch-glass-card pitch-neon-edge mb-3 grid gap-2 p-4",
          stickyHeading ? "lg:sticky lg:top-2 lg:z-20" : undefined,
          headingClassName
        )}
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2">
            {eyebrow ? <Badge>{eyebrow}</Badge> : null}
            <span className="rounded-full border border-[rgba(2,111,134,0.24)] px-2 py-1 text-[0.65rem] font-semibold uppercase tracking-[0.1em] text-[color:#026F86]">
              Anchor
            </span>
          </div>
          {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
        </div>
        <h2 id={`${id}-heading`} className="m-0 text-xl font-semibold tracking-[-0.02em] text-[color:var(--pitch-ink)]">
          {title}
        </h2>
        {description ? (
          <p className="m-0 text-sm leading-6 text-[color:rgba(4,18,25,0.72)]">{description}</p>
        ) : null}
      </header>

      <div className={cn("grid gap-3", contentClassName)}>{children}</div>
    </section>
  );
}
