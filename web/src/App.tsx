import { Play, RotateCcw, Server, StepForward } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { workflowApi } from './api/client';
import { ArtifactPanel } from './components/ArtifactPanel';
import { LogPanel } from './components/LogPanel';
import { ParameterPanel } from './components/ParameterPanel';
import { StepDetails } from './components/StepDetails';
import { StepList } from './components/StepList';
import { defaultConfig, nextRunnableStep } from './lib/workflow';
import type { WorkflowConfig, WorkflowDefinition, WorkflowState } from './types';

export default function App() {
  const [definition, setDefinition] = useState<WorkflowDefinition | null>(null);
  const [config, setConfig] = useState<WorkflowConfig>(defaultConfig);
  const [session, setSession] = useState<WorkflowState | null>(null);
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    workflowApi
      .getDefinition()
      .then((nextDefinition) => {
        setDefinition(nextDefinition);
        setSelectedStepId(nextDefinition.steps[0]?.id ?? null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!session?.busy) {
      return undefined;
    }
    const timer = window.setInterval(() => {
      workflowApi
        .getSession(session.session_id)
        .then(setSession)
        .catch((err: Error) => setError(err.message));
    }, 1500);
    return () => window.clearInterval(timer);
  }, [session?.busy, session?.session_id]);

  useEffect(() => {
    if (session?.active_step_id) {
      setSelectedStepId(session.active_step_id);
    }
  }, [session?.active_step_id]);

  const selectedDefinition = useMemo(
    () => definition?.steps.find((step) => step.id === selectedStepId),
    [definition, selectedStepId]
  );
  const selectedState = useMemo(
    () => session?.steps.find((step) => step.id === selectedStepId),
    [session, selectedStepId]
  );
  const nextStep = session ? nextRunnableStep(session.steps) : undefined;

  async function createSession() {
    try {
      setError(null);
      const nextConfig = prepareConfig(config);
      setConfig(nextConfig);
      const nextSession = await workflowApi.createSession(nextConfig);
      setSession(nextSession);
      setSelectedStepId(nextSession.steps[0]?.id ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create a workflow session.');
    }
  }

  async function runStep(stepId: string) {
    if (!session) {
      return;
    }
    try {
      setError(null);
      setSession(await workflowApi.runStep(session.session_id, stepId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to run the selected step.');
    }
  }

  async function runNext() {
    if (!session) {
      return;
    }
    try {
      setError(null);
      setSession(await workflowApi.runNext(session.session_id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to run the next step.');
    }
  }

  async function runAll() {
    if (!session) {
      return;
    }
    try {
      setError(null);
      setSession(await workflowApi.runAll(session.session_id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to run the workflow.');
    }
  }

  function resetSession() {
    setSession(null);
    setError(null);
    setSelectedStepId(definition?.steps[0]?.id ?? null);
  }

  if (loading || !definition) {
    return <main className="boot-screen">Loading workflow console...</main>;
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>TRELLIS Workflow</h1>
          <p>Configure each stage, run it when ready, and inspect the pipeline logs as they arrive.</p>
        </div>
        <div className="session-chip">
          <Server size={16} />
          <span>{session ? `Session ${session.session_id}` : 'No session'}</span>
        </div>
      </header>

      <section className="command-bar" aria-label="Workflow commands">
        <button type="button" className="primary-button" onClick={() => void createSession()} disabled={session?.busy}>
          <Server size={16} />
          {session ? 'Create New Session' : 'Create Session'}
        </button>
        <button type="button" onClick={() => void runNext()} disabled={!session || session.busy || !nextStep}>
          <StepForward size={16} />
          Run Next
        </button>
        <button type="button" onClick={() => void runAll()} disabled={!session || session.busy || !nextStep}>
          <Play size={16} />
          Run Remaining
        </button>
        <button type="button" onClick={resetSession} disabled={session?.busy}>
          <RotateCcw size={16} />
          Reset View
        </button>
      </section>

      {error && <div className="error-banner">{error}</div>}

      <div className="workspace-grid">
        <ParameterPanel definition={definition} config={config} disabled={Boolean(session?.busy)} onChange={setConfig} />
        <div className="middle-column">
          <StepList
            definitions={definition.steps}
            steps={session?.steps ?? definition.steps.map((step) => ({ id: step.id, title: step.title, status: 'pending', metrics: {} }))}
            selectedStepId={selectedStepId}
            busy={Boolean(session?.busy)}
            onSelect={setSelectedStepId}
            onRunStep={(stepId) => void runStep(stepId)}
          />
          <StepDetails definition={selectedDefinition} state={selectedState} />
        </div>
        <div className="right-column">
          <ArtifactPanel artifacts={session?.artifacts ?? []} />
          <LogPanel logs={session?.logs ?? []} />
        </div>
      </div>
    </main>
  );
}

function prepareConfig(config: WorkflowConfig): WorkflowConfig {
  return {
    ...config,
    output_name: config.output_name?.trim() ? config.output_name.trim() : null,
    output_dir: config.output_dir.trim() || 'outputs',
    image_path: config.image_path.trim() || defaultConfig.image_path,
    model_id: config.model_id.trim() || defaultConfig.model_id,
    sampler_steps: config.sampler_steps && config.sampler_steps > 0 ? config.sampler_steps : null,
    num_samples: Math.max(1, config.num_samples || 1),
    max_num_tokens: Math.max(1024, config.max_num_tokens || defaultConfig.max_num_tokens),
    decimation_target: Math.max(10000, config.decimation_target || defaultConfig.decimation_target)
  };
}
