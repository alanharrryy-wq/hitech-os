'use client';

import type { ButtonHTMLAttributes, HTMLAttributes, ReactNode } from 'react';
import styles from './prisma-glass-capsule.module.css';

type CapsuleVariant = 'neutral' | 'tinted' | 'active' | 'thinking' | 'danger' | 'disabled';
type CapsuleShape = 'circle' | 'pill' | 'rounded';
type CapsuleTone = 'graphite' | 'rose' | 'violet' | 'blue' | 'adaptive';
type CapsuleDensity = 'compact' | 'regular' | 'spacious';
type CapsuleElement = 'button' | 'div';

export type PrismaGlassCapsuleProps = {
  as?: CapsuleElement;
  variant?: CapsuleVariant;
  shape?: CapsuleShape;
  tone?: CapsuleTone;
  density?: CapsuleDensity;
  floating?: boolean;
  children?: ReactNode;
  className?: string;
} & ButtonHTMLAttributes<HTMLButtonElement> & HTMLAttributes<HTMLDivElement>;

function cx(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(' ');
}

function emitPrismaGlassAction(label: string) {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent('prisma:glass-action', {
    detail: { label, source: 'PrismaGlassTopDock', ts: new Date().toISOString() }
  }));
}

export function PrismaGlassCapsule({
  as = 'button',
  variant = 'neutral',
  shape = 'pill',
  tone = 'graphite',
  density = 'regular',
  floating = true,
  children,
  className,
  type,
  ...props
}: PrismaGlassCapsuleProps) {
  const common = {
    className: cx(styles.root, className),
    'data-variant': variant,
    'data-shape': shape,
    'data-tone': tone,
    'data-density': density,
    'data-floating': floating ? 'true' : 'false',
  } as const;

  const content = (
    <>
      <span aria-hidden="true" className={styles.refraction} />
      <span aria-hidden="true" className={styles.underGlow} />
      <span aria-hidden="true" className={styles.lobeLens} />
      <span aria-hidden="true" className={styles.edgeFrame} />
      <span aria-hidden="true" className={styles.volumeFrame} />
      <span aria-hidden="true" className={styles.innerFrame} />
      <span aria-hidden="true" className={styles.specular} />
      <span aria-hidden="true" className={styles.liquidSheen} />
      <span className={styles.content}>{children}</span>
    </>
  );

  if (as === 'div') {
    return (
      <div {...common} {...(props as HTMLAttributes<HTMLDivElement>)}>
        {content}
      </div>
    );
  }

  return (
    <button {...common} type={type ?? 'button'} {...(props as ButtonHTMLAttributes<HTMLButtonElement>)}>
      {content}
    </button>
  );
}

export type PrismaGlassTopDockAction = {
  label: string;
  icon?: ReactNode;
  onClick?: () => void;
};

export type PrismaGlassTopDockProps = {
  status?: string;
  statusTone?: CapsuleTone;
  thinking?: boolean;
  className?: string;
  leftLabel?: string;
  actions?: PrismaGlassTopDockAction[];
};

function MenuGlyph() {
  return <span aria-hidden="true" className={styles.menuGlyph}><i /><i /></span>;
}

function EditGlyph() {
  return <span aria-hidden="true" className={styles.editGlyph} />;
}

function DotsGlyph() {
  return <span aria-hidden="true" className={styles.dotsGlyph}><i /><i /><i /></span>;
}

export function PrismaGlassTopDock({
  status = 'Thinking',
  statusTone = 'blue',
  thinking = true,
  className,
  leftLabel = 'Abrir navegación',
  actions,
}: PrismaGlassTopDockProps) {
  const finalActions: PrismaGlassTopDockAction[] = actions?.length
    ? actions
    : [
        { label: 'Editar', icon: <EditGlyph />, onClick: () => emitPrismaGlassAction('Editar') },
        { label: 'Más opciones', icon: <DotsGlyph />, onClick: () => emitPrismaGlassAction('Más opciones') },
      ];

  return (
    <div className={cx(styles.topDock, className)} aria-label="Controles flotantes Liquid Glass" data-prisma-hardening="glass-actions-260611">
      <PrismaGlassCapsule aria-label={leftLabel} shape="circle" tone="graphite" density="regular" onClick={() => emitPrismaGlassAction(leftLabel)}>
        <MenuGlyph />
      </PrismaGlassCapsule>

      <PrismaGlassCapsule
        as="div"
        role="status"
        aria-live="polite"
        variant={thinking ? 'thinking' : 'active'}
        shape="pill"
        tone={statusTone}
        density="spacious"
        className={styles.statusPill}
      >
        <span className={styles.statusText}>{status}</span>
      </PrismaGlassCapsule>

      <PrismaGlassCapsule
        as="div"
        shape="pill"
        tone="rose"
        density="regular"
        className={styles.actionGroup}
      >
        {finalActions.map((action, index) => (
          <button
            key={`${action.label}-${index}`}
            type="button"
            className={styles.actionButton}
            aria-label={action.label}
            onClick={action.onClick ?? (() => emitPrismaGlassAction(action.label))}
          >
            {action.icon ?? <DotsGlyph />}
          </button>
        ))}
      </PrismaGlassCapsule>
    </div>
  );
}
