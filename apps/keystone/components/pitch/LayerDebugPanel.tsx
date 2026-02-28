'use client';

import { useMemo } from 'react';
import { useLayerFlags } from './LayerFlagsProvider';
import styles from './LayerDebugPanel.module.css';

function toRows(flags: Record<string, boolean>) {
  return Object.entries(flags)
    .map(([name, enabled]) => ({ name, enabled }))
    .sort((left, right) => left.name.localeCompare(right.name));
}

export interface LayerDebugPanelProps {
  readonly title?: string;
}

export function LayerDebugPanel({ title = 'Layer Debug Panel' }: LayerDebugPanelProps) {
  const state = useLayerFlags();
  const rows = useMemo(() => toRows(state.flags), [state.flags]);

  return (
    <aside className={styles.root} aria-label={title}>
      <header className={styles.header}>
        <h3 className={styles.title}>{title}</h3>
        <p className={styles.summary}>
          mode={state.mode} profile={state.profile} debug={state.debug ? '1' : '0'}
        </p>
      </header>
      <dl className={styles.metaGrid}>
        <div>
          <dt>layers</dt>
          <dd>{state.queryEcho.layers}</dd>
        </div>
        <div>
          <dt>layerProfile</dt>
          <dd>{state.queryEcho.layerProfile}</dd>
        </div>
        <div>
          <dt>debug</dt>
          <dd>{state.queryEcho.debug}</dd>
        </div>
        <div>
          <dt>layerList</dt>
          <dd>{state.queryEcho.layerList || '-'}</dd>
        </div>
      </dl>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">Layer</th>
              <th scope="col">Enabled</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.name}>
                <th scope="row">{row.name}</th>
                <td>
                  <span className={row.enabled ? styles.enabled : styles.disabled}>
                    {row.enabled ? 'on' : 'off'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </aside>
  );
}

export default LayerDebugPanel;
