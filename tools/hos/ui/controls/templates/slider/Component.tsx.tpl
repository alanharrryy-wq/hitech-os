import "./{{COMPONENT_NAME}}.styles.css";
import { useId } from "react";

export interface {{COMPONENT_NAME}}Props {
  readonly label: string;
  readonly min: number;
  readonly max: number;
  readonly value: number;
  readonly step?: number;
  readonly onChange: (next: number) => void;
  readonly hint?: string;
}

export function {{COMPONENT_NAME}}(props: {{COMPONENT_NAME}}Props): JSX.Element {
  const { label, min, max, value, step = 1, onChange, hint } = props;
  const id = useId();
  return (
    <label className="{{component_name}}-root" htmlFor={id} data-control-kind="{{CONTROL_KIND}}">
      <span className="{{component_name}}-label">{label}</span>
      {hint ? <span className="{{component_name}}-hint">{hint}</span> : null}
      <div className="{{component_name}}-row">
        <input
          id={id}
          className="{{component_name}}-input"
          type="range"
          min={min}
          max={max}
          value={value}
          step={step}
          onChange={(event) => onChange(Number(event.currentTarget.value))}
        />
        <output className="{{component_name}}-value">{value}</output>
      </div>
    </label>
  );
}

