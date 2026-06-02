import React, { useEffect, useMemo, useState } from 'react';
import { PrismoDependentSelect } from './PrismoDependentSelect';
import composerModel from '../../contracts/composer/dependent_crystal_composer.json';

type ComposerSubmit = {
  objective: string;
  domain: string;
  lens: string;
  freeText: string;
  contextNote: string;
  autoRender: true;
};

function optionId(option: any): string {
  return typeof option === 'string' ? option : option.id;
}

function optionLabel(option: any): string {
  return typeof option === 'string' ? option : option.label ?? option.id;
}

export function PrismoQueryComposer({ onSubmit }: { onSubmit?: (payload: ComposerSubmit) => void }) {
  const objectiveOptions = composerModel.dropdowns[0].options;
  const [objective, setObjective] = useState(optionId(objectiveOptions[0]));
  const [domain, setDomain] = useState('learning');
  const [lens, setLens] = useState('procedural_memory');
  const [freeText, setFreeText] = useState('');
  const [contextNote, setContextNote] = useState('');

  const domainOptions = useMemo(() => composerModel.dropdowns[1].options_by_objective[objective] ?? ['learning'], [objective]);
  const lensOptions = useMemo(() => composerModel.dropdowns[2].options_by_pair[`${objective}:${domain}`] ?? ['procedural_memory'], [objective, domain]);

  useEffect(() => {
    if (!domainOptions.includes(domain)) setDomain(domainOptions[0] ?? 'learning');
  }, [domainOptions, domain]);

  useEffect(() => {
    if (!lensOptions.includes(lens)) setLens(lensOptions[0] ?? 'procedural_memory');
  }, [lensOptions, lens]);

  function submit() {
    onSubmit?.({ objective, domain, lens, freeText, contextNote, autoRender: true });
  }

  const smartChips = [
    'Qué falta para dejarlo listo',
    'Qué evidencia soporta esto',
    'Qué protocolo conviene',
    'Qué riesgo hay',
    'Prepara plan con rollback',
    'Ver detalle técnico'
  ];

  return (
    <form className="prismo-ui1p-composer prismo-preset-crystal-dropdown-refrigerant" onSubmit={(e) => { e.preventDefault(); submit(); }}>
      <div className="prismo-ui1p-brand-kicker">PRISMO Theater · Auto Render Ensemble</div>
      <h2>Pregunta con intención. PRISMO decide la mejor escena.</h2>
      <p className="prismo-ui1p-composer-note">Tres dropdowns guían el motor; el formato visual se elige automáticamente según evidencia, memoria y protocolo.</p>

      <PrismoDependentSelect
        label="Objetivo"
        value={objective}
        options={objectiveOptions.map((o: any) => ({ value: optionId(o), label: optionLabel(o) }))}
        onChange={setObjective}
      />
      <PrismoDependentSelect label="Superficie / Área" value={domain} options={domainOptions} onChange={setDomain} />
      <PrismoDependentSelect label="Lente / Evidencia" value={lens} options={lensOptions} onChange={setLens} />

      <label className="prismo-ui1p-field">
        <span>Texto libre</span>
        <textarea value={freeText} onChange={(e) => setFreeText(e.target.value)} placeholder="Dile a PRISMO qué quieres entender, diagnosticar, decidir o preparar..." />
      </label>
      <label className="prismo-ui1p-field compact">
        <span>Contexto opcional</span>
        <input value={contextNote} onChange={(e) => setContextNote(e.target.value)} placeholder="ruta, síntoma, pantalla, zip, módulo, evidencia, error..." />
      </label>
      <div className="prismo-ui1p-chip-row">
        {smartChips.map((chip) => <button key={chip} type="button" onClick={() => setFreeText(chip)}>{chip}</button>)}
      </div>
      <button className="prismo-ui1p-primary" type="submit">Renderizar respuesta con PRISMO</button>
    </form>
  );
}
