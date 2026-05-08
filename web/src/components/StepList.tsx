import { Check, Circle, Loader2, Play, SkipForward, XCircle } from 'lucide-react';

import type { StepDefinition, StepState } from '../types';
import { formatDuration, statusLabel, statusTone } from '../lib/workflow';

type Props = {
  definitions: StepDefinition[];
  steps: StepState[];
  selectedStepId: string | null;
  busy: boolean;
  onSelect: (stepId: string) => void;
  onRunStep: (stepId: string) => void;
};

export function StepList({ definitions, steps, selectedStepId, busy, onSelect, onRunStep }: Props) {
  const stepById = new Map(steps.map((step) => [step.id, step]));

  return (
    <section className="panel step-panel" aria-label="Pipeline steps">
      <div className="panel-heading">
        <h2>Pipeline</h2>
        <span>{steps.length} steps</span>
      </div>
      <div className="step-list">
        {definitions.map((definition, index) => {
          const state = stepById.get(definition.id);
          if (!state) {
            return null;
          }
          const selected = selectedStepId === definition.id;
          return (
            <div key={definition.id} className={`step-row ${selected ? 'selected' : ''}`}>
              <button type="button" className="step-select" onClick={() => onSelect(definition.id)}>
                <span className={`status-dot ${statusTone(state.status)}`} aria-hidden="true">
                  <StatusIcon status={state.status} />
                </span>
                <span className="step-copy">
                  <span className="step-title">{index + 1}. {definition.title}</span>
                  <span className="step-meta">
                    {statusLabel(state.status)} {formatDuration(state.duration_seconds)}
                  </span>
                </span>
              </button>
              <button
                type="button"
                className="icon-button"
                title={`Run ${definition.title}`}
                disabled={busy || state.status === 'running'}
                onClick={() => onRunStep(definition.id)}
              >
                <Play size={16} />
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function StatusIcon({ status }: { status: StepState['status'] }) {
  if (status === 'running') {
    return <Loader2 size={15} className="spin" />;
  }
  if (status === 'completed') {
    return <Check size={15} />;
  }
  if (status === 'skipped') {
    return <SkipForward size={15} />;
  }
  if (status === 'failed') {
    return <XCircle size={15} />;
  }
  return <Circle size={15} />;
}
