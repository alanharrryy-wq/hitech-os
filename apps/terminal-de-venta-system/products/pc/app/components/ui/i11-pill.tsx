import type { ReactNode } from 'react';

type Tone = 'sky' | 'amber' | 'rose' | 'violet' | 'slate';

const classes: Record<Tone, string> = {
  sky: 'border-sky-400/20 bg-sky-400/10 text-sky-100',
  amber: 'border-amber-400/20 bg-amber-400/10 text-amber-100',
  rose: 'border-rose-400/20 bg-rose-400/10 text-rose-100',
  violet: 'border-violet-400/20 bg-violet-400/10 text-violet-100',
  slate: 'border-white/10 bg-white/5 text-white/75',
};

export function I11Pill({ children, tone = 'slate' }: { children: ReactNode; tone?: Tone }) {
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs ${classes[tone]}`}>{children}</span>;
}
