import type { ParameterDefinition, WorkflowConfig, WorkflowDefinition } from '../types';

type Props = {
  definition: WorkflowDefinition;
  config: WorkflowConfig;
  disabled: boolean;
  onChange: (next: WorkflowConfig) => void;
};

const numericKeys = new Set<keyof WorkflowConfig>([
  'seed',
  'texture_size',
  'sampler_steps',
  'num_samples',
  'max_num_tokens',
  'decimation_target'
]);

export function ParameterPanel({ definition, config, disabled, onChange }: Props) {
  const paramsByStep = new Map<string, ParameterDefinition[]>();
  for (const parameter of definition.parameters) {
    const group = paramsByStep.get(parameter.step_id) ?? [];
    group.push(parameter);
    paramsByStep.set(parameter.step_id, group);
  }

  function updateValue(key: keyof WorkflowConfig, value: unknown) {
    onChange({ ...config, [key]: value });
  }

  return (
    <section className="panel parameter-panel" aria-label="Workflow parameters">
      <div className="panel-heading">
        <h2>Parameters</h2>
        <span>{definition.parameters.length} controls</span>
      </div>
      <div className="parameter-groups">
        {definition.steps.map((step) => {
          const parameters = paramsByStep.get(step.id) ?? [];
          if (parameters.length === 0) {
            return null;
          }
          return (
            <fieldset key={step.id} className="parameter-group" disabled={disabled}>
              <legend>{step.title}</legend>
              <div className="parameter-grid">
                {parameters.map((parameter) => (
                  <label key={parameter.key} className="field">
                    <span>{parameter.label}</span>
                    <ParameterInput parameter={parameter} config={config} onChange={updateValue} />
                  </label>
                ))}
              </div>
            </fieldset>
          );
        })}
      </div>
    </section>
  );
}

type InputProps = {
  parameter: ParameterDefinition;
  config: WorkflowConfig;
  onChange: (key: keyof WorkflowConfig, value: unknown) => void;
};

function ParameterInput({ parameter, config, onChange }: InputProps) {
  const key = parameter.key;
  const value = config[key];

  if (parameter.control === 'checkbox') {
    return (
      <input
        type="checkbox"
        checked={Boolean(value)}
        onChange={(event) => onChange(key, event.currentTarget.checked)}
      />
    );
  }

  if (parameter.control === 'select') {
    return (
      <select
        value={String(value ?? '')}
        onChange={(event) => {
          const next = numericKeys.has(key) ? Number(event.currentTarget.value) : event.currentTarget.value;
          onChange(key, next);
        }}
      >
        {parameter.options?.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    );
  }

  if (parameter.control === 'number') {
    return (
      <input
        type="number"
        value={value == null ? '' : String(value)}
        min={parameter.minimum ?? undefined}
        max={parameter.maximum ?? undefined}
        onChange={(event) => {
          const raw = event.currentTarget.value;
          onChange(key, raw === '' ? null : Number(raw));
        }}
      />
    );
  }

  return (
    <input
      type="text"
      value={value == null ? '' : String(value)}
      placeholder={parameter.default == null ? '' : String(parameter.default)}
      onChange={(event) => onChange(key, key === 'output_name' ? event.currentTarget.value || null : event.currentTarget.value)}
    />
  );
}
