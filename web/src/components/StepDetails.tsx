import type { StepDefinition, StepState } from '../types';
import { formatDuration, statusLabel, statusTone } from '../lib/workflow';

type Props = {
  definition?: StepDefinition;
  state?: StepState;
};

export function StepDetails({ definition, state }: Props) {
  if (!definition || !state) {
    return (
      <section className="panel detail-panel">
        <div className="empty-state">Select a pipeline step.</div>
      </section>
    );
  }

  return (
    <section className="panel detail-panel" aria-label="Step details">
      <div className="panel-heading">
        <h2>{definition.title}</h2>
        <span className={`status-pill ${statusTone(state.status)}`}>{statusLabel(state.status)}</span>
      </div>
      <p className="step-description">{definition.description}</p>
      <dl className="detail-grid">
        <div>
          <dt>Started</dt>
          <dd>{state.started_at ? new Date(state.started_at).toLocaleTimeString() : 'Not started'}</dd>
        </div>
        <div>
          <dt>Duration</dt>
          <dd>{formatDuration(state.duration_seconds) || 'Pending'}</dd>
        </div>
      </dl>
      {state.summary && <p className="step-summary">{state.summary}</p>}
      {state.error && <pre className="error-block">{state.error}</pre>}
      {Object.keys(state.metrics).length > 0 && (
        <div className="metrics">
          {Object.entries(state.metrics).map(([key, value]) => (
            <div key={key} className="metric">
              <span>{key.replace(/_/g, ' ')}</span>
              <strong>{formatMetric(value)}</strong>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function formatMetric(value: unknown): string {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(2);
  }
  if (value == null) {
    return 'None';
  }
  return String(value);
}
