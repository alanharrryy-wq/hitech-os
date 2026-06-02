import React, { useState } from 'react';
import '../styles/prismo-theater-cloudglass-pro.css';
import '../styles/prismo-interaction-fx-pro.css';
import '../styles/prismo-radix-liquid-select.css';
import { PrismoQueryComposer } from './PrismoQueryComposer';
import { PrismoAutoRenderEnsemble } from './PrismoAutoRenderEnsemble';
import { PrismoTechnicalDrawer } from './PrismoTechnicalDrawer';
import { PrismoEmptyState } from './PrismoEmptyState';
import { PrismoLoadingScene } from './PrismoLoadingScene';
import { PrismoErrorScene } from './PrismoErrorScene';

export type PrismoTheaterState = 'empty' | 'loading' | 'success' | 'partial' | 'error';

export function PrismoAdaptiveTheater({ initialPlan, onSubmit }: any) {
  const [state, setState] = useState<PrismoTheaterState>(initialPlan ? 'success' : 'empty');
  const [plan, setPlan] = useState(initialPlan ?? null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  async function handleSubmit(payload: any) {
    setState('loading');
    try {
      const next = onSubmit ? await onSubmit(payload) : (window as any).__PRISMO_UI1P_FIXTURE_PLAN__;
      setPlan(next);
      setState(next?.warnings?.length ? 'partial' : 'success');
    } catch (err) {
      setPlan({ error: String(err) });
      setState('error');
    }
  }

  return (
    <section className="prismo-ui1p-shell" data-prismo-theater="pro" data-auto-render="true">
      <div className="prismo-ui1p-bg" aria-hidden="true" />
      <aside className="prismo-ui1p-composer-panel">
        <PrismoQueryComposer onSubmit={handleSubmit} />
      </aside>
      <main className="prismo-ui1p-theater-stage">
        {state === 'empty' && <PrismoEmptyState />}
        {state === 'loading' && <PrismoLoadingScene />}
        {state === 'error' && <PrismoErrorScene error={plan?.error} onRetry={() => setState('empty')} />}
        {(state === 'success' || state === 'partial') && (
          <PrismoAutoRenderEnsemble renderPlan={plan} onOpenDetail={() => setDrawerOpen(true)} />
        )}
      </main>
      <PrismoTechnicalDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} plan={plan} />
    </section>
  );
}
