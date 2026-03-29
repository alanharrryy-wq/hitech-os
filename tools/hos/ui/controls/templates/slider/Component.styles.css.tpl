.{{component_name}}-root {
  display: grid;
  gap: var(--ui-core-space-2, 8px);
  color: var(--ui-text-1, rgba(16, 24, 40, 1));
}

.{{component_name}}-label {
  font-size: 0.95rem;
  font-weight: 600;
}

.{{component_name}}-hint {
  font-size: 0.8rem;
  color: var(--ui-text-2, rgba(71, 84, 103, 1));
}

.{{component_name}}-row {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: var(--ui-core-space-3, 12px);
}

.{{component_name}}-input {
  inline-size: 100%;
  accent-color: hsl(var(--ui-accent, 222 89% 55%));
}

.{{component_name}}-value {
  min-inline-size: 42px;
  text-align: right;
  font-feature-settings: "tnum";
  color: var(--ui-text-2, rgba(71, 84, 103, 1));
}

